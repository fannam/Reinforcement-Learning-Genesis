from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import torch
from torch import nn

from robotics_genesis.rl.observations import OBSERVATION_SCHEMA_VERSION, observation_shape_from_space
from robotics_genesis.rl.policy import ActorCritic, PolicyConfig


@dataclass(frozen=True)
class PPOConfig:
    total_timesteps: int = 200000
    rollout_steps: int = 1024
    batch_size: int = 256
    update_epochs: int = 4
    learning_rate: float = 0.0003
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_range: float = 0.2
    ent_coef: float = 0.01
    vf_coef: float = 0.5
    max_grad_norm: float = 0.5
    device: str = "cpu"


@dataclass(frozen=True)
class TrainStats:
    update: int
    timesteps: int
    mean_reward: float
    mean_length: float
    policy_loss: float
    value_loss: float
    entropy: float
    approx_kl: float


def observation_to_tensor(
    obs: Mapping[str, np.ndarray],
    *,
    device: torch.device,
    add_batch: bool = False,
) -> dict[str, torch.Tensor]:
    tensors: dict[str, torch.Tensor] = {}
    for key, value in obs.items():
        tensor = torch.as_tensor(value, dtype=torch.float32, device=device)
        if add_batch:
            tensor = tensor.unsqueeze(0)
        tensors[key] = tensor
    return tensors


def _slice_observation_batch(
    obs: Mapping[str, torch.Tensor],
    indices: np.ndarray,
) -> dict[str, torch.Tensor]:
    return {key: value[indices] for key, value in obs.items()}


class RolloutBuffer:
    def __init__(self, rollout_steps: int, obs_shape: Mapping[str, tuple[int, ...]], action_dim: int) -> None:
        self.rollout_steps = int(rollout_steps)
        self.obs = {
            key: np.zeros((rollout_steps, *shape), dtype=np.float32)
            for key, shape in obs_shape.items()
        }
        self.actions = np.zeros((rollout_steps, action_dim), dtype=np.float32)
        self.log_probs = np.zeros(rollout_steps, dtype=np.float32)
        self.rewards = np.zeros(rollout_steps, dtype=np.float32)
        self.dones = np.zeros(rollout_steps, dtype=np.float32)
        self.values = np.zeros(rollout_steps, dtype=np.float32)
        self.advantages = np.zeros(rollout_steps, dtype=np.float32)
        self.returns = np.zeros(rollout_steps, dtype=np.float32)

    def add(
        self,
        step: int,
        *,
        obs: Mapping[str, np.ndarray],
        action: np.ndarray,
        log_prob: float,
        reward: float,
        done: bool,
        value: float,
    ) -> None:
        for key, value_arr in obs.items():
            self.obs[key][step] = value_arr
        self.actions[step] = action
        self.log_probs[step] = log_prob
        self.rewards[step] = reward
        self.dones[step] = float(done)
        self.values[step] = value

    def compute_returns_and_advantages(self, *, last_value: float, last_done: bool, gamma: float, gae_lambda: float) -> None:
        last_gae = 0.0
        for step in reversed(range(self.rollout_steps)):
            if step == self.rollout_steps - 1:
                next_non_terminal = 1.0 - float(last_done)
                next_value = float(last_value)
            else:
                next_non_terminal = 1.0 - self.dones[step + 1]
                next_value = self.values[step + 1]
            delta = self.rewards[step] + gamma * next_value * next_non_terminal - self.values[step]
            last_gae = delta + gamma * gae_lambda * next_non_terminal * last_gae
            self.advantages[step] = last_gae
        self.returns = self.advantages + self.values


def _safe_mean(values: list[float]) -> float:
    return float(np.mean(values)) if values else 0.0


