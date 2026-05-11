# Robotics Genesis Drone Warehouse

This repo uses **Genesis** and **MJCF/XML** to simulate a quadcopter in a warehouse scene. The default workflow is now drone-first:

```text
assets/robots/drone/drone.xml      Quadcopter MJCF
assets/worlds/warehouse.xml        Generated warehouse MJCF
scripts/gen_warehouse.py    Deterministic warehouse generator
scripts/run_warehouse.py    Drone + warehouse simulation runner
src/robotics_genesis/       Shared Python utilities and controllers
tests/                      Fast structure/controller tests
```

The humanoid files under `assets/robots/humanoid/` are legacy/secondary assets. Use `scripts/run_warehouse.py` for the primary simulation.

## Requirements

- Ubuntu 22.04/24.04 or WSL2 Ubuntu on Windows 11.
- Python `>=3.10,<3.14`; this repo is currently used with Python `3.12`.
- CPU simulation works. GPU simulation is optional and depends on a working CUDA/PyTorch setup.
- Viewer mode needs a desktop/display environment such as WSLg or an X server.

ROS 2 is not required for the Genesis simulation path. `tools/install_ros2_jazzy.sh` is only for separate ROS 2 Jazzy setup.

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip setuptools wheel
```

Install PyTorch first. CPU-only example:

```bash
.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
```

Then install project dependencies:

```bash
.venv/bin/pip install -r requirements.txt
```

Check the environment:

```bash
.venv/bin/python - <<'PY'
import genesis as gs
import mujoco

print("Genesis:", gs.__version__)
print("MuJoCo:", mujoco.__version__)
PY
```

## Run

Validate XML:

```bash
.venv/bin/python scripts/validate_xml.py assets/robots/drone/drone.xml --mujoco
.venv/bin/python scripts/validate_xml.py assets/worlds/warehouse.xml --mujoco
```

Regenerate the warehouse:

```bash
.venv/bin/python scripts/gen_warehouse.py
```

Run a headless hover smoke test:

```bash
SHOW_VIEWER=0 GENESIS_BACKEND=cpu .venv/bin/python scripts/run_warehouse.py --steps 100 --backend cpu
```

Run a simple waypoint mission:

```bash
SHOW_VIEWER=0 GENESIS_BACKEND=cpu .venv/bin/python scripts/run_warehouse.py \
  --steps 600 \
  --backend cpu \
  --waypoint -1.5 -2.0 2.0 \
  --waypoint -1.0 -1.5 2.0 \
  --mission-log demo_waypoints.csv
```

Bare mission log filenames are written under `outputs/logs/`.

## RL Training

The first RL target is single-drone waypoint navigation with high-level target-delta actions. `HoverController` remains the low-level stabilizer; the policy learns where to move the hover target.

Install the RL dependencies from `requirements.txt`, then run a small custom PyTorch PPO smoke train:

```bash
.venv/bin/python scripts/train_drone_ppo.py \
  --config configs/rl/single_drone_ppo.yaml \
  --total-timesteps 10000 \
  --rollout-steps 256 \
  --batch-size 64 \
  --backend cpu \
  --run-name ppo_single_drone_smoke
```

Evaluate a saved model:

```bash
.venv/bin/python scripts/eval_drone_policy.py \
  --model outputs/checkpoints/ppo_single_drone_smoke/final.pt \
  --config configs/rl/single_drone_ppo.yaml \
  --episodes 20 \
  --backend cpu \
  --csv outputs/logs/eval_single_drone_smoke.csv
```

Show one rollout in the viewer:

```bash
SHOW_VIEWER=1 .venv/bin/python scripts/eval_drone_policy.py \
  --model outputs/checkpoints/ppo_single_drone_smoke/final.pt \
  --episodes 1 \
  --viewer
```

The detailed RL/swarm roadmap is in `docs/plans/rl_swarm_training_plan.md`.

Open the viewer:

```bash
SHOW_VIEWER=1 .venv/bin/python scripts/run_warehouse.py --steps 10000 --viewer
```

By default, the runner asks for GPU and falls back to CPU if CUDA is unavailable. To force CPU:

```bash
GENESIS_BACKEND=cpu .venv/bin/python scripts/run_warehouse.py --steps 300 --backend cpu
```

## Tests

Fast tests avoid requiring Genesis runtime:

```bash
.venv/bin/python -m pytest -q
```

Optional manual smoke checks:

```bash
.venv/bin/python scripts/validate_xml.py assets/robots/drone/drone.xml --mujoco
.venv/bin/python scripts/validate_xml.py assets/worlds/warehouse.xml --mujoco
SHOW_VIEWER=0 GENESIS_BACKEND=cpu .venv/bin/python scripts/run_warehouse.py --steps 100 --backend cpu
```

## Notes

- `assets/robots/drone/drone.xml` contains a visual/collision split: visual geoms are group `2`, collision geoms are group `3`.
- Genesis does not currently use the MJCF site-based drone actuators in this setup, so `HoverController` applies a body-frame wrench to the chassis link.
- `scripts/run_warehouse.py` strips the drone's standalone floor/lights before spawning it into the warehouse scene.
- Generated files under `outputs/` are ignored except `.gitkeep` placeholders.

## Troubleshooting

If there is no `python` shell alias, use `.venv/bin/python` or `python3`.

If viewer mode fails on WSL, check OpenGL:

```bash
echo "$DISPLAY"
glxinfo -B
```

If needed, try:

```bash
SHOW_VIEWER=1 \
GENESIS_GL_PLATFORM=glx \
GALLIUM_DRIVER=d3d12 \
MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA \
.venv/bin/python scripts/run_warehouse.py --steps 10000 --viewer
```

If viewer threading causes OpenGL context errors:

```bash
SHOW_VIEWER=1 GENESIS_VIEWER_THREAD=0 .venv/bin/python scripts/run_warehouse.py --steps 10000 --viewer
```
