# Legacy Humanoid

This folder keeps the legacy humanoid MJCF as a secondary asset. The repo's primary workflow is the drone + warehouse simulation.

Main file:

```text
assets/robots/humanoid/humanoid.xml
```

The humanoid model has 45 actuated hinge joints plus a floating root `freejoint`. It still works with the legacy single-robot runner:

```bash
.venv/bin/python scripts/validate_xml.py assets/robots/humanoid/humanoid.xml --mujoco
SHOW_VIEWER=1 .venv/bin/python scripts/run_sim.py --robot assets/robots/humanoid/humanoid.xml --steps 10000
```

Use `scripts/run_warehouse.py` for new drone + warehouse work.
