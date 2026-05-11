# Repository Status

Date: 2026-05-09 UTC
Branch: master
HEAD: dcf4c65

## Current State

- The repo is dirty. The RL stack and warehouse assets are still untracked in git, while several pre-existing project files are modified.
- The primary simulation target is a single quadcopter in `worlds/warehouse.xml`, controlled by `HoverController`.
- The RL environment is `WarehouseDroneEnv`; it now exposes a multi-modal Gymnasium `Dict` observation.
- PPO, checkpointing, training, and evaluation scripts have been updated for dict observations.

## Git Status Snapshot

```text
 M README.md
 M configs/robot.yaml
 M configs/simulation.yaml
 M requirements.txt
 M robots/drone/drone.xml
 M robots/humanoid/README.md
 M scripts/run_sim.py
 M src/robotics_genesis/__init__.py
 M src/robotics_genesis/controllers/__init__.py
 M tests/test_project_structure.py
?? STATUS.md
?? configs/rl.yaml
?? conftest.py
?? docs/rl_swarm_training_plan.md
?? pytest.ini
?? robots/drone/drone_on_going.xml
?? scripts/eval_drone_policy.py
?? scripts/gen_warehouse.py
?? scripts/run_warehouse.py
?? scripts/train_drone_ppo.py
?? src/robotics_genesis/controllers/drone_hover.py
?? src/robotics_genesis/controllers/waypoint_mission.py
?? src/robotics_genesis/rl/
?? tests/test_rl_components.py
?? worlds/
```

## Observation Schema

Schema version: `multimodal_depth_v1`

- `state`: `float32` shape `(28,)`
  - normalized position xyz
  - normalized linear velocity xyz
  - quaternion wxyz
  - normalized angular velocity xyz
  - normalized finite-difference linear acceleration xyz
  - normalized goal vector xyz
  - normalized distance to goal
  - previous action xyz
  - normalized hover wrench proxy: total thrust plus body torque xyz
  - contact flag
- `depth`: `float32` shape `(1, 64, 64)`
  - Genesis pinhole depth camera
  - `fov=90`, `near=0.1`, `far=8.0`
  - mounted at body offset `(0.08, 0.0, 0.02)`, looking along body `+X`
  - clipped and normalized to `[0, 1]`

## RL Stack

- `configs/rl.yaml` contains env, scenario, observation, reward, policy, and PPO config.
- `ActorCritic` is now multi-modal:
  - state MLP branch
  - depth CNN branch
  - fusion MLP before actor and critic heads
- Checkpoints now store `observation_schema` instead of a flat `obs_dim`.
- Old flat 21-float checkpoints are not expected to load without a manual migration.

## Verification

Fast test suite:

```bash
.venv/bin/python -m pytest -q
```

Result:

```text
13 passed, 2 skipped
```

Genesis depth-camera smoke:

```bash
XDG_CACHE_HOME=/tmp/robotics-genesis-cache MPLCONFIGDIR=/tmp/robotics-genesis-mpl RUN_GENESIS_TESTS=1 .venv/bin/python -m pytest -q tests/test_rl_components.py::test_warehouse_env_reset_and_step_smoke
```

Result:

```text
1 passed
```

## Known Risks

- Genesis/Taichi cache writes fail in this environment if `XDG_CACHE_HOME` is not redirected away from read-only `/home/namph32/.cache`.
- Depth rendering is significantly slower than the old flat observation path; training throughput should be measured before long PPO runs.
- RL evaluation with `--viewer` uses non-threaded Genesis viewer by default because threaded viewer mode flickers white when combined with depth-camera rendering on this WSL/GLX setup. Override with `GENESIS_VIEWER_THREAD=1` only if needed.
- The new policy architecture is intentionally incompatible with old flat-observation checkpoints.
- `src/robotics_genesis/rl/` is still untracked, so commit hygiene is important before sharing or branching.
