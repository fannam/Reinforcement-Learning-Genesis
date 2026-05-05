# Robotics Genesis Modular Humanoid

Dự án này tập trung vào một robot humanoid dạng modular, được thiết kế bằng MJCF/XML và chạy mô phỏng bằng Genesis.

## Cấu Trúc Chính

```text
configs/                Tham số robot và simulation
docs/                   Ghi chú thiết kế robot XML và roadmap phát triển
outputs/                Log, XML generated, video, checkpoint
robots/modular_humanoid Robot humanoid chính
scripts/                Script validate XML và chạy simulation
src/robotics_genesis/   Code Python dùng lại được
tests/                  Test cấu trúc XML
```

Robot chính:

```text
robots/modular_humanoid/modular_humanoid.xml
```

## Modular Humanoid

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

`modular_humanoid.xml` là file chính. Các bộ phận được ráp bằng MJCF `<include>`.

## Chạy Nhanh

```bash
source .venv/bin/activate
python scripts/validate_xml.py robots/modular_humanoid/modular_humanoid.xml --mujoco
python scripts/run_sim.py --steps 300
```

Mở viewer:

```bash
SHOW_VIEWER=1 python scripts/run_sim.py --steps 10000
```

Chạy qua `test.py`:

```bash
ROBOT_XML=robots/modular_humanoid/modular_humanoid.xml STEPS=100 .venv/bin/python test.py
SHOW_VIEWER=1 ROBOT_XML=robots/modular_humanoid/modular_humanoid.xml STEPS=10000 .venv/bin/python test.py
```

Chọn backend:

```bash
GENESIS_BACKEND=cpu python scripts/run_sim.py
GENESIS_BACKEND=gpu python scripts/run_sim.py
```

## Quy Trình Phát Triển

1. Sửa từng file trong `robots/modular_humanoid/parts/`.
2. Chạy validate:

```bash
python scripts/validate_xml.py robots/modular_humanoid/modular_humanoid.xml --mujoco
```

3. Chạy simulation ngắn:

```bash
python scripts/run_sim.py --steps 1
```

4. Mở viewer kiểm tra:

```bash
SHOW_VIEWER=1 python scripts/run_sim.py --steps 10000
```

Nếu đổi tên joint, cập nhật controller trong `src/robotics_genesis/controllers/sine_pose.py`.
