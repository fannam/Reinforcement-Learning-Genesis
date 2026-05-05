# Robotics Genesis Modular Humanoid

Dự án này dùng **Genesis** để mô phỏng một robot humanoid được thiết kế bằng **MJCF/XML**. Robot chính được chia thành nhiều file XML nhỏ để dễ phát triển từng bộ phận như torso, tay, chân, actuator và asset.

## Yêu Cầu Hệ Thống

Khuyến nghị:

- OS: Ubuntu 22.04/24.04 hoặc WSL2 Ubuntu trên Windows 11.
- Python: `>=3.10,<3.14`. Repo hiện được test với Python `3.12`.
- CPU simulation: chạy được.
- GPU simulation: tùy chọn, cần driver GPU phù hợp.
- Viewer GUI: cần môi trường desktop/display. Trên WSL nên dùng WSLg hoặc X server.

Không bắt buộc:

- ROS 2 không cần để chạy simulation Genesis trong repo này.
- `script.sh` chỉ dùng nếu bạn muốn cài ROS 2 Jazzy riêng.

## Cấu Trúc Dự Án

```text
configs/                  Tham số robot và simulation
docs/                     Tài liệu thiết kế XML và roadmap phát triển
outputs/                  Log, video, checkpoint, XML generated
robots/modular_humanoid/  Robot humanoid chính
scripts/                  CLI validate XML và chạy simulation
src/robotics_genesis/     Code Python dùng lại được
tests/                    Test cấu trúc XML
```

Robot chính:

```text
robots/modular_humanoid/modular_humanoid.xml
```

## Cấu Trúc Robot

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

`modular_humanoid.xml` là file chính. Các file trong `parts/` được ráp bằng MJCF `<include>`.

## Cài Đặt Từ Đầu

### 1. Cài system packages

Ubuntu/WSL:

```bash
sudo apt update
sudo apt install -y \
  python3 \
  python3-venv \
  python3-pip \
  build-essential \
  git \
  libgl1 \
  libegl1 \
  libglfw3 \
  libxrender1 \
  libxext6 \
  libsm6 \
  mesa-utils
```

### 2. Tạo virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

### 3. Cài PyTorch

CPU-only:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

Nếu dùng NVIDIA GPU/CUDA, cài PyTorch theo phiên bản CUDA phù hợp với máy của bạn trước khi cài các package còn lại.

### 4. Cài thư viện Python của project

```bash
pip install -r requirements.txt
```

Các thư viện chính:

- `genesis-world`: physics simulation.
- `mujoco`: validate/load MJCF.
- `pyglet`: OpenGL/viewer.
- `pytest`: chạy test.

### 5. Kiểm tra cài đặt

```bash
python - <<'PY'
import genesis as gs
import mujoco

print("Genesis:", gs.__version__)
print("MuJoCo:", mujoco.__version__)
PY
```

## Chạy Simulation

Validate MJCF/XML:

```bash
source .venv/bin/activate
python scripts/validate_xml.py robots/modular_humanoid/modular_humanoid.xml --mujoco
```

Chạy headless 300 steps:

```bash
python scripts/run_sim.py --steps 300
```

Mở viewer:

```bash
SHOW_VIEWER=1 python scripts/run_sim.py --steps 10000
```

Chạy bằng CPU:

```bash
GENESIS_BACKEND=cpu python scripts/run_sim.py --steps 300
```

Chạy bằng GPU:

```bash
GENESIS_BACKEND=gpu python scripts/run_sim.py --steps 300
```

Chạy trực tiếp qua `test.py`:

```bash
ROBOT_XML=robots/modular_humanoid/modular_humanoid.xml STEPS=100 .venv/bin/python test.py
SHOW_VIEWER=1 ROBOT_XML=robots/modular_humanoid/modular_humanoid.xml STEPS=10000 .venv/bin/python test.py
```

## Lưu Ý Về XML Include

Genesis có thể gặp vấn đề với path tương đối khi load MJCF có `<include>`. Repo này xử lý bằng cách tự expand XML modular vào:

```text
outputs/generated/modular_humanoid.expanded.xml
```

File generated này chỉ là output tạm và đã được ignore trong git.

## Quy Trình Phát Triển Robot

1. Sửa một file trong `robots/modular_humanoid/parts/`.
2. Validate XML:

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

Nếu đổi tên joint, cập nhật thêm:

- `robots/modular_humanoid/parts/actuators.xml`
- `src/robotics_genesis/controllers/sine_pose.py`
- `tests/test_project_structure.py`

## Chạy Test

```bash
source .venv/bin/activate
pytest -q
```

Nếu `pytest` chưa có:

```bash
pip install pytest
```

## Troubleshooting

Nếu không có lệnh `python`:

```bash
python3 --version
source .venv/bin/activate
python --version
```

Nếu viewer không mở trên WSL:

```bash
echo $DISPLAY
SHOW_VIEWER=1 PYOPENGL_PLATFORM=glx python scripts/run_sim.py --steps 10000
```

Nếu simulation chậm:

```bash
GENESIS_BACKEND=cpu python scripts/run_sim.py --steps 100
```

Nếu XML lỗi:

```bash
python scripts/validate_xml.py robots/modular_humanoid/modular_humanoid.xml --mujoco
```

Nếu thấy warning self-collision ở neutral pose, đó thường là dấu hiệu một số geom đang chạm nhau ở tư thế ban đầu. Chỉnh vị trí link hoặc kích thước geom trong `parts/`.

## Tài Liệu Nội Bộ

- `docs/robot_xml_guide.md`: hướng dẫn viết MJCF/XML.
- `docs/parts_coding_guide.md`: hướng dẫn code từng file trong `robots/modular_humanoid/parts/`.
- `docs/humanoid_development_plan.md`: roadmap phát triển humanoid.
- `robots/modular_humanoid/README.md`: mô tả robot modular.
