# Modular Humanoid

Template humanoid được chia thành nhiều file XML nhỏ bằng MJCF `<include>`.

File chính:

```text
robots/modular_humanoid/modular_humanoid.xml
```

Cấu trúc:

```text
robots/modular_humanoid/
  modular_humanoid.xml
  parts/
    assets.xml
    scene.xml
    body.xml
    torso.xml
    right_arm.xml
    left_arm.xml
    right_leg.xml
    left_leg.xml
    actuators.xml
  meshes/
```

Lệnh test:

```bash
.venv/bin/python scripts/validate_xml.py robots/modular_humanoid/modular_humanoid.xml --mujoco
SHOW_VIEWER=1 .venv/bin/python scripts/run_sim.py --robot robots/modular_humanoid/modular_humanoid.xml --steps 10000
```

Khi phát triển robot thật, copy folder này thành `robots/my_humanoid_v1/` rồi sửa từng file trong `parts/`.
