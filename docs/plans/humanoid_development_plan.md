# Modular Humanoid Development Plan

Roadmap này chỉ dùng cho robot chính tại `robots/modular_humanoid/`.

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
    right_hand.xml
    left_hand.xml
    right_leg.xml
    left_leg.xml
    actuators.xml
  meshes/
```

Robot hiện tại có 45 actuated hinge joints:

- Torso 3 DOF: `abdomen_yaw`, `abdomen_roll`, `abdomen_pitch`.
- Neck 2 DOF: `neck_yaw`, `neck_pitch`.
- Mỗi tay 13 DOF: shoulder yaw/roll/pitch, forearm yaw, elbow pitch, wrist yaw/pitch, thumb/index/middle fingers.
- Mỗi chân 7 DOF: hip yaw/roll/pitch, knee pitch, ankle roll/pitch, toe pitch.

## Luồng Làm Việc

1. Sửa một bộ phận trong `parts/`.
2. Validate XML.
3. Chạy simulation 1 bước.
4. Mở viewer kiểm tra hình học và chuyển động.
5. Chỉ khi phase hiện tại ổn mới thêm DOF hoặc bộ phận mới.

Lệnh chuẩn:

```bash
.venv/bin/python scripts/validate_xml.py robots/modular_humanoid/modular_humanoid.xml --mujoco
ROBOT_XML=robots/modular_humanoid/modular_humanoid.xml STEPS=1 .venv/bin/python test.py
SHOW_VIEWER=1 ROBOT_XML=robots/modular_humanoid/modular_humanoid.xml STEPS=10000 .venv/bin/python test.py
```

## Phase 1: Body Tree

Mục tiêu: giữ cấu trúc pelvis, torso, head, arms, legs rõ ràng.

File chính:

- `parts/body.xml`
- `parts/torso.xml`
- `parts/right_arm.xml`
- `parts/left_arm.xml`
- `parts/right_leg.xml`
- `parts/left_leg.xml`

Checklist:

- Mỗi body chuyển động có `geom` hoặc `inertial`.
- Link không rời khỏi body tree.
- Neutral pose không xuyên nhau quá nhiều.
- Foot gần mặt đất và đủ rộng để đứng.

## Phase 2: Joint Naming

Tên joint nên theo hướng `pitch/roll/yaw`:

```text
abdomen_pitch
abdomen_roll
abdomen_yaw
shoulder_pitch_right
shoulder_roll_right
shoulder_yaw_right
elbow_pitch_right
wrist_pitch_right
hip_pitch_right
knee_pitch_right
ankle_pitch_right
```

Khi đổi tên joint, cập nhật:

- `parts/actuators.xml`
- `src/robotics_genesis/controllers/sine_pose.py`
- `tests/test_project_structure.py`

## Phase 3: Actuators

Mỗi joint điều khiển được cần một motor trong `parts/actuators.xml`.

Gợi ý gear ban đầu:

```text
torso: 80
hip: 80-120
knee: 80-120
ankle: 50-80
shoulder: 40-70
elbow: 30-60
wrist: 15-35
finger: 3-15
```

## Phase 4: Standing Pose

Mục tiêu: robot giữ pose ổn định trước khi làm walking.

Việc cần làm:

- Tạo controller pose đứng riêng.
- Giữ arm ở pose cố định.
- Giảm amplitude của sine motion khi debug balance.
- Theo dõi pelvis height và foot contact.

## Phase 5: Arm Và Wrist

Mục tiêu: tay đưa được tới vùng phía trước torso.

Thứ tự:

1. Shoulder yaw/roll/pitch.
2. Elbow pitch.
3. Forearm yaw.
4. Wrist yaw/pitch.
5. Hand hoặc end-effector marker.

## Phase 6: Simple Gripper

Robot hiện đã có hand đơn giản với thumb, index và middle finger. Nếu muốn grasping ổn định hơn, có thể thêm gripper 2 ngón hoặc tendon/coupling trước khi mở rộng thành full hand 5 ngón.

File hiện tại:

```text
parts/right_hand.xml
parts/left_hand.xml
```

Hai file này đang được include vào wrist trong `right_arm.xml` và `left_arm.xml`.

## Phase 7: Full Hand

Chỉ làm full hand khi arm, wrist và gripper đơn giản đã ổn.

Thứ tự:

1. Palm.
2. Thumb + index.
3. Middle finger.
4. Ring + pinky.
5. Tendon/coupling nếu cần.

## Phase 8: Mesh Upgrade

Dùng mesh cho visual, giữ primitive geom cho collision.

```xml
<geom name="torso_visual" type="mesh" mesh="torso_mesh" contype="0" conaffinity="0"/>
<geom name="torso_collision" type="capsule" fromto="0 0 0 0 0 0.42" size="0.11"/>
```

## Definition Of Done

Một thay đổi được coi là ổn khi pass:

```bash
.venv/bin/python scripts/validate_xml.py robots/modular_humanoid/modular_humanoid.xml --mujoco
.venv/bin/python scripts/run_sim.py --steps 1
```

Và khi cần kiểm tra bằng mắt:

```bash
SHOW_VIEWER=1 .venv/bin/python scripts/run_sim.py --steps 10000
```
