# RL and Swarm Training Plan

This plan turns the current drone + warehouse simulation into a trainable reinforcement learning stack, then extends it to swarm training.

Current baseline:

- Drone MJCF: `robots/drone/drone.xml`
- Warehouse MJCF: `worlds/warehouse.xml`
- Warehouse runner: `scripts/run_warehouse.py`
- Low-level stabilizer: `HoverController`
- Mission helper: `WaypointMission`

Primary design choice: **train high-level navigation first, not raw motor thrust**. The first RL policy should command target offsets or velocity-like actions while `HoverController` keeps the drone stable. Raw rotor-level RL can come later after navigation, logging, resets, and evaluation are reliable.

## Target Outcome

The repo should support:

1. Single-drone RL training for waypoint navigation in the warehouse.
2. Reproducible training/evaluation scripts with saved policies and logs.
3. Curriculum and randomization for better robustness.
4. A multi-drone/swarm environment using shared-policy training.
5. Clear success metrics: reached goals, collisions, timeouts, path efficiency, and swarm separation.

## Architecture

Add a new RL package:

```text
src/robotics_genesis/rl/
  __init__.py
  warehouse_env.py          # Single-drone Gymnasium-style env
  rewards.py                # Reward, termination, metrics helpers
  observations.py           # Observation builders and normalization helpers
  scenarios.py              # Spawn/goal sampling and curriculum configs
  swarm_env.py              # Later: multi-drone environment

scripts/
  train_drone_ppo.py        # Single-drone PPO training
  eval_drone_policy.py      # Load policy and run evaluation/viewer
  train_swarm_ppo.py        # Later: multi-agent/shared-policy training
  eval_swarm_policy.py      # Later: swarm evaluation

configs/
  rl.yaml                   # Single-drone training/env config
  swarm.yaml                # Later: swarm config

outputs/
  checkpoints/              # Saved policies
  logs/                     # CSV training/evaluation summaries
  videos/                   # Optional rollouts
```

New dependencies:

```text
gymnasium
pyyaml
torch
```

Add `ray[rllib]` only when starting the multi-agent RLlib phase. Do not add it for the single-drone PPO milestone unless needed.

## Phase 1: Single-Drone RL Environment

Goal: make one drone trainable with a standard `reset()` / `step()` environment API.

### Environment Class

Implement `WarehouseDroneEnv` in `src/robotics_genesis/rl/warehouse_env.py`.

Constructor arguments:

```python
WarehouseDroneEnv(
    world_xml="worlds/warehouse.xml",
    drone_xml="robots/drone/drone.xml",
    backend="cpu",
    episode_steps=1000,
    control_skip=4,
    action_mode="target_delta",
    seed=None,
    randomize=True,
    show_viewer=False,
)
```

Behavior:

- Build a Genesis scene containing the warehouse and one drone.
- Reuse `strip_world_decorations()` logic so the drone is spawned without its standalone floor/lights.
- Reuse `HoverController` for low-level stabilization.
- `reset()` samples a spawn and goal, initializes the drone, resets episode metrics, and returns `(obs, info)`.
- `step(action)` converts policy action into a hover target, advances Genesis for `control_skip` physics steps, computes reward/done/truncated, and returns `(obs, reward, terminated, truncated, info)`.
- If Genesis entity state cannot be reset cleanly in-place, v1 may rebuild the scene per episode. Prefer correctness first; optimize later.

### Action Space v1

Use high-level target deltas:

```text
Box(low=-1, high=1, shape=(3,), dtype=float32)
```

Mapping:

- `action[0]`: desired x target delta
- `action[1]`: desired y target delta
- `action[2]`: desired z target delta

Scale:

```text
dx, dy: +/- 0.75 m per env step
dz:     +/- 0.35 m per env step
```

Clamp target position to:

```text
x: [-21.5, 21.5]
y: [-13.5, 13.5]
z: [0.75, 5.25]
```

Do not expose raw force/torque or rotor commands in v1.

### Observation Space v1

Use a flat float32 vector:

