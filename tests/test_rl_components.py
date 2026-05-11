from __future__ import annotations

import os

import numpy as np
import pytest

from robotics_genesis.rl.observations import DEPTH_IMAGE_SHAPE, STATE_OBSERVATION_SIZE, DroneState, build_observation
from robotics_genesis.rl.rewards import RewardConfig, compute_reward, is_out_of_bounds, tilt_penalty
from robotics_genesis.rl.scenarios import ScenarioConfig, sample_spawn_goal


def _dummy_observation() -> dict[str, np.ndarray]:
    return {
        "state": np.zeros(STATE_OBSERVATION_SIZE, dtype=np.float32),
        "depth": np.zeros(DEPTH_IMAGE_SHAPE, dtype=np.float32),
    }


def test_build_observation_shapes_and_dtypes():
    state = DroneState(
        pos=np.array([-2.0, -2.0, 2.0], dtype=np.float32),
        vel=np.zeros(3, dtype=np.float32),
        quat_wxyz=np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32),
        ang_vel=np.zeros(3, dtype=np.float32),
    )

    obs = build_observation(
        state,
        goal=(-1.0, -1.5, 2.0),
        previous_action=(0.0, 0.0, 0.0),
        contact_flag=False,
        linear_acceleration=(0.0, 0.0, 0.0),
        hover_wrench=(0.0, 0.0, 0.0, 0.0),
        depth_image=np.full((64, 64), 4.0, dtype=np.float32),
        depth_far=8.0,
    )

    assert set(obs) == {"state", "depth"}
    assert obs["state"].shape == (STATE_OBSERVATION_SIZE,)
    assert obs["state"].dtype == np.float32
    assert obs["state"][-1] == 0.0
    assert obs["depth"].shape == DEPTH_IMAGE_SHAPE
    assert obs["depth"].dtype == np.float32
    assert np.allclose(obs["depth"], 0.5)


def test_reward_prefers_progress_and_penalizes_collision():
    config = RewardConfig()
    progress_reward = compute_reward(
        previous_distance=2.0,
        current_distance=1.5,
        action=(0.0, 0.0, 0.0),
        quat_wxyz=(1.0, 0.0, 0.0, 0.0),
        contact=False,
        out_of_bounds=False,
        success=False,
        config=config,
    )
    collision_reward = compute_reward(
        previous_distance=2.0,
        current_distance=1.5,
        action=(0.0, 0.0, 0.0),
        quat_wxyz=(1.0, 0.0, 0.0, 0.0),
        contact=True,
        out_of_bounds=False,
        success=False,
        config=config,
    )

    assert progress_reward > 0.0
    assert collision_reward == pytest.approx(progress_reward - config.contact_penalty)


def test_bounds_and_tilt_helpers():
    assert is_out_of_bounds((23.0, 0.0, 2.0))
    assert not is_out_of_bounds((0.0, 0.0, 2.0))
    assert tilt_penalty((1.0, 0.0, 0.0, 0.0)) == pytest.approx(0.0)


def test_scenario_sampler_respects_distance_and_deterministic_mode():
    config = ScenarioConfig(min_goal_distance=1.0)
    rng = np.random.default_rng(7)

    scenario = sample_spawn_goal(rng, config, randomize=True)
    distance = np.linalg.norm(np.array(scenario.goal) - np.array(scenario.spawn))
    deterministic = sample_spawn_goal(rng, config, randomize=False)

    assert distance >= config.min_goal_distance
    assert deterministic.spawn == config.deterministic_spawn
    assert deterministic.goal == config.deterministic_goal


def test_warehouse_env_spaces_without_building_genesis():
    gymnasium = pytest.importorskip("gymnasium")
    from robotics_genesis.rl.envs.warehouse_drone import WarehouseDroneEnv

    env = WarehouseDroneEnv(randomize=False, episode_steps=5, control_skip=1)
    try:
        assert env.action_space.shape == (3,)
        assert isinstance(env.observation_space, gymnasium.spaces.Dict)
        assert env.observation_space["state"].shape == (STATE_OBSERVATION_SIZE,)
        assert env.observation_space["depth"].shape == DEPTH_IMAGE_SHAPE
    finally:
        env.close()


def test_actor_critic_outputs_action_and_value_shapes():
    torch = pytest.importorskip("torch")
    from robotics_genesis.rl.policy import ActorCritic, PolicyConfig

    obs_shape = {"state": (STATE_OBSERVATION_SIZE,), "depth": DEPTH_IMAGE_SHAPE}
    model = ActorCritic(
        obs_shape,
        action_dim=3,
        config=PolicyConfig(state_hidden_sizes=(16,), depth_feature_dim=16, fusion_hidden_sizes=(32,)),
    )
    obs = {
        "state": torch.zeros((4, STATE_OBSERVATION_SIZE), dtype=torch.float32),
        "depth": torch.zeros((4, *DEPTH_IMAGE_SHAPE), dtype=torch.float32),
    }
    action, log_prob, value = model.act(obs)
    eval_log_prob, entropy, eval_value = model.evaluate_actions(obs, action)

    assert action.shape == (4, 3)
    assert log_prob.shape == (4,)
    assert value.shape == (4,)
    assert eval_log_prob.shape == (4,)
    assert entropy.shape == (4,)
    assert eval_value.shape == (4,)
    assert torch.all(action <= 1.0)
    assert torch.all(action >= -1.0)


