from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


Vector3 = tuple[float, float, float]


@dataclass(frozen=True)
class Scenario:
    spawn: Vector3
    goal: Vector3


@dataclass(frozen=True)
class ScenarioConfig:
    spawn_x: tuple[float, float] = (-3.0, 2.0)
    spawn_y: tuple[float, float] = (-2.5, 2.5)
    spawn_z: tuple[float, float] = (1.8, 2.6)
    goal_x: tuple[float, float] = (-4.0, 4.0)
    goal_y: tuple[float, float] = (-3.0, 3.0)
    goal_z: tuple[float, float] = (1.8, 2.8)
    min_goal_distance: float = 1.0
    max_attempts: int = 100
    deterministic_spawn: Vector3 = (-2.0, -2.0, 2.0)
    deterministic_goal: Vector3 = (-1.0, -1.5, 2.0)


def _uniform3(
    rng: np.random.Generator,
    ranges: tuple[tuple[float, float], tuple[float, float], tuple[float, float]],
) -> Vector3:
    return tuple(float(rng.uniform(low, high)) for low, high in ranges)


def _distance(a: Sequence[float], b: Sequence[float]) -> float:
    return float(np.linalg.norm(np.asarray(a, dtype=np.float32) - np.asarray(b, dtype=np.float32)))


def sample_spawn_goal(
    rng: np.random.Generator,
    config: ScenarioConfig = ScenarioConfig(),
    *,
    randomize: bool = True,
) -> Scenario:
    if not randomize:
        return Scenario(config.deterministic_spawn, config.deterministic_goal)

    spawn_ranges = (config.spawn_x, config.spawn_y, config.spawn_z)
    goal_ranges = (config.goal_x, config.goal_y, config.goal_z)
    last_spawn = config.deterministic_spawn
    last_goal = config.deterministic_goal

    for _ in range(config.max_attempts):
        spawn = _uniform3(rng, spawn_ranges)
        goal = _uniform3(rng, goal_ranges)
        last_spawn, last_goal = spawn, goal
        if _distance(spawn, goal) >= config.min_goal_distance:
            return Scenario(spawn, goal)

    return Scenario(last_spawn, last_goal)
