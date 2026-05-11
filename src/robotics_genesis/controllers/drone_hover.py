"""Hover controller for the quadcopter MJCF in `robots/drone/drone.xml`.

Genesis ignores MJCF site-based actuators (it only parses joint/tendon
transmissions). We apply a body-frame wrench (force + torque) on the chassis
link via the rigid solver: `solver.apply_links_external_force` and
`apply_links_external_torque` with `local=True`.

Per-rotor force application proved unstable due to numerical drift when applying
forces at off-center link origins under fixed-joint child links. The body
wrench formulation is mathematically equivalent for a rigid frame and avoids
that issue.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.spatial.transform import Rotation


CHASSIS_LINK_NAME: str = "drone_core"


@dataclass
class HoverConfig:
    mass: float = 0.81
    gravity: float = 9.81
    kp_z: float = 8.0
    kv_z: float = 4.0
    kp_att: float = 0.4
    kv_att: float = 0.08
    kp_yaw: float = 0.2
    kv_yaw: float = 0.05
    kp_xy: float = 1.0
    kv_xy: float = 1.5
    max_tilt_deg: float = 15.0
    fz_max_factor: float = 4.0
    tau_max: float = 1.0
    chassis_link_name: str = CHASSIS_LINK_NAME


class HoverController:
    """PD hover controller for a free-body quadcopter `RigidEntity`.

    Applies body-frame force `(0, 0, Fz_total)` and body-frame torque
    `(tau_roll, tau_pitch, tau_yaw)` on the chassis link each step.
    """

    def __init__(
        self,
        entity,
        config: HoverConfig | None = None,
        target_pos: Sequence[float] = (0.0, 0.0, 1.0),
        target_yaw: float = 0.0,
    ) -> None:
        self.entity = entity
        self.solver = entity.solver
        self.config = config or HoverConfig()
        self.target_pos = np.asarray(target_pos, dtype=np.float32)
        self.target_yaw = float(target_yaw)

        self.chassis_idx = entity.get_link(self.config.chassis_link_name).idx
        self.fz_max = self.config.fz_max_factor * self.config.mass * self.config.gravity

    def set_target_pos(self, target_pos: Sequence[float]) -> None:
        self.target_pos = np.asarray(target_pos, dtype=np.float32)

    @staticmethod
    def _to_numpy(value) -> np.ndarray:
        try:
            return value.detach().cpu().numpy()
        except AttributeError:
            return np.asarray(value)

    def compute_wrench(
        self,
        pos: np.ndarray,
        quat_wxyz: np.ndarray,
        lin_vel: np.ndarray,
        ang_vel_world: np.ndarray,
    ) -> tuple[float, np.ndarray]:
        cfg = self.config

        rot = Rotation.from_quat([quat_wxyz[1], quat_wxyz[2], quat_wxyz[3], quat_wxyz[0]])
        roll, pitch, yaw = rot.as_euler("xyz", degrees=False)
        ang_body = rot.inv().apply(ang_vel_world)
        p_body, q_body, r_body = ang_body
        cos_tilt = float(max(0.5, rot.as_matrix()[2, 2]))

        x_target, y_target, z_target = (float(v) for v in self.target_pos)

        ax_w = cfg.kp_xy * (x_target - pos[0]) + cfg.kv_xy * (-lin_vel[0])
        ay_w = cfg.kp_xy * (y_target - pos[1]) + cfg.kv_xy * (-lin_vel[1])
        cy, sy = np.cos(yaw), np.sin(yaw)
        ax_b =  cy * ax_w + sy * ay_w
        ay_b = -sy * ax_w + cy * ay_w

        max_tilt_rad = np.deg2rad(cfg.max_tilt_deg)
        desired_pitch = float(np.clip( ax_b / cfg.gravity, -max_tilt_rad, max_tilt_rad))
        desired_roll  = float(np.clip(-ay_b / cfg.gravity, -max_tilt_rad, max_tilt_rad))

        fz_total = (
            cfg.mass * cfg.gravity
            + cfg.kp_z * (z_target - pos[2])
            + cfg.kv_z * (-lin_vel[2])
        ) / cos_tilt
        fz_total = float(np.clip(fz_total, 0.0, self.fz_max))

        tau = np.array([
            cfg.kp_att * (desired_roll  - roll)  + cfg.kv_att * (-p_body),
            cfg.kp_att * (desired_pitch - pitch) + cfg.kv_att * (-q_body),
            cfg.kp_yaw * (self.target_yaw - yaw) + cfg.kv_yaw * (-r_body),
        ], dtype=np.float32)
        tau = np.clip(tau, -cfg.tau_max, cfg.tau_max)
        return fz_total, tau

    def step(self) -> dict:
        pos = self._to_numpy(self.entity.get_pos())
        quat = self._to_numpy(self.entity.get_quat())
        lin_vel = self._to_numpy(self.entity.get_vel())
        ang_vel = self._to_numpy(self.entity.get_ang())

        fz, tau = self.compute_wrench(pos, quat, lin_vel, ang_vel)

        force = np.array([[0.0, 0.0, fz]], dtype=np.float32)
        torque = tau.reshape(1, 3).astype(np.float32)
        self.solver.apply_links_external_force(
            force, links_idx=[self.chassis_idx], ref="link_origin", local=True,
        )
        self.solver.apply_links_external_torque(
            torque, links_idx=[self.chassis_idx], ref="link_origin", local=True,
        )

        return {"pos": pos, "fz": fz, "tau": tau}
