"""Reinforcement learning environments and helpers."""

from robotics_genesis.rl.rewards import RewardConfig, compute_reward, is_out_of_bounds
from robotics_genesis.rl.scenarios import Scenario, ScenarioConfig, sample_spawn_goal

__all__ = [
    "RewardConfig",
    "Scenario",
    "ScenarioConfig",
    "DepthCameraConfig",
    "WarehouseDroneEnv",
    "compute_reward",
    "is_out_of_bounds",
    "sample_spawn_goal",
]


def __getattr__(name: str):
    if name == "WarehouseDroneEnv":
        from robotics_genesis.rl.warehouse_env import WarehouseDroneEnv

        return WarehouseDroneEnv
    if name == "DepthCameraConfig":
        from robotics_genesis.rl.warehouse_env import DepthCameraConfig

        return DepthCameraConfig
    raise AttributeError(name)