def test_custom_ppo_updates_on_dummy_env(tmp_path):
    gymnasium = pytest.importorskip("gymnasium")
    pytest.importorskip("torch")
    from robotics_genesis.rl.policy import ActorCritic, PolicyConfig
    from robotics_genesis.rl.ppo import PPOConfig, train_ppo

    class DummyEnv(gymnasium.Env):
        def __init__(self):
            self.observation_space = gymnasium.spaces.Dict({
                "state": gymnasium.spaces.Box(-10.0, 10.0, shape=(STATE_OBSERVATION_SIZE,), dtype=np.float32),
                "depth": gymnasium.spaces.Box(0.0, 1.0, shape=DEPTH_IMAGE_SHAPE, dtype=np.float32),
            })
            self.action_space = gymnasium.spaces.Box(-1.0, 1.0, shape=(3,), dtype=np.float32)
            self.step_i = 0

        def reset(self, *, seed=None, options=None):
            super().reset(seed=seed)
            self.step_i = 0
            return _dummy_observation(), {}

        def step(self, action):
            self.step_i += 1
            reward = 1.0 - float(np.linalg.norm(action))
            terminated = self.step_i >= 4
            return _dummy_observation(), reward, terminated, False, {}

    env = DummyEnv()
    obs_shape = {"state": (STATE_OBSERVATION_SIZE,), "depth": DEPTH_IMAGE_SHAPE}
    model = ActorCritic(obs_shape, 3, PolicyConfig(state_hidden_sizes=(16,), depth_feature_dim=16, fusion_hidden_sizes=(32,)))
    stats = train_ppo(
        env,
        model,
        PPOConfig(total_timesteps=8, rollout_steps=4, batch_size=2, update_epochs=1),
        seed=1,
        log_csv=tmp_path / "metrics.csv",
    )

    assert stats
    assert stats[-1].timesteps == 8
    assert (tmp_path / "metrics.csv").exists()


def test_checkpoint_round_trip_multimodal(tmp_path):
    torch = pytest.importorskip("torch")
    from robotics_genesis.rl.policy import ActorCritic, PolicyConfig
    from robotics_genesis.rl.ppo import PPOConfig, load_checkpoint, save_checkpoint

    obs_shape = {"state": (STATE_OBSERVATION_SIZE,), "depth": DEPTH_IMAGE_SHAPE}
    policy_config = PolicyConfig(state_hidden_sizes=(16,), depth_feature_dim=16, fusion_hidden_sizes=(32,))
    model = ActorCritic(obs_shape, 3, policy_config)
    checkpoint_path = tmp_path / "model.pt"

    save_checkpoint(
        checkpoint_path,
        model=model,
        policy_config=policy_config,
        ppo_config=PPOConfig(total_timesteps=8),
        obs_shape=obs_shape,
        action_dim=3,
    )
    loaded, checkpoint = load_checkpoint(checkpoint_path)

    assert isinstance(loaded, ActorCritic)
    assert checkpoint["observation_schema"]["shape"]["state"] == (STATE_OBSERVATION_SIZE,)


@pytest.mark.skipif(os.getenv("RUN_GENESIS_TESTS") != "1", reason="Genesis env smoke tests are opt-in.")
def test_warehouse_env_reset_and_step_smoke():
    pytest.importorskip("gymnasium")
    from robotics_genesis.rl.envs.warehouse_drone import WarehouseDroneEnv

    env = WarehouseDroneEnv(
        backend="cpu",
        randomize=False,
        episode_steps=3,
        control_skip=1,
    )
    try:
        obs, info = env.reset(seed=0)
        assert obs["state"].shape == (STATE_OBSERVATION_SIZE,)
        assert obs["depth"].shape == DEPTH_IMAGE_SHAPE
        assert np.all((obs["depth"] >= 0.0) & (obs["depth"] <= 1.0))
        assert info["distance_to_goal"] >= 0.0

        obs, reward, terminated, truncated, info = env.step(np.zeros(3, dtype=np.float32))
        assert obs["state"].shape == (STATE_OBSERVATION_SIZE,)
        assert obs["depth"].shape == DEPTH_IMAGE_SHAPE
        assert isinstance(reward, float)
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
    finally:
        env.close()
