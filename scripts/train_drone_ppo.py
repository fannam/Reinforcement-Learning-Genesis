#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
import shutil
import sys
from dataclasses import fields, replace
from pathlib import Path

import numpy as np
import torch
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from robotics_genesis.paths import project_path
from robotics_genesis.rl.observations import observation_shape_from_space
from robotics_genesis.rl.policy import ActorCritic, PolicyConfig
from robotics_genesis.rl.ppo import PPOConfig, save_checkpoint, train_ppo
from robotics_genesis.rl.rewards import RewardConfig
from robotics_genesis.rl.scenarios import ScenarioConfig
from robotics_genesis.rl.warehouse_env import DepthCameraConfig, WarehouseDroneEnv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a custom PyTorch PPO policy for single-drone navigation.")
    parser.add_argument("--config", default="configs/rl/single_drone_ppo.yaml", help="RL YAML config path.")
    parser.add_argument("--total-timesteps", type=int, default=None, help="Override PPO total timesteps.")
    parser.add_argument("--rollout-steps", type=int, default=None, help="Override rollout size per PPO update.")
    parser.add_argument("--batch-size", type=int, default=None, help="Override PPO minibatch size.")
    parser.add_argument("--update-epochs", type=int, default=None, help="Override PPO epochs per update.")
    parser.add_argument("--backend", choices=("cpu", "gpu"), default=None, help="Override Genesis backend.")
    parser.add_argument("--device", default=None, help="Override PyTorch device, e.g. cpu or cuda.")
    parser.add_argument("--run-name", default="ppo_single_drone_v1", help="Output run name.")
    parser.add_argument("--seed", type=int, default=0, help="Training seed.")
    return parser.parse_args()


def load_config(path: str | Path) -> dict:
    config_path = Path(path)
    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _to_tuple_config(config: dict) -> dict:
    converted = dict(config)
    for key, value in list(converted.items()):
        if isinstance(value, list):
            converted[key] = tuple(value)
    return converted


def _filter_dataclass_config(config: dict, cls) -> dict:
    allowed = {field.name for field in fields(cls)}
    return {key: value for key, value in config.items() if key in allowed}


def build_env(config: dict, *, backend_override: str | None = None) -> WarehouseDroneEnv:
    env_config = dict(config.get("env", {}))
    observation_config = dict(config.get("observation", {}))
    depth_camera_config = DepthCameraConfig(**_to_tuple_config(observation_config.get("depth_camera", {})))
    reward_config = RewardConfig(**dict(config.get("reward", {})))
    scenario_config = ScenarioConfig(**_to_tuple_config(config.get("scenario", {})))
    if backend_override is not None:
        env_config["backend"] = backend_override
    return WarehouseDroneEnv(
        **env_config,
        reward_config=reward_config,
        scenario_config=scenario_config,
        depth_camera_config=depth_camera_config,
    )


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    ppo_raw_config = dict(config.get("ppo", {}))
    policy_config = PolicyConfig(**_to_tuple_config(config.get("policy", {})))
    ppo_config = PPOConfig(**_filter_dataclass_config(ppo_raw_config, PPOConfig))
    if args.total_timesteps is not None:
        ppo_config = replace(ppo_config, total_timesteps=args.total_timesteps)
    if args.rollout_steps is not None:
        ppo_config = replace(ppo_config, rollout_steps=args.rollout_steps)
    if args.batch_size is not None:
        ppo_config = replace(ppo_config, batch_size=args.batch_size)
    if args.update_epochs is not None:
        ppo_config = replace(ppo_config, update_epochs=args.update_epochs)
    if args.device is not None:
        ppo_config = replace(ppo_config, device=args.device)

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    checkpoint_dir = project_path("outputs", "checkpoints", args.run_name)
    log_dir = project_path("outputs", "logs", args.run_name)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    source_config = Path(args.config)
    if not source_config.is_absolute():
        source_config = PROJECT_ROOT / source_config
    shutil.copy2(source_config, log_dir / "train_config.yaml")

    env = build_env(config, backend_override=args.backend)
    try:
        obs_shape = observation_shape_from_space(env.observation_space)
        action_dim = int(env.action_space.shape[0])
        model = ActorCritic(obs_shape, action_dim, policy_config)
        train_ppo(
            env,
            model,
            ppo_config,
            seed=args.seed,
            log_csv=log_dir / "training_metrics.csv",
        )
        final_path = checkpoint_dir / "final.pt"
        save_checkpoint(
            final_path,
            model=model,
            policy_config=policy_config,
            ppo_config=ppo_config,
            obs_shape=obs_shape,
            action_dim=action_dim,
            extra={"run_name": args.run_name, "seed": args.seed},
        )
        print(f"Saved final model to {final_path}")
    finally:
        env.close()


if __name__ == "__main__":
    main()