```text
[
  drone_pos_xyz,           # 3
  drone_vel_xyz,           # 3
  drone_quat_wxyz,         # 4
  drone_ang_vel_xyz,       # 3
  goal_vector_xyz,         # 3 = goal - position
  distance_to_goal,        # 1
  previous_action_xyz,     # 3
  contact_flag,            # 1
]
```

Total: 21 floats.

Normalize where practical:

- Positions and goal vector by warehouse half-extents.
- Velocities by a conservative max velocity, initially `5.0`.
- Distance by max warehouse diagonal.
- Contact flag as `0.0` or `1.0`.

Do not add camera images or lidar in v1. Add proximity/raycast observations after the first PPO loop is working.

### Reward v1

Implement reward helpers in `rewards.py`.

Reward per env step:

```text
reward =
  progress_weight * (previous_distance - current_distance)
  - distance_weight * current_distance
  - action_weight * ||action||^2
  - tilt_weight * tilt_penalty
  - contact_penalty if contact
  - bounds_penalty if out of bounds
  + success_bonus if reached goal
```

Initial weights:

```yaml
reward:
  progress_weight: 8.0
  distance_weight: 0.02
  action_weight: 0.01
  tilt_weight: 0.02
  contact_penalty: 20.0
  bounds_penalty: 20.0
  success_bonus: 50.0
```

Success condition:

```text
distance_to_goal <= 0.35 m for 20 consecutive env steps
```

Termination:

- `terminated=True` on success.
- `terminated=True` on collision with warehouse.
- `terminated=True` on out-of-bounds.
- `truncated=True` on episode step limit.

Info dict:

```python
{
    "distance_to_goal": float,
    "success": bool,
    "collision": bool,
    "out_of_bounds": bool,
    "episode_step": int,
    "contacts": int,
    "goal": tuple[float, float, float],
    "spawn": tuple[float, float, float],
}
```

## Phase 2: PPO Training

Goal: train one drone to reach random goals better than a random policy.

### Training Script

Implement `scripts/train_drone_ppo.py`.

CLI:

```bash
.venv/bin/python scripts/train_drone_ppo.py \
  --config configs/rl.yaml \
  --total-timesteps 200000 \
  --backend cpu \
  --run-name ppo_single_drone_v1
```

Behavior:

- Load YAML config.
- Create `WarehouseDroneEnv`.
- Build the repo-owned PyTorch `ActorCritic`.
- Train with the repo-owned PPO loop in `src/robotics_genesis/rl/ppo.py`.
- Write checkpoints under `outputs/checkpoints/<run-name>/`.
- Write logs under `outputs/logs/<run-name>/`.
- Save final model as `outputs/checkpoints/<run-name>/final.pt`.

Initial PPO config:

```yaml
ppo:
  device: cpu
  total_timesteps: 200000
  learning_rate: 0.0003
  rollout_steps: 1024
  batch_size: 256
  update_epochs: 4
  gamma: 0.99
  gae_lambda: 0.95
  clip_range: 0.2
  ent_coef: 0.01
  vf_coef: 0.5
  max_grad_norm: 0.5
```

Start with one environment process. Add vectorization only after single-env training is stable, because Genesis global initialization and scene reset behavior must be verified first.

### Evaluation Script

Implement `scripts/eval_drone_policy.py`.

CLI:

```bash
.venv/bin/python scripts/eval_drone_policy.py \
  --model outputs/checkpoints/ppo_single_drone_v1/final.pt \
  --episodes 20 \
  --backend cpu
```

Options:

- `--viewer` to visualize one policy rollout.
- `--seed` for repeatability.
- `--csv outputs/logs/eval_single_drone.csv` for episode summaries.

Metrics:

- success rate
- collision rate
- timeout rate
- mean final distance
- mean episode length
- mean cumulative reward

Acceptance for Phase 2:

- Random policy baseline is measured.
- PPO policy beats random on success rate and final distance.
- Training and evaluation scripts run from clean CLI commands.
- One saved model can be loaded and evaluated without retraining.

## Phase 3: Better Observations and Curriculum

Goal: make navigation learnable around real warehouse obstacles, not only open-space target seeking.

### Proximity Sensing