def train_ppo(
    env,
    model: ActorCritic,
    config: PPOConfig,
    *,
    seed: int = 0,
    log_csv: Path | None = None,
) -> list[TrainStats]:
    np.random.seed(seed)
    torch.manual_seed(seed)
    device = torch.device(config.device)
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    obs, _ = env.reset(seed=seed)
    obs_shape = observation_shape_from_space(env.observation_space)
    action_dim = int(env.action_space.shape[0])

    stats: list[TrainStats] = []
    episode_rewards: list[float] = []
    episode_lengths: list[float] = []
    current_episode_reward = 0.0
    current_episode_length = 0
    timesteps = 0
    update = 0

    csv_file = None
    writer = None
    if log_csv is not None:
        log_csv.parent.mkdir(parents=True, exist_ok=True)
        csv_file = log_csv.open("w", newline="", encoding="utf-8")
        writer = csv.DictWriter(csv_file, fieldnames=list(TrainStats.__dataclass_fields__.keys()))
        writer.writeheader()

    try:
        while timesteps < config.total_timesteps:
            update += 1
            buffer = RolloutBuffer(config.rollout_steps, obs_shape, action_dim)
            last_done = False

            for step in range(config.rollout_steps):
                obs_tensor = observation_to_tensor(obs, device=device, add_batch=True)
                action_tensor, log_prob_tensor, value_tensor = model.act(obs_tensor)
                action = action_tensor.squeeze(0).cpu().numpy().astype(np.float32)
                next_obs, reward, terminated, truncated, _ = env.step(action)
                done = bool(terminated or truncated)

                buffer.add(
                    step,
                    obs=obs,
                    action=action,
                    log_prob=float(log_prob_tensor.item()),
                    reward=float(reward),
                    done=done,
                    value=float(value_tensor.item()),
                )

                timesteps += 1
                current_episode_reward += float(reward)
                current_episode_length += 1
                obs = next_obs
                last_done = done

                if done:
                    episode_rewards.append(current_episode_reward)
                    episode_lengths.append(float(current_episode_length))
                    current_episode_reward = 0.0
                    current_episode_length = 0
                    obs, _ = env.reset()

            with torch.no_grad():
                if last_done:
                    last_value = 0.0
                else:
                    obs_tensor = observation_to_tensor(obs, device=device, add_batch=True)
                    last_value = float(model.value(obs_tensor).item())
            buffer.compute_returns_and_advantages(
                last_value=last_value,
                last_done=last_done,
                gamma=config.gamma,
                gae_lambda=config.gae_lambda,
            )

            obs_batch = {
                key: torch.as_tensor(value, dtype=torch.float32, device=device)
                for key, value in buffer.obs.items()
            }
            action_batch = torch.as_tensor(buffer.actions, dtype=torch.float32, device=device)
            old_log_prob_batch = torch.as_tensor(buffer.log_probs, dtype=torch.float32, device=device)
            return_batch = torch.as_tensor(buffer.returns, dtype=torch.float32, device=device)
            advantage_batch = torch.as_tensor(buffer.advantages, dtype=torch.float32, device=device)
            advantage_batch = (advantage_batch - advantage_batch.mean()) / (advantage_batch.std(unbiased=False) + 1e-8)

            indices = np.arange(config.rollout_steps)
            policy_losses = []
            value_losses = []
            entropies = []
            approx_kls = []
            for _ in range(config.update_epochs):
                np.random.shuffle(indices)
                for start in range(0, config.rollout_steps, config.batch_size):
                    batch_idx = indices[start:start + config.batch_size]
                    new_log_prob, entropy, value = model.evaluate_actions(
                        _slice_observation_batch(obs_batch, batch_idx),
                        action_batch[batch_idx],
                    )
                    log_ratio = new_log_prob - old_log_prob_batch[batch_idx]
                    ratio = log_ratio.exp()
                    clipped_ratio = torch.clamp(ratio, 1.0 - config.clip_range, 1.0 + config.clip_range)
                    policy_loss = -torch.min(
                        ratio * advantage_batch[batch_idx],
                        clipped_ratio * advantage_batch[batch_idx],
                    ).mean()
                    value_loss = nn.functional.mse_loss(value, return_batch[batch_idx])
                    entropy_loss = entropy.mean()
                    loss = policy_loss + config.vf_coef * value_loss - config.ent_coef * entropy_loss

                    optimizer.zero_grad()
                    loss.backward()
                    nn.utils.clip_grad_norm_(model.parameters(), config.max_grad_norm)
                    optimizer.step()

                    with torch.no_grad():
                        approx_kl = ((ratio - 1.0) - log_ratio).mean()
                    policy_losses.append(float(policy_loss.item()))
                    value_losses.append(float(value_loss.item()))
                    entropies.append(float(entropy_loss.item()))
                    approx_kls.append(float(approx_kl.item()))

            train_stats = TrainStats(
                update=update,
                timesteps=min(timesteps, config.total_timesteps),
                mean_reward=_safe_mean(episode_rewards[-20:]),
                mean_length=_safe_mean(episode_lengths[-20:]),
                policy_loss=_safe_mean(policy_losses),
                value_loss=_safe_mean(value_losses),
                entropy=_safe_mean(entropies),
                approx_kl=_safe_mean(approx_kls),
            )
            stats.append(train_stats)
            if writer is not None:
                writer.writerow(asdict(train_stats))
                csv_file.flush()
            print(
                f"update={train_stats.update} timesteps={train_stats.timesteps} "
                f"mean_reward={train_stats.mean_reward:.3f} mean_len={train_stats.mean_length:.1f} "
                f"policy_loss={train_stats.policy_loss:.4f} value_loss={train_stats.value_loss:.4f}"
            )

    finally:
        if csv_file is not None:
            csv_file.close()

    return stats


def save_checkpoint(
    path: Path,
    *,
    model: ActorCritic,
    policy_config: PolicyConfig,
    ppo_config: PPOConfig,
    obs_shape: Mapping[str, tuple[int, ...]],
    action_dim: int,
    extra: dict[str, Any] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "policy_config": asdict(policy_config),
            "ppo_config": asdict(ppo_config),
            "observation_schema": {
                "version": OBSERVATION_SCHEMA_VERSION,
                "shape": {key: tuple(int(dim) for dim in shape) for key, shape in obs_shape.items()},
            },
            "action_dim": int(action_dim),
            "extra": extra or {},
        },
        path,
    )


def load_checkpoint(path: Path, *, device: str = "cpu") -> tuple[ActorCritic, dict[str, Any]]:
    try:
        checkpoint = torch.load(path, map_location=torch.device(device), weights_only=False)
    except TypeError:
        checkpoint = torch.load(path, map_location=torch.device(device))
    policy_config = PolicyConfig(**checkpoint["policy_config"])
    schema = checkpoint.get("observation_schema", {})
    obs_shape_raw = schema.get("shape")
    if obs_shape_raw is None:
        raise ValueError("Checkpoint does not contain a multimodal observation schema.")
    obs_shape = {key: tuple(int(dim) for dim in shape) for key, shape in obs_shape_raw.items()}
    model = ActorCritic(
        obs_shape,
        int(checkpoint["action_dim"]),
        policy_config,
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(torch.device(device))
    model.eval()
    return model, checkpoint
