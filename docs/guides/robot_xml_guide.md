# Hướng Dẫn Thiết Kế Robot Bằng XML/MJCF

File robot chính hiện tại là `robots/modular_humanoid/modular_humanoid.xml`.

## Thành Phần Quan Trọng

- `<worldbody>` chứa cây body/link của robot và môi trường.
- `<body>` đại diện cho một link hoặc cụm link.
- `<joint>` định nghĩa bậc tự do giữa body cha và body con.
- `<geom>` định nghĩa hình dạng va chạm và hình ảnh đơn giản.
- `<asset>` khai báo mesh, texture, material.
- `<actuator>` khai báo motor điều khiển joint.

## Quy Ước Dự Án

- Joint nên có tên rõ ràng: `shoulder_pitch_right`, `elbow_pitch_left`, `hip_pitch_left`.
- Mesh nên để cạnh robot trong `robots/modular_humanoid/meshes/`.
- XML nên chạy được bằng `scripts/validate_xml.py` trước khi đưa vào simulation.
- Nếu robot có base tự do, dùng `<freejoint name="root"/>` ở body gốc.

## Ví Dụ Workflow

```bash
python scripts/validate_xml.py robots/modular_humanoid/modular_humanoid.xml --mujoco
python scripts/run_sim.py --robot robots/modular_humanoid/modular_humanoid.xml --steps 300
```

Khi đổi tên joint trong XML, cập nhật controller tương ứng trong `src/robotics_genesis/controllers/sine_pose.py`.

## Chia Robot Thành Nhiều File XML

Khi humanoid bắt đầu lớn, nên tách từng bộ phận bằng MJCF `<include>`:

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
    right_hand.xml
    left_hand.xml
    right_leg.xml
    left_leg.xml
    actuators.xml
  meshes/
```

File chính chỉ ráp các phần:

```xml
<mujoco model="modular_humanoid">
  <asset>
    <include file="parts/assets.xml"/>
  </asset>

  <worldbody>
    <include file="parts/scene.xml"/>
    <include file="parts/body.xml"/>
  </worldbody>

  <actuator>
    <include file="parts/actuators.xml"/>
  </actuator>
</mujoco>
```

Mỗi file trong `parts/` dùng root `<mujoco>` làm wrapper, còn nội dung bên trong là snippet cần include.
