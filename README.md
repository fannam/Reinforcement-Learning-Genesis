# Robotics Genesis Starter

Bộ khung này dùng cho dự án robotics tự thiết kế robot bằng file XML/MJCF và chạy mô phỏng bằng Genesis.

## Cấu Trúc Chính

```text
assets/                 Mesh, texture, material dùng chung
configs/                Tham số robot và simulation
docs/                   Ghi chú thiết kế robot XML
outputs/                Log, video, checkpoint sinh ra khi chạy
robots/                 Mỗi robot nằm trong một thư mục riêng
scripts/                Script CLI để validate XML và chạy mô phỏng
src/robotics_genesis/   Code Python dùng lại được
tests/                  Test cấu trúc và XML
xml/                    Khu vực XML thử nghiệm hoặc legacy
```

Robot mẫu nằm ở `robots/starter_humanoid/starter_humanoid.xml`.

## Chạy Nhanh

```bash
source .venv/bin/activate
python scripts/validate_xml.py robots/starter_humanoid/starter_humanoid.xml
python scripts/run_sim.py --robot robots/starter_humanoid/starter_humanoid.xml --steps 300
```

Mở viewer:

```bash
SHOW_VIEWER=1 python scripts/run_sim.py --robot robots/starter_humanoid/starter_humanoid.xml
```

Chọn backend:

```bash
GENESIS_BACKEND=gpu python scripts/run_sim.py
GENESIS_BACKEND=cpu python scripts/run_sim.py
```

## Quy Trình Thiết Kế Robot XML

1. Tạo thư mục mới trong `robots/<ten_robot>/`.
2. Đặt file MJCF chính là `robots/<ten_robot>/<ten_robot>.xml`.
3. Đặt mesh riêng của robot vào `robots/<ten_robot>/meshes/`.
4. Chạy `python scripts/validate_xml.py robots/<ten_robot>/<ten_robot>.xml`.
5. Chạy mô phỏng với `python scripts/run_sim.py --robot robots/<ten_robot>/<ten_robot>.xml`.

Nếu cần điều khiển joint theo tên, sửa `src/robotics_genesis/controllers/sine_pose.py`.
# Reinforcement-Learning-Genesis