Add simple ray/proximity features before camera images.

Observation extension:

```text
horizontal_rays: 16 distances
vertical_rays:   5 distances
```

Use Genesis raycasting if available and stable. If not, implement a conservative geometric approximation from known warehouse bounds and static obstacle AABBs extracted from MJCF.

Do not add RGB/depth camera RL until vectorized state-based RL is working.

### Curriculum

Implement scenario sampling in `scenarios.py`.

Curriculum levels:

1. Open-space short waypoint, no dense obstacle routes.
2. Medium-distance routes in central aisles.
3. Shelf-adjacent goals.
4. Routes crossing conveyors/pod field.
5. Full random warehouse goals.

Config:

```yaml
curriculum:
  enabled: true
  level: 1
  promote_success_rate: 0.75
  promote_window: 100
```

Promotion can be manual in v1. Automatic curriculum can come after metrics are reliable.

### Domain Randomization

Start with:

- spawn position
- goal position
- drone yaw
- small mass scale range, e.g. `[0.9, 1.1]`
- controller gain scale range, e.g. `[0.8, 1.2]`

Do not randomize warehouse geometry in the first training milestone. Regenerating the world every episode is too expensive and complicates debugging.

## Phase 4: Vectorized Training and Performance

Goal: improve throughput without breaking reproducibility.

Steps:

1. Benchmark single-env FPS for headless CPU and GPU.
2. Try a repo-owned multiprocessing runner with one Genesis scene per process.
3. If Genesis global state blocks multi-process stability, use multiple independent training runs and aggregate evaluation first.
4. Add vectorized training only after deterministic single-env reset is stable.

Metrics to track:

- sim steps/sec
- env steps/sec
- wall-clock time per 100k PPO steps
- crash rate from environment/runtime errors

## Phase 5: Swarm Environment

Goal: train multiple drones with shared policy and collision avoidance.

Do not start swarm until single-drone PPO reaches stable non-random waypoint behavior.

### Swarm v1 Task

Task:

- `N` drones spawn in safe positions.
- Each drone has one assigned goal.
- All drones use the same policy.
- Episode succeeds when all drones reach their goals.
- Episode fails for any warehouse collision, drone-drone collision, or out-of-bounds event.

Start with:

```yaml
swarm:
  num_drones: 2
  shared_policy: true
  min_spawn_separation: 1.5
  min_goal_separation: 1.5
```

Scale after success:

```text
2 drones -> 4 drones -> 8 drones
```

### Swarm Observation v1

Per-agent observation:

```text
single_drone_obs
nearest_k_neighbor_relative_positions
nearest_k_neighbor_relative_velocities
nearest_k_neighbor_goal_vectors
```

Use `k=3`. If fewer neighbors exist, pad with zeros and include a valid mask.

### Swarm Reward v1

Per-agent reward:

```text
single_drone_reward
- separation_penalty if another drone is too close
- team_penalty if any drone crashes
+ team_success_bonus when all drones finish
```

Initial separation threshold:

```text
soft separation: 1.0 m
hard collision/failure: contact or < 0.35 m center distance
```

### Swarm Training Stack

Use one of these paths:

1. **Custom fixed-size shared-policy approximation first**
   - Treat all drones as one large observation/action vector.
   - Simpler implementation.
   - Less flexible for variable agent counts.

2. **RLlib MultiAgentEnv second**
   - Proper per-agent API.
   - Better for shared policy and future heterogeneous agents.
   - Larger dependency and more setup.

Recommended sequence:

- Implement a custom fixed-size shared-policy swarm for `N=2`.
- Move to RLlib only when the environment and reward are stable.

## Phase 6: Evaluation and Reporting

Add reproducible evaluation reports.

Per-run outputs:

```text
outputs/logs/<run-name>/
  train_config.yaml
  eval_summary.csv
  episode_metrics.csv
  random_baseline.csv
```

Evaluation scenarios:

- Fixed seed set: `0..19`
- Easy aisle goals
- Shelf-adjacent goals
- Dense pod/conveyor area goals
- Long route goals

Report:

- success rate
- collision rate
- timeout rate
- mean final distance
- mean path length
- mean control effort
- swarm mean minimum separation

## Testing Plan

Fast tests should remain default and should not require Genesis runtime.

Add tests for:

- `WarehouseDroneEnv` spaces have expected shape and dtype.
- Reward increases when distance decreases.
- Success triggers after required dwell steps.
- Collision/out-of-bounds termination helpers work.
- Scenario sampler returns in-bounds spawn/goal pairs.
- Swarm neighbor observation padding/masks are correct.

Genesis smoke tests remain opt-in:

```bash
RUN_GENESIS_TESTS=1 .venv/bin/python -m pytest -q
```

Opt-in smoke coverage:

- Create env, `reset()`, random `step()` for 20 steps.
- Train PPO for a tiny run, e.g. 256 timesteps.
- Load saved PPO model and run one short eval episode.

## Milestones

### Milestone A: Trainable Single-Drone Env

Deliverables:

- `WarehouseDroneEnv`
- `rewards.py`
- `scenarios.py`
- `configs/rl.yaml`
- fast tests for observation/reward/termination

Done when:

- Random actions can run for 100 env steps without Python/runtime errors.
- `reset()` and `step()` return Gymnasium-compatible values.
- Contact, success, out-of-bounds, and timeout are reflected in `info`.

### Milestone B: PPO Smoke Training

Deliverables:

- `scripts/train_drone_ppo.py`
- `scripts/eval_drone_policy.py`
- saved checkpoint path convention
- CSV evaluation summary

Done when:

- PPO trains for at least 10k timesteps.
- A saved model can be loaded.
- Evaluation beats random baseline on fixed seeds.

### Milestone C: Useful Navigation Policy

Deliverables:

- tuned reward weights
- curriculum level 1-3
- eval report

Done when:

- Success rate is at least 70% on easy/medium waypoint tasks.
- Collision rate is below 10% on evaluation seeds.
- Viewer evaluation shows coherent target-seeking, not only hovering or drifting.

### Milestone D: Obstacle-Aware Policy

Deliverables:

- proximity/raycast observation
- curriculum level 4-5
- route evaluation near shelves/conveyors/pods

Done when:

- Success rate is at least 60% in dense warehouse tasks.
- Collision rate is below 20% in dense warehouse tasks.

### Milestone E: Swarm v1

Deliverables:

- `SwarmWarehouseEnv`
- fixed `num_drones=2`
- shared-policy training script
- swarm evaluation script

Done when:

- Two drones can reach separate goals more reliably than random.
- Drone-drone collision rate is tracked and penalized.
- Minimum separation metrics are logged.

## Risks and Controls

Risk: Genesis reset may not support cheap per-episode resets.

- Control: rebuild the scene per episode for correctness first; optimize later.

Risk: Training with raw physics is slow.

- Control: high-level action space, `control_skip`, no camera observations in v1.

Risk: Reward hacking leads to hovering instead of navigating.

- Control: progress reward, final distance metric, random baseline, fixed evaluation seeds.

Risk: Swarm complexity hides single-agent bugs.

- Control: swarm begins only after single-drone policy beats random.

Risk: ROS pytest plugins or ambient environment packages break tests.

- Control: keep `pytest.ini` plugin disables and avoid requiring ROS for RL tests.

## Current Implementation Status

Implemented:

1. RL dependencies in `requirements.txt`.
2. `src/robotics_genesis/rl/` with `WarehouseDroneEnv`, observations, rewards, and scenario sampling.
3. High-level target-delta action space.
4. `configs/rl.yaml`.
5. Custom PyTorch PPO training and evaluation scripts.
6. Fast tests for observations, rewards, scenarios, env spaces, and opt-in Genesis env smoke coverage.

Immediate next task:

1. Run a real PPO training session, starting with `10k-50k` timesteps.
2. Evaluate against a random-policy baseline on fixed seeds.
3. Tune reward weights and episode length until the drone reliably improves final distance.
4. Only then add proximity/raycast observations and curriculum levels.

Do not implement swarm or raw rotor actions until the single-drone PPO policy beats random on fixed evaluation seeds.
