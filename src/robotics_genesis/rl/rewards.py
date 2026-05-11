from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


WAREHOUSE_LOW = np.array([-22.0, -14.0, 0.05], dtype=np.float32)
WAREHOUSE_HIGH = np.array([22.0, 14.0, 7.0], dtype=np.float32)


@dataclass(frozen=True)
class RewardConfig:
    progress_weight: float = 8.0
    distance_weight: float = 0.02
    action_weight: float = 0.01
    tilt_weight: float = 0.02
    contact_penalty: float = 20.0
    bounds_penalty: float = 20.0
    success_bonus: float = 50.0


def is_out_of_bounds(
    pos: Sequence[float],
    *,
    low: Sequence[float] = WAREHOUSE_LOW,
    high: Sequence[float] = WAREHOUSE_HIGH,
) -> bool:
    pos_arr = np.asarray(pos, dtype=np.float32)
    return bool(np.any(pos_arr < np.asarray(low, dtype=np.float32)) or np.any(pos_arr > np.asarray(high, dtype=np.float32)))


def tilt_penalty(quat_wxyz: Sequence[float]) -> float:
    quat = np.asarray(quat_wxyz, dtype=np.float32).reshape(4)
    norm = float(np.linalg.norm(quat))
    if norm == 0.0:
        return 1.0
    w, x, y, z = quat / norm
    body_z_world_z = 1.0 - 2.0 * (x * x + y * y)
    return float(max(0.0, 1.0 - body_z_world_z))


def compute_reward(
    *,
    previous_distance: float,
    current_distance: float,
    action: Sequence[float],
    quat_wxyz: Sequence[float],
    contact: bool,
    out_of_bounds: bool,
    success: bool,
    config: RewardConfig = RewardConfig(),
) -> float:
    action_arr = np.asarray(action, dtype=np.float32).reshape(3)
    progress = float(previous_distance - current_distance)
    reward = (
        config.progress_weight * progress
        - config.distance_weight * float(current_distance)
        - config.action_weight * float(np.dot(action_arr, action_arr))
        - config.tilt_weight * tilt_penalty(quat_wxyz)
    )
    if contact:
        reward -= config.contact_penalty
    if out_of_bounds:
        reward -= config.bounds_penalty
    if success:
        reward += config.success_bonus
    return float(reward)
