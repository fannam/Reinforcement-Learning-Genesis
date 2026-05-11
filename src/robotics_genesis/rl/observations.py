from __future__ import annotations

from math import sqrt
from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np


OBSERVATION_SCHEMA_VERSION = "multimodal_depth_v1"
STATE_OBSERVATION_SIZE = 28
OBSERVATION_SIZE = STATE_OBSERVATION_SIZE
DEPTH_IMAGE_SHAPE = (1, 64, 64)
POSITION_SCALE = np.array([22.0, 14.0, 7.0], dtype=np.float32)
GOAL_VECTOR_SCALE = np.array([44.0, 28.0, 7.0], dtype=np.float32)
LINEAR_VELOCITY_SCALE = 5.0
LINEAR_ACCELERATION_SCALE = 20.0
ANGULAR_VELOCITY_SCALE = 10.0
MAX_WAREHOUSE_DISTANCE = float(sqrt(44.0**2 + 28.0**2 + 7.0**2))


@dataclass(frozen=True)
class DroneState:
    pos: np.ndarray
    vel: np.ndarray
    quat_wxyz: np.ndarray
    ang_vel: np.ndarray


def as_float3(value: Sequence[float]) -> np.ndarray:
    return np.asarray(value, dtype=np.float32).reshape(3)


def as_quat_wxyz(value: Sequence[float]) -> np.ndarray:
    return np.asarray(value, dtype=np.float32).reshape(4)


def normalize_depth_image(
    depth_image: np.ndarray | Sequence[float],
    *,
    far: float,
    shape: tuple[int, int, int] = DEPTH_IMAGE_SHAPE,
) -> np.ndarray:
    if far <= 0.0:
        raise ValueError("Depth camera far plane must be positive.")

    depth = np.asarray(depth_image, dtype=np.float32)
    expected_c, expected_h, expected_w = shape
    if expected_c != 1:
        raise ValueError("Depth observation currently supports exactly one channel.")
    if depth.shape == (expected_h, expected_w):
        depth = depth.reshape(shape)
    elif depth.shape == (expected_h, expected_w, 1):
        depth = np.moveaxis(depth, -1, 0)
    elif depth.shape != shape:
        raise ValueError(f"Depth image has shape {depth.shape}, expected {(expected_h, expected_w)} or {shape}.")

    depth = np.nan_to_num(depth, nan=far, posinf=far, neginf=far)
    return np.clip(depth, 0.0, far).astype(np.float32) / np.float32(far)


def build_state_observation(
    state: DroneState,
    *,
    goal: Sequence[float],
    previous_action: Sequence[float],
    contact_flag: bool,
    linear_acceleration: Sequence[float],
    hover_wrench: Sequence[float],
) -> np.ndarray:
    goal_arr = as_float3(goal)
    action_arr = np.asarray(previous_action, dtype=np.float32).reshape(3)
    acceleration_arr = as_float3(linear_acceleration)
    wrench_arr = np.asarray(hover_wrench, dtype=np.float32).reshape(4)
    goal_vector = goal_arr - state.pos
    distance = np.float32(np.linalg.norm(goal_vector))

    state_obs = np.concatenate(
        [
            state.pos / POSITION_SCALE,
            state.vel / LINEAR_VELOCITY_SCALE,
            state.quat_wxyz,
            state.ang_vel / ANGULAR_VELOCITY_SCALE,
            acceleration_arr / LINEAR_ACCELERATION_SCALE,
            goal_vector / GOAL_VECTOR_SCALE,
            np.array([distance / MAX_WAREHOUSE_DISTANCE], dtype=np.float32),
            action_arr,
            wrench_arr,
            np.array([1.0 if contact_flag else 0.0], dtype=np.float32),
        ]
    ).astype(np.float32)

    if state_obs.shape != (STATE_OBSERVATION_SIZE,):
        raise ValueError(f"State observation has shape {state_obs.shape}, expected {(STATE_OBSERVATION_SIZE,)}.")
    return state_obs


def build_observation(
    state: DroneState,
    *,
    goal: Sequence[float],
    previous_action: Sequence[float],
    contact_flag: bool,
    linear_acceleration: Sequence[float],
    hover_wrench: Sequence[float],
    depth_image: np.ndarray | Sequence[float],
    depth_far: float,
    depth_shape: tuple[int, int, int] = DEPTH_IMAGE_SHAPE,
) -> dict[str, np.ndarray]:
    return {
        "state": build_state_observation(
            state,
            goal=goal,
            previous_action=previous_action,
            contact_flag=contact_flag,
            linear_acceleration=linear_acceleration,
            hover_wrench=hover_wrench,
        ),
        "depth": normalize_depth_image(depth_image, far=depth_far, shape=depth_shape),
    }


def observation_shape_from_space(observation_space) -> dict[str, tuple[int, ...]]:
    spaces = getattr(observation_space, "spaces", None)
    if not isinstance(spaces, Mapping):
        raise TypeError("Observation space must be a gymnasium.spaces.Dict.")
    return {key: tuple(int(dim) for dim in space.shape) for key, space in spaces.items()}
