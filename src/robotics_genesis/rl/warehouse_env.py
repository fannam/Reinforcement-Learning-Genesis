from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from gymnasium import Env, spaces

from robotics_genesis.controllers import HoverConfig, HoverController
from robotics_genesis.paths import PROJECT_ROOT, project_path
from robotics_genesis.rl.observations import DEPTH_IMAGE_SHAPE, STATE_OBSERVATION_SIZE, DroneState, as_float3, as_quat_wxyz, build_observation
from robotics_genesis.rl.rewards import RewardConfig, compute_reward, is_out_of_bounds
from robotics_genesis.rl.scenarios import Scenario, ScenarioConfig, sample_spawn_goal
from robotics_genesis.viewer_env import configure_pyglet_options, configure_viewer_environment
from robotics_genesis.xml_robot import prepare_mjcf_for_genesis


ACTION_SCALE = np.array([0.75, 0.75, 0.35], dtype=np.float32)
TARGET_LOW = np.array([-21.5, -13.5, 0.75], dtype=np.float32)
TARGET_HIGH = np.array([21.5, 13.5, 5.25], dtype=np.float32)
IDENTITY_QUAT_WXYZ = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
PHYSICS_TIMESTEP = 0.005
CAMERA_FORWARD_BODY = np.array([1.0, 0.0, 0.0], dtype=np.float32)
CAMERA_UP_BODY = np.array([0.0, 0.0, 1.0], dtype=np.float32)


def _strip_world_decorations(src: Path, dst: Path) -> Path:
    tree = ET.parse(src)
    root = tree.getroot()
    worldbody = root.find("worldbody")
    if worldbody is not None:
        for child in list(worldbody):
            if child.tag == "light":
                worldbody.remove(child)
            elif child.tag == "geom" and child.attrib.get("name") == "floor":
                worldbody.remove(child)
    dst.parent.mkdir(parents=True, exist_ok=True)
    tree.write(dst, encoding="utf-8", xml_declaration=False)
    return dst


def _cuda_available() -> bool:
    try:
        import torch
    except ImportError:
        return False
    return torch.cuda.is_available()


def _select_backend(gs, name: str):
    normalized = name.strip().lower()
    if normalized in ("gpu", "cuda"):
        return gs.gpu if _cuda_available() else gs.cpu
    if normalized == "cpu":
        return gs.cpu
    raise ValueError("backend must be 'cpu' or 'gpu'")


def _to_numpy(value) -> np.ndarray:
    try:
        return value.detach().cpu().numpy()
    except AttributeError:
        return np.asarray(value)


def _count_valid_contacts(contact_data: dict[str, Any]) -> int:
    valid_mask = contact_data.get("valid_mask")
    if valid_mask is None:
        return 0
    return int(_to_numpy(valid_mask).sum())


def _quat_wxyz_to_matrix(quat_wxyz: Sequence[float]) -> np.ndarray:
    quat = np.asarray(quat_wxyz, dtype=np.float32).reshape(4)
    norm = float(np.linalg.norm(quat))
    if norm == 0.0:
        return np.eye(3, dtype=np.float32)
    w, x, y, z = quat / norm
    return np.array(
        [
            [1.0 - 2.0 * (y * y + z * z), 2.0 * (x * y - z * w), 2.0 * (x * z + y * w)],
            [2.0 * (x * y + z * w), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - x * w)],
            [2.0 * (x * z - y * w), 2.0 * (y * z + x * w), 1.0 - 2.0 * (x * x + y * y)],
        ],
        dtype=np.float32,
    )


@dataclass(frozen=True)
class DepthCameraConfig:
    width: int = DEPTH_IMAGE_SHAPE[2]
    height: int = DEPTH_IMAGE_SHAPE[1]
    fov: float = 90.0
    near: float = 0.1
    far: float = 8.0
    offset: tuple[float, float, float] = (0.08, 0.0, 0.02)

    def __post_init__(self) -> None:
        if self.width < 1 or self.height < 1:
            raise ValueError("Depth camera width and height must be positive.")
        if self.fov <= 0.0:
            raise ValueError("Depth camera fov must be positive.")
        if self.near <= 0.0:
            raise ValueError("Depth camera near plane must be positive.")
        if self.far <= self.near:
            raise ValueError("Depth camera far plane must be greater than near plane.")
        if len(self.offset) != 3:
            raise ValueError("Depth camera offset must contain three values.")
        object.__setattr__(self, "width", int(self.width))
        object.__setattr__(self, "height", int(self.height))
        object.__setattr__(self, "offset", tuple(float(v) for v in self.offset))

    @property
    def shape(self) -> tuple[int, int, int]:
        return (1, self.height, self.width)


