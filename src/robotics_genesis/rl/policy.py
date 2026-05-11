from __future__ import annotations

from dataclasses import dataclass
from math import prod
from typing import Iterable, Mapping

import torch
from torch import nn
from torch.distributions import Normal


@dataclass(frozen=True)
class PolicyConfig:
    state_hidden_sizes: tuple[int, ...] = (128,)
    depth_feature_dim: int = 128
    fusion_hidden_sizes: tuple[int, ...] = (256, 128)
    activation: str = "relu"
    log_std_init: float = -0.5


def _activation(name: str) -> type[nn.Module]:
    normalized = name.lower()
    if normalized == "relu":
        return nn.ReLU
    if normalized == "gelu":
        return nn.GELU
    if normalized == "tanh":
        return nn.Tanh
    raise ValueError(f"Unsupported activation: {name}")


def _mlp(input_dim: int, hidden_sizes: Iterable[int], activation: str) -> nn.Sequential:
    layers: list[nn.Module] = []
    prev_dim = input_dim
    act = _activation(activation)
    for hidden_dim in hidden_sizes:
        layers.append(nn.Linear(prev_dim, int(hidden_dim)))
        layers.append(act())
        prev_dim = int(hidden_dim)
    return nn.Sequential(*layers)


def _last_dim(input_dim: int, hidden_sizes: Iterable[int]) -> int:
    hidden_tuple = tuple(int(size) for size in hidden_sizes)
    return hidden_tuple[-1] if hidden_tuple else int(input_dim)


class ActorCritic(nn.Module):
    """Gaussian actor-critic network for state + depth observations."""

    def __init__(
        self,
        obs_shape: Mapping[str, tuple[int, ...]],
        action_dim: int,
        config: PolicyConfig | None = None,
    ) -> None:
        super().__init__()
        self.config = config or PolicyConfig()
        if "state" not in obs_shape or "depth" not in obs_shape:
            raise ValueError("obs_shape must contain 'state' and 'depth' entries.")

        self.obs_shape = {key: tuple(int(dim) for dim in value) for key, value in obs_shape.items()}
        self.state_dim = int(prod(self.obs_shape["state"]))
        self.depth_shape = self.obs_shape["depth"]
        if len(self.depth_shape) != 3:
            raise ValueError("Depth observation shape must be (channels, height, width).")

        self.action_dim = int(action_dim)
        act = _activation(self.config.activation)

        self.state_encoder = _mlp(self.state_dim, self.config.state_hidden_sizes, self.config.activation)
        self.depth_encoder = nn.Sequential(
            nn.Conv2d(self.depth_shape[0], 16, kernel_size=5, stride=2, padding=2),
            act(),
            nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1),
            act(),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
            act(),
            nn.AdaptiveAvgPool2d((4, 4)),
            nn.Flatten(),
            nn.Linear(64 * 4 * 4, int(self.config.depth_feature_dim)),
            act(),
        )

        state_feature_dim = _last_dim(self.state_dim, self.config.state_hidden_sizes)
        fusion_dim = state_feature_dim + int(self.config.depth_feature_dim)
        self.actor_body = _mlp(fusion_dim, self.config.fusion_hidden_sizes, self.config.activation)
        self.critic_body = _mlp(fusion_dim, self.config.fusion_hidden_sizes, self.config.activation)
        last_dim = _last_dim(fusion_dim, self.config.fusion_hidden_sizes)
        self.actor_mean = nn.Linear(last_dim, self.action_dim)
        self.critic_value = nn.Linear(last_dim, 1)
        self.log_std = nn.Parameter(torch.full((self.action_dim,), float(self.config.log_std_init)))

    def _features(self, obs: Mapping[str, torch.Tensor]) -> torch.Tensor:
        state = obs["state"]
        depth = obs["depth"]
        if state.ndim == len(self.obs_shape["state"]):
            state = state.unsqueeze(0)
        if depth.ndim == len(self.depth_shape):
            depth = depth.unsqueeze(0)
        state = state.reshape(state.shape[0], -1)
        return torch.cat([self.state_encoder(state), self.depth_encoder(depth)], dim=-1)

    def distribution(self, obs: Mapping[str, torch.Tensor]) -> Normal:
        features = self._features(obs)
        mean = torch.tanh(self.actor_mean(self.actor_body(features)))
        std = torch.exp(self.log_std).expand_as(mean)
        return Normal(mean, std)

    def value(self, obs: Mapping[str, torch.Tensor]) -> torch.Tensor:
        features = self._features(obs)
        return self.critic_value(self.critic_body(features)).squeeze(-1)

    @torch.no_grad()
    def act(
        self,
        obs: Mapping[str, torch.Tensor],
        *,
        deterministic: bool = False,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        dist = self.distribution(obs)
        raw_action = dist.mean if deterministic else dist.sample()
        action = torch.clamp(raw_action, -1.0, 1.0)
        log_prob = dist.log_prob(action).sum(dim=-1)
        value = self.value(obs)
        return action, log_prob, value

    def evaluate_actions(
        self,
        obs: Mapping[str, torch.Tensor],
        actions: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        dist = self.distribution(obs)
        clamped_actions = torch.clamp(actions, -1.0, 1.0)
        log_prob = dist.log_prob(clamped_actions).sum(dim=-1)
        entropy = dist.entropy().sum(dim=-1)
        value = self.value(obs)
        return log_prob, entropy, value
