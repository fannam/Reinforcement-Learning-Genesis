#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import torch
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from robotics_genesis.paths import project_path
from robotics_genesis.rl.ppo import load_checkpoint, observation_to_tensor
from robotics_genesis.rl.rewards import RewardConfig
from robotics_genesis.rl.scenarios import ScenarioConfig
from robotics_genesis.rl.warehouse_env import DepthCameraConfig, WarehouseDroneEnv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a custom PyTorch drone policy.")
    parser.add_argument("--model", required=True, help="Path to a saved .pt checkpoint.")
    parser.add_argument("--config", default="configs/rl/single_drone_ppo.yaml", help="RL YAML config path.")
    parser.add_argument("--episodes", type=int, default=20)
    parser.add_argument("--backend", choices=("cpu", "gpu"), default=None)
    parser.add_argument("--device", default="cpu", help="PyTorch device for policy inference.")
    parser.add_argument("--viewer", action="store_true", help="Show Genesis viewer during evaluation.")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--csv", default=None, help="Optional CSV summary path.")
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


def build_env(config: dict, *, backend_override: str | None = None, show_viewer: bool = False) -> WarehouseDroneEnv:
    env_config = dict(config.get("env", {}))
    env_config["show_viewer"] = show_viewer
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


def resolve_csv(path: str | None, model_path: Path) -> Path:
    if path is None:
        return project_path("outputs", "logs", f"eval_{model_path.stem}.csv")
    csv_path = Path(path)
    return csv_path if csv_path.is_absolute() else PROJECT_ROOT / csv_path


def main() -> None:
    args = parse_args()

    model_path = Path(args.model)
    if not model_path.is_absolute():
        model_path = PROJECT_ROOT / model_path
    config = load_config(args.config)
    env = build_env(config, backend_override=args.backend, show_viewer=args.viewer)
    model, _ = load_checkpoint(model_path, device=args.device)
    device = torch.device(args.device)

    csv_path = resolve_csv(args.csv, model_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []

    try:
        for episode_i in range(args.episodes):
            obs, info = env.reset(seed=args.seed + episode_i)
            total_reward = 0.0
            terminated = False
            truncated = False
            while not (terminated or truncated):
                obs_tensor = observation_to_tensor(obs, device=device, add_batch=True)
                action, _, _ = model.act(obs_tensor, deterministic=True)
                obs, reward, terminated, truncated, info = env.step(action.squeeze(0).cpu().numpy())
                total_reward += float(reward)

            rows.append({
                "episode": episode_i,
                "reward": total_reward,
                "success": info["success"],
                "collision": info["collision"],
                "out_of_bounds": info["out_of_bounds"],
                "truncated": truncated,
                "steps": info["episode_step"],
                "distance_to_goal": info["distance_to_goal"],
            })
    finally:
        env.close()

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["episode"])
        writer.writeheader()
        writer.writerows(rows)

    success_rate = sum(1 for row in rows if row["success"]) / len(rows) if rows else 0.0
    collision_rate = sum(1 for row in rows if row["collision"]) / len(rows) if rows else 0.0
    mean_distance = sum(float(row["distance_to_goal"]) for row in rows) / len(rows) if rows else 0.0
    print(f"episodes={len(rows)} success_rate={success_rate:.3f} "
          f"collision_rate={collision_rate:.3f} mean_final_distance={mean_distance:.3f}")
    print(f"Wrote evaluation CSV to {csv_path}")


if __name__ == "__main__":
    main()