class WarehouseDroneEnv(Env):
    """Gymnasium environment for one stabilized drone in the warehouse."""

    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(
        self,
        world_xml: str | Path = "worlds/warehouse.xml",
        drone_xml: str | Path = "robots/drone/drone.xml",
        *,
        backend: str = "cpu",
        episode_steps: int = 1000,
        control_skip: int = 4,
        action_mode: str = "target_delta",
        seed: int | None = None,
        randomize: bool = True,
        show_viewer: bool = False,
        success_radius: float = 0.35,
        success_dwell_steps: int = 20,
        reward_config: RewardConfig | None = None,
        scenario_config: ScenarioConfig | None = None,
        depth_camera_config: DepthCameraConfig | None = None,
    ) -> None:
        super().__init__()
        if action_mode != "target_delta":
            raise ValueError("Only action_mode='target_delta' is supported in v1.")
        if episode_steps < 1:
            raise ValueError("episode_steps must be at least 1.")
        if control_skip < 1:
            raise ValueError("control_skip must be at least 1.")
        if success_radius <= 0:
            raise ValueError("success_radius must be positive.")
        if success_dwell_steps < 1:
            raise ValueError("success_dwell_steps must be at least 1.")

        self.world_xml = self._resolve_path(world_xml)
        self.drone_xml = self._resolve_path(drone_xml)
        self.backend = backend
        self.episode_steps = int(episode_steps)
        self.control_skip = int(control_skip)
        self.randomize = bool(randomize)
        self.show_viewer = bool(show_viewer)
        self.success_radius = float(success_radius)
        self.success_dwell_steps = int(success_dwell_steps)
        self.reward_config = reward_config or RewardConfig()
        self.scenario_config = scenario_config or ScenarioConfig()
        self.depth_camera_config = depth_camera_config or DepthCameraConfig()

        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(3,), dtype=np.float32)
        self.observation_space = spaces.Dict(
            {
                "state": spaces.Box(
                    low=-np.inf,
                    high=np.inf,
                    shape=(STATE_OBSERVATION_SIZE,),
                    dtype=np.float32,
                ),
                "depth": spaces.Box(
                    low=0.0,
                    high=1.0,
                    shape=self.depth_camera_config.shape,
                    dtype=np.float32,
                ),
            }
        )

        self._scene = None
        self._warehouse_entity = None
        self._drone_entity = None
        self._depth_camera = None
        self._controller: HoverController | None = None
        self._owns_genesis = False
        self._episode_step = 0
        self._success_dwell = 0
        self._previous_action = np.zeros(3, dtype=np.float32)
        self._previous_velocity = np.zeros(3, dtype=np.float32)
        self._linear_acceleration = np.zeros(3, dtype=np.float32)
        self._last_hover_wrench = np.zeros(4, dtype=np.float32)
        self._previous_distance = 0.0
        self._scenario = Scenario(self.scenario_config.deterministic_spawn, self.scenario_config.deterministic_goal)
        self._contact_flag = False
        self._last_contacts = 0
        self._target_pos = np.asarray(self._scenario.spawn, dtype=np.float32)

        if seed is not None:
            self.reset(seed=seed)

    @staticmethod
    def _resolve_path(path: str | Path) -> Path:
        value = Path(path)
        return value if value.is_absolute() else PROJECT_ROOT / value

    def _ensure_scene(self) -> None:
        if self._scene is not None:
            return

        configure_viewer_environment(self.show_viewer)
        if self.show_viewer:
            import pyglet
            configure_pyglet_options(pyglet)

        import genesis as gs

        if not getattr(gs, "_initialized", False):
            gs.init(backend=_select_backend(gs, self.backend))
            self._owns_genesis = True

        world_genesis = prepare_mjcf_for_genesis(self.world_xml, project_path("outputs", "generated"))
        drone_prepared = prepare_mjcf_for_genesis(self.drone_xml, project_path("outputs", "generated"))
        drone_genesis = _strip_world_decorations(
            drone_prepared,
            project_path("outputs", "generated") / f"{drone_prepared.stem}.rl_scene_ready.xml",
        )

        viewer_options = None
        if self.show_viewer:
            run_in_thread = os.getenv("GENESIS_VIEWER_THREAD", "0") != "0"
            viewer_options = gs.options.ViewerOptions(
                run_in_thread=run_in_thread,
                res=(1280, 800),
                camera_pos=(-3.5, -3.5, 2.5),
                camera_lookat=(0.0, 0.0, 0.0),
                camera_fov=50,
            )

        self._scene = gs.Scene(
            show_viewer=self.show_viewer,
            viewer_options=viewer_options,
            rigid_options=gs.options.RigidOptions(enable_self_collision=False),
        )
        self._warehouse_entity = self._scene.add_entity(
            gs.morphs.MJCF(file=str(world_genesis)),
            material=gs.materials.Rigid(sdf_cell_size=0.05, sdf_max_res=32),
        )
        self._drone_entity = self._scene.add_entity(gs.morphs.MJCF(file=str(drone_genesis), pos=(0.0, 0.0, 2.0)))
        self._depth_camera = self._scene.add_camera(
            model="pinhole",
            res=(self.depth_camera_config.width, self.depth_camera_config.height),
            pos=(0.0, 0.0, 2.0),
            lookat=(1.0, 0.0, 2.0),
            up=(0.0, 0.0, 1.0),
            fov=self.depth_camera_config.fov,
            near=self.depth_camera_config.near,
            far=self.depth_camera_config.far,
            GUI=False,
        )
        self._scene.build()

    def _get_state(self) -> DroneState:
        if self._drone_entity is None:
            raise RuntimeError("Scene has not been built.")
        return DroneState(
            pos=as_float3(_to_numpy(self._drone_entity.get_pos())),
            vel=as_float3(_to_numpy(self._drone_entity.get_vel())),
            quat_wxyz=as_quat_wxyz(_to_numpy(self._drone_entity.get_quat())),
            ang_vel=as_float3(_to_numpy(self._drone_entity.get_ang())),
        )

    def _render_depth_observation(self, state: DroneState) -> np.ndarray:
        if self._depth_camera is None:
            raise RuntimeError("Depth camera has not been built.")

        rot = _quat_wxyz_to_matrix(state.quat_wxyz)
        camera_pos = state.pos + rot @ np.asarray(self.depth_camera_config.offset, dtype=np.float32)
        lookat = camera_pos + rot @ CAMERA_FORWARD_BODY
        up = rot @ CAMERA_UP_BODY
        self._depth_camera.set_pose(pos=camera_pos, lookat=lookat, up=up)
        _, depth, _, _ = self._depth_camera.render(rgb=False, depth=True)
        if depth is None:
            raise RuntimeError("Genesis camera did not return a depth image.")
        return _to_numpy(depth)

    def _observe(self) -> dict[str, np.ndarray]:
        state = self._get_state()
        return build_observation(
            state,
            goal=self._scenario.goal,
            previous_action=self._previous_action,
            contact_flag=self._contact_flag,
            linear_acceleration=self._linear_acceleration,
            hover_wrench=self._last_hover_wrench,
            depth_image=self._render_depth_observation(state),
            depth_far=self.depth_camera_config.far,
            depth_shape=self.depth_camera_config.shape,
        )

    def _normalize_hover_wrench(self, controller_info: dict[str, Any] | None) -> np.ndarray:
        if controller_info is None or self._controller is None:
            return np.zeros(4, dtype=np.float32)

        fz = float(controller_info.get("fz", 0.0))
        tau = np.asarray(controller_info.get("tau", np.zeros(3, dtype=np.float32)), dtype=np.float32).reshape(3)
        fz_scale = max(float(self._controller.fz_max), 1e-6)
        tau_scale = max(float(self._controller.config.tau_max), 1e-6)
        wrench = np.array([fz / fz_scale, tau[0] / tau_scale, tau[1] / tau_scale, tau[2] / tau_scale], dtype=np.float32)
        return np.clip(wrench, -1.0, 1.0).astype(np.float32)

    def _set_drone_pose(self, pos: Sequence[float]) -> None:
        if self._drone_entity is None:
            raise RuntimeError("Scene has not been built.")
        self._drone_entity.set_pos(pos, zero_velocity=True)
        self._drone_entity.set_quat(IDENTITY_QUAT_WXYZ, zero_velocity=True)

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        super().reset(seed=seed)
        self._ensure_scene()
        if self._scene is None:
            raise RuntimeError("Scene build failed.")

        self._scene.reset()
        self._scenario = sample_spawn_goal(self.np_random, self.scenario_config, randomize=self.randomize)
        if options:
            if "spawn" in options or "goal" in options:
                self._scenario = Scenario(
                    tuple(float(v) for v in options.get("spawn", self._scenario.spawn)),
                    tuple(float(v) for v in options.get("goal", self._scenario.goal)),
                )

        self._set_drone_pose(self._scenario.spawn)
        self._target_pos = np.asarray(self._scenario.spawn, dtype=np.float32)
        self._controller = HoverController(self._drone_entity, HoverConfig(), target_pos=self._target_pos)
        self._episode_step = 0
        self._success_dwell = 0
        self._previous_action = np.zeros(3, dtype=np.float32)
        self._linear_acceleration = np.zeros(3, dtype=np.float32)
        self._last_hover_wrench = np.zeros(4, dtype=np.float32)
        self._contact_flag = False
        self._last_contacts = 0
        state = self._get_state()
        self._previous_velocity = state.vel.copy()
        self._previous_distance = float(np.linalg.norm(np.asarray(self._scenario.goal, dtype=np.float32) - state.pos))

        return self._observe(), self._info(state, success=False, out_of_bounds=False)

    def step(self, action):
        if self._controller is None:
            raise RuntimeError("Call reset() before step().")

        action_arr = np.clip(np.asarray(action, dtype=np.float32).reshape(3), -1.0, 1.0)
        current_state = self._get_state()
        self._target_pos = np.clip(current_state.pos + action_arr * ACTION_SCALE, TARGET_LOW, TARGET_HIGH)
        self._controller.set_target_pos(self._target_pos)

        controller_info = None
        for _ in range(self.control_skip):
            controller_info = self._controller.step()
            self._scene.step()

        self._episode_step += 1
        state = self._get_state()
        control_dt = PHYSICS_TIMESTEP * float(self.control_skip)
        self._linear_acceleration = ((state.vel - current_state.vel) / control_dt).astype(np.float32)
        self._previous_velocity = state.vel.copy()
        self._last_hover_wrench = self._normalize_hover_wrench(controller_info)
        self._last_contacts = _count_valid_contacts(self._drone_entity.get_contacts(with_entity=self._warehouse_entity))
        self._contact_flag = self._last_contacts > 0
        out_of_bounds = is_out_of_bounds(state.pos)

        current_distance = float(np.linalg.norm(np.asarray(self._scenario.goal, dtype=np.float32) - state.pos))
        if current_distance <= self.success_radius:
            self._success_dwell += 1
        else:
            self._success_dwell = 0
        success = self._success_dwell >= self.success_dwell_steps

        reward = compute_reward(
            previous_distance=self._previous_distance,
            current_distance=current_distance,
            action=action_arr,
            quat_wxyz=state.quat_wxyz,
            contact=self._contact_flag,
            out_of_bounds=out_of_bounds,
            success=success,
            config=self.reward_config,
        )
        self._previous_distance = current_distance
        self._previous_action = action_arr

        terminated = bool(success or self._contact_flag or out_of_bounds)
        truncated = bool(self._episode_step >= self.episode_steps and not terminated)
        return self._observe(), reward, terminated, truncated, self._info(state, success=success, out_of_bounds=out_of_bounds)

    def _info(self, state: DroneState, *, success: bool, out_of_bounds: bool) -> dict[str, Any]:
        distance = float(np.linalg.norm(np.asarray(self._scenario.goal, dtype=np.float32) - state.pos))
        return {
            "distance_to_goal": distance,
            "success": bool(success),
            "collision": bool(self._contact_flag),
            "out_of_bounds": bool(out_of_bounds),
            "episode_step": self._episode_step,
            "contacts": self._last_contacts,
            "goal": self._scenario.goal,
            "spawn": self._scenario.spawn,
            "target_pos": tuple(float(v) for v in self._target_pos),
        }

    def render(self):
        return None

    def close(self) -> None:
        if self._owns_genesis:
            import genesis as gs

            gs.destroy()
        self._scene = None
        self._warehouse_entity = None
        self._drone_entity = None
        self._depth_camera = None
        self._controller = None
        self._owns_genesis = False
