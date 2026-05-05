# Humanoid Robot Development Plan

Tài liệu này là roadmap thực hành để phát triển robot humanoid trong dự án Genesis/MJCF hiện tại. Mục tiêu là đi từ XML skeleton đơn giản đến humanoid có body ổn định, tay/chân điều khiển được, gripper đơn giản, rồi mới tiến tới bàn tay nhiều ngón.

## Mục Tiêu Dài Hạn

Tạo một humanoid robot có thể:

- Load được từ file MJCF/XML trong Genesis.
- Có body tree rõ ràng: pelvis, torso, head, arms, legs, wrist, gripper/hand.
- Có joint và actuator đủ để điều khiển pose, balance, reaching và grasping cơ bản.
- Có cấu trúc XML dễ mở rộng sang mesh thật, sensor, controller và reinforcement learning.

## Nguyên Tắc Phát Triển

- Luôn phát triển theo từng module nhỏ, không thêm toàn bộ humanoid phức tạp cùng lúc.
- Mỗi lần thêm link/joint phải chạy validate XML và simulation ngắn.
- Ưu tiên primitive geometry trước: capsule, box, sphere. Mesh STL/OBJ thêm sau.
- Ưu tiên arm/wrist/reaching trước full hand.
- Full hand phát triển cuối cùng vì contact và DOF rất khó ổn định.
- Mỗi joint cần có tên rõ ràng và actuator tương ứng nếu muốn điều khiển.

## Cấu Trúc Folder Khuyến Nghị

```text
robots/
  basic_humanoid/
    basic_humanoid.xml
    meshes/
    README.md

  my_humanoid_v1/
    my_humanoid_v1.xml
    meshes/
      torso.stl
      pelvis.stl
      thigh_left.stl
      thigh_right.stl
    README.md

src/robotics_genesis/
  controllers/
    sine_pose.py
    stand_pose.py
    reaching.py
  simulation/
    genesis_runner.py

docs/
  robot_xml_guide.md
  humanoid_development_plan.md
```

## XML Skeleton Chuẩn

Humanoid nên có cấu trúc MJCF cơ bản như sau:

```xml
<mujoco model="my_humanoid">
  <compiler angle="radian" inertiafromgeom="true" autolimits="true"/>
  <option timestep="0.01" gravity="0 0 -9.81"/>

  <default>
    <joint damping="1.0" armature="0.02" limited="true"/>
    <geom density="650" friction="1.0 0.1 0.1"/>
    <motor ctrllimited="true" ctrlrange="-1 1"/>
  </default>

  <asset>
    <!-- material, mesh, texture -->
  </asset>

  <worldbody>
    <!-- floor, light, camera -->

    <body name="pelvis" pos="0 0 1.05">
      <freejoint name="root"/>

      <!-- torso -->
      <!-- left arm, right arm -->
      <!-- left leg, right leg -->
    </body>
  </worldbody>

  <actuator>
    <!-- one motor per controllable joint -->
  </actuator>
</mujoco>
```

## Naming Convention

Dùng tên nhất quán để controller dễ map joint:

```text
root
pelvis
torso
head

shoulder_pitch_right
shoulder_roll_right
shoulder_yaw_right
elbow_right
wrist_pitch_right
wrist_yaw_right

hip_pitch_right
hip_roll_right
hip_yaw_right
knee_right
ankle_pitch_right
ankle_roll_right

thumb_1_right
index_1_right
middle_1_right
```

Giai đoạn đầu có thể dùng tên đơn giản hơn:

```text
shoulder_right
elbow_right
hip_right
knee_right
ankle_right
```

Khi robot lớn hơn, nên đổi sang `pitch/roll/yaw` để tránh nhầm axis.

## Phase 0: Setup Và Baseline

Mục tiêu: đảm bảo môi trường chạy được và có robot mẫu để so sánh.

File liên quan:

- `robots/basic_arm/basic_arm.xml`
- `robots/basic_humanoid/basic_humanoid.xml`
- `scripts/validate_xml.py`
- `scripts/run_sim.py`
- `test.py`

Lệnh kiểm tra:

```bash
.venv/bin/python scripts/validate_xml.py robots/basic_humanoid/basic_humanoid.xml --mujoco
ROBOT_XML=robots/basic_humanoid/basic_humanoid.xml STEPS=1 .venv/bin/python test.py
SHOW_VIEWER=1 ROBOT_XML=robots/basic_humanoid/basic_humanoid.xml STEPS=10000 .venv/bin/python test.py
```

Tiêu chí hoàn thành:

- XML pass MuJoCo validation.
- Genesis load được robot.
- Viewer mở được nếu đặt `SHOW_VIEWER=1`.
- Simulation không crash trong 1000 bước.

Practice:

- Đổi màu material trong XML.
- Đổi chiều dài arm/leg một chút.
- Chạy lại validate và viewer.

## Phase 1: Static Body Skeleton

Mục tiêu: tạo humanoid chỉ gồm link cơ bản, chưa cần control đẹp.

Thành phần cần có:

- `pelvis`
- `torso`
- `head`
- `left_upper_arm`, `left_forearm`
- `right_upper_arm`, `right_forearm`
- `left_thigh`, `left_shin`, `left_foot`
- `right_thigh`, `right_shin`, `right_foot`

MJCF cần tập trung:

- Mỗi body có ít nhất một `geom` hoặc `inertial`.
- Dùng `capsule` cho limb.
- Dùng `sphere` cho head/joint marker.
- Dùng `box` cho foot.

Checklist:

- Pelvis ở trên mặt đất, ví dụ `pos="0 0 1.05"`.
- Chân chạm gần mặt đất nhưng không xuyên quá sâu.
- Tay không xuyên torso ở pose ban đầu.
- Foot có kích thước đủ rộng để sau này đứng.

Practice:

- Tạo bản copy:

```bash
mkdir -p robots/my_humanoid_v1/meshes
cp robots/basic_humanoid/basic_humanoid.xml robots/my_humanoid_v1/my_humanoid_v1.xml
```

- Chỉnh chiều cao robot bằng cách tăng/giảm chiều dài `thigh`, `shin`, `torso`.
- Validate:

```bash
.venv/bin/python scripts/validate_xml.py robots/my_humanoid_v1/my_humanoid_v1.xml --mujoco
```

Tiêu chí hoàn thành:

- Body nhìn giống humanoid cơ bản.
- Không lỗi mass/inertia.
- Không có link bị rơi rời khỏi body tree.

## Phase 2: Joint Architecture

Mục tiêu: quyết định robot có bao nhiêu DOF và axis nào.

DOF tối thiểu để test:

```text
torso:
  abdomen_y: 1 DOF

arm each side:
  shoulder: 1 DOF
  elbow: 1 DOF

leg each side:
  hip: 1 DOF
  knee: 1 DOF
  ankle: 1 DOF
```

DOF tốt hơn cho humanoid:

```text
torso:
  abdomen_pitch
  abdomen_roll
  abdomen_yaw

arm each side:
  shoulder_pitch
  shoulder_roll
  shoulder_yaw
  elbow
  wrist_pitch
  wrist_yaw

leg each side:
  hip_pitch
  hip_roll
  hip_yaw
  knee
  ankle_pitch
  ankle_roll
```

MJCF joint example:

```xml
<joint name="hip_pitch_right" type="hinge" axis="0 1 0" range="-1.2 1.0"/>
<joint name="hip_roll_right" type="hinge" axis="1 0 0" range="-0.5 0.5"/>
<joint name="hip_yaw_right" type="hinge" axis="0 0 1" range="-0.8 0.8"/>
```

Practice:

- Bắt đầu với 1 DOF mỗi khớp.
- Khi chạy ổn, tách shoulder thành 2 hoặc 3 DOF.
- Khi chạy ổn, tách hip thành 2 hoặc 3 DOF.

Tiêu chí hoàn thành:

- `scripts/validate_xml.py` liệt kê đúng số joint.
- Controller có thể set target cho từng joint theo tên.
- Joint range không làm link xuyên nhau quá nhiều ở neutral pose.

## Phase 3: Actuator Và Control Surface

Mục tiêu: mọi joint quan trọng đều có actuator.

Quy tắc:

- Một joint điều khiển được cần một `<motor>`.
- Gear lớn hơn cho hip/knee, nhỏ hơn cho wrist/finger.
- Giữ `ctrlrange="-1 1"` ở giai đoạn đầu để tránh lực quá lớn.

Ví dụ:

```xml
<actuator>
  <motor name="hip_pitch_right_motor" joint="hip_pitch_right" gear="90"/>
  <motor name="knee_right_motor" joint="knee_right" gear="90"/>
  <motor name="ankle_pitch_right_motor" joint="ankle_pitch_right" gear="60"/>
</actuator>
```

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

Practice:

- Thêm motor cho toàn bộ joint.
- Chạy sine controller rất nhỏ, ví dụ amplitude `0.05`.
- Tăng dần amplitude khi robot không bị nổ simulation.

Tiêu chí hoàn thành:

- Không có joint quan trọng bị thiếu actuator.
- Simulation không bị rung mạnh khi set target.
- Có thể tạo pose đứng yên bằng target cố định.

## Phase 4: Inertia, Mass Và Collision

Mục tiêu: robot có khối lượng và va chạm hợp lý.

Các lỗi thường gặp:

- Body có joint nhưng không có `geom` hoặc `inertial`.
- Capsule/box quá nhỏ làm contact không ổn định.
- Limb xuyên nhau ở neutral pose.
- Foot quá nhỏ khiến robot dễ ngã.

Practice:

- Dùng `density` thống nhất trước.
- Nếu body trung gian không có geom, thêm:

```xml
<inertial pos="0 0 0" mass="0.02" diaginertia="0.0001 0.0001 0.0001"/>
```

- Tách visual geom và collision geom sau này nếu cần.

Tiêu chí hoàn thành:

- MuJoCo không báo lỗi mass/inertia.
- Genesis không crash khi build scene.
- Warning self-collision giảm dần khi chỉnh pose ban đầu.

## Phase 5: Standing Pose

Mục tiêu: tạo pose đứng yên trước khi nghĩ tới bước đi.

Thành phần code nên thêm sau:

```text
src/robotics_genesis/controllers/stand_pose.py
```

Pose ban đầu gợi ý:

```text
abdomen_y: 0.0
hip_right: 0.05
knee_right: -0.15
ankle_right: 0.05
hip_left: 0.05
knee_left: -0.15
ankle_left: 0.05
shoulder_right: 0.15
elbow_right: -0.35
shoulder_left: 0.15
elbow_left: -0.35
```

Practice:

- Tắt sine motion.
- Set target cố định.
- Chạy 1000 bước.
- Quan sát robot có ngã ngay không.

Tiêu chí hoàn thành:

- Robot giữ pose ít nhất vài giây simulation.
- Foot contact ổn định.
- Joint không giật liên tục.

## Phase 6: Arm Reaching

Mục tiêu: phát triển tay trước bàn tay.

Thứ tự:

1. Shoulder 1 DOF.
2. Elbow 1 DOF.
3. Shoulder 2-3 DOF.
4. Wrist 2 DOF.
5. End-effector marker.

XML wrist gợi ý:

```xml
<body name="right_wrist" pos="0 -0.24 0">
  <joint name="wrist_pitch_right" type="hinge" axis="0 1 0" range="-0.8 0.8"/>
  <joint name="wrist_yaw_right" type="hinge" axis="0 0 1" range="-0.8 0.8"/>
  <geom name="right_wrist_geom" type="sphere" size="0.035" material="joint_mat"/>
</body>
```

Practice:

- Tạo target pose cho arm.
- Điều khiển shoulder/elbow/wrist bằng sine nhỏ.
- Kiểm tra tay có với được vùng phía trước torso không.

Tiêu chí hoàn thành:

- End-effector tới được trước mặt robot.
- Tay không xuyên torso quá nhiều.
- Joint limit hợp lý.

## Phase 7: Simple Gripper

Mục tiêu: thêm gripper 2 ngón trước khi làm bàn tay 5 ngón.

XML structure:

```xml
<body name="right_gripper" pos="0 -0.04 0">
  <body name="right_gripper_finger_a" pos="0 -0.03 0">
    <joint name="gripper_a_right" type="hinge" axis="0 0 1" range="-0.6 0.2"/>
    <geom type="box" size="0.015 0.05 0.02"/>
  </body>

  <body name="right_gripper_finger_b" pos="0 0.03 0">
    <joint name="gripper_b_right" type="hinge" axis="0 0 1" range="-0.2 0.6"/>
    <geom type="box" size="0.015 0.05 0.02"/>
  </body>
</body>
```

Practice:

- Đặt một cube trước robot.
- Mở/đóng gripper bằng target position.
- Chỉ test với arm cố định trước.

Tiêu chí hoàn thành:

- Gripper đóng/mở ổn.
- Contact không làm simulation nổ.
- Có thể giữ một object đơn giản trong vài bước.

## Phase 8: Full Hand

Mục tiêu: chỉ bắt đầu khi arm, wrist và simple gripper đã ổn.

Cấu trúc hand tối thiểu:

```text
right_hand
  right_palm
  thumb_1_right
  thumb_2_right
  index_1_right
  index_2_right
  middle_1_right
  middle_2_right
```

Cấu trúc hand đầy đủ hơn:

```text
thumb: 3 joints
index: 3 joints
middle: 3 joints
ring: 3 joints
pinky: 3 joints
wrist: 2-3 joints
```

Khuyến nghị:

- Không làm 5 ngón ngay.
- Bắt đầu với thumb + index.
- Sau đó thêm middle.
- Coupling joint finger bằng controller trước, tendon sau.

Practice:

- Test từng ngón một.
- Không dùng object phức tạp lúc đầu.
- Dùng sphere hoặc box nhỏ.
- Giảm gear finger.
- Giảm joint range nếu contact không ổn.

Tiêu chí hoàn thành:

- Finger không xuyên palm ở neutral pose.
- Có thể đóng/mở từng ngón.
- Contact với object không tạo jitter quá lớn.

## Phase 9: Sensors Và Observations

Mục tiêu: chuẩn bị dữ liệu cho control/RL.

Sensor nên thêm sau:

```text
joint position
joint velocity
body orientation
pelvis height
foot contact
hand contact
end-effector pose
object pose
```

MJCF sensor example:

```xml
<sensor>
  <jointpos name="knee_right_pos" joint="knee_right"/>
  <jointvel name="knee_right_vel" joint="knee_right"/>
</sensor>
```

Practice:

- Bắt đầu với joint pos/vel.
- Thêm contact sensor sau khi collision ổn.
- Log observation vào `outputs/logs/`.

Tiêu chí hoàn thành:

- Có observation vector ổn định.
- Không có NaN.
- Observation shape cố định giữa các episode.

## Phase 10: Locomotion

Mục tiêu: đi bộ chỉ sau khi standing pose ổn.

Thứ tự:

1. Giữ thăng bằng tại chỗ.
2. Dịch trọng tâm trái/phải.
3. Nhấc một chân rất thấp.
4. Step tại chỗ.
5. Walk forward chậm.
6. Walk với disturbance.

Practice:

- Không thêm hand trong giai đoạn locomotion đầu.
- Lock arm hoặc để arm pose cố định.
- Tập trung foot contact và pelvis height.

Metrics:

```text
pelvis_height
pelvis_roll
pelvis_pitch
foot_contact_left
foot_contact_right
forward_velocity
energy_cost
fall_count
```

Tiêu chí hoàn thành:

- Robot không ngã trong thời gian mục tiêu.
- Foot contact luân phiên có kiểm soát.
- Pelvis không dao động quá lớn.

## Phase 11: Manipulation

Mục tiêu: reaching và grasping.

Thứ tự:

1. Arm reaching với base cố định.
2. Wrist orientation control.
3. Simple gripper close/open.
4. Pick object với gripper.
5. Place object.
6. Full hand grasp.

Practice:

- Dùng object đơn giản: cube, sphere, cylinder.
- Đặt object trong workspace dễ với.
- Không kết hợp walking và grasping ngay.

Metrics:

```text
end_effector_distance_to_target
object_lift_height
grasp_success
object_slip
contact_count
joint_limit_violation
```

Tiêu chí hoàn thành:

- End-effector tới target ổn.
- Gripper giữ object trong vài giây simulation.
- Object không bị bắn đi do contact quá mạnh.

## Phase 12: Mesh Và Visual Upgrade

Mục tiêu: thay primitive shape bằng mesh đẹp hơn nhưng không phá simulation.

Quy tắc:

- Giữ collision primitive trước.
- Dùng mesh cho visual sau.
- Mesh nên scale đúng đơn vị mét.
- Mesh nên đặt trong `robots/<robot_name>/meshes/`.

Example asset:

```xml
<asset>
  <mesh name="torso_mesh" file="meshes/torso.stl"/>
</asset>
```

Example geom:

```xml
<geom name="torso_visual" type="mesh" mesh="torso_mesh" contype="0" conaffinity="0"/>
<geom name="torso_collision" type="capsule" fromto="0 0 0 0 0 0.42" size="0.11"/>
```

Practice:

- Thay visual của torso trước.
- Sau đó tới pelvis, arms, legs.
- Không thay toàn bộ collision bằng mesh ngay.

Tiêu chí hoàn thành:

- Visual đẹp hơn nhưng simulation vẫn ổn.
- Contact không phụ thuộc mesh phức tạp.
- File XML vẫn validate được.

## Debug Checklist

Khi simulation lỗi hoặc robot hành xử lạ:

- Chạy `scripts/validate_xml.py --mujoco`.
- Giảm `STEPS=1` để test load.
- Tắt viewer để xem lỗi nhanh hơn.
- Kiểm tra body có `geom` hoặc `inertial`.
- Kiểm tra joint axis có đúng không.
- Kiểm tra joint range có quá rộng không.
- Kiểm tra actuator gear có quá lớn không.
- Kiểm tra limb có xuyên nhau ở neutral pose không.
- Kiểm tra foot có nằm dưới mặt đất không.

Lệnh debug nhanh:

```bash
.venv/bin/python scripts/validate_xml.py robots/basic_humanoid/basic_humanoid.xml --mujoco
ROBOT_XML=robots/basic_humanoid/basic_humanoid.xml STEPS=1 .venv/bin/python test.py
SHOW_VIEWER=1 ROBOT_XML=robots/basic_humanoid/basic_humanoid.xml STEPS=10000 .venv/bin/python test.py
```

## Roadmap Thực Hành Đề Xuất

### Week 1: XML Và Body Tree

- Đọc `docs/robot_xml_guide.md`.
- Chạy `basic_arm`.
- Chạy `basic_humanoid`.
- Copy `basic_humanoid` thành robot riêng.
- Chỉnh kích thước torso, arm, leg.
- Validate XML sau mỗi lần chỉnh.

Deliverable:

- `robots/my_humanoid_v1/my_humanoid_v1.xml`
- Robot load được trong viewer.

### Week 2: Joint Và Actuator

- Đổi tên joint theo `pitch/roll/yaw` nếu cần.
- Thêm actuator cho toàn bộ joint.
- Tạo pose đứng cơ bản.
- Giảm self-collision ở neutral pose.

Deliverable:

- Robot có thể giữ pose cố định.
- Controller map joint theo tên.

### Week 3: Arm Và Wrist

- Tách shoulder thành 2 hoặc 3 DOF.
- Thêm wrist 2 DOF.
- Thêm end-effector marker.
- Test reaching đơn giản.

Deliverable:

- Tay phải/tay trái đưa tới target phía trước.

### Week 4: Gripper Đơn Giản

- Thêm gripper 2 ngón.
- Thêm actuator cho gripper.
- Test mở/đóng.
- Test contact với cube.

Deliverable:

- Gripper có thể đóng quanh object đơn giản.

### Week 5: Balance Và Locomotion Cơ Bản

- Tạo standing controller.
- Test pelvis height.
- Test dịch trọng tâm.
- Test nhấc chân thấp.

Deliverable:

- Robot đứng ổn hơn và có bước chuẩn bị cho walking.

### Week 6+: Full Hand Và Manipulation

- Thêm thumb + index.
- Thêm middle finger.
- Test grasp object đơn giản.
- Tối ưu contact/friction.
- Sau đó mới mở rộng 5 ngón.

Deliverable:

- Hand module riêng có thể gắn vào wrist.

## Thứ Tự Ưu Tiên Kỹ Thuật

Ưu tiên cao:

- XML load ổn.
- Body tree đúng.
- Inertia/mass hợp lý.
- Joint names nhất quán.
- Actuator đầy đủ.
- Standing pose ổn.

Ưu tiên trung bình:

- Arm reaching.
- Wrist.
- Simple gripper.
- Sensor/logging.

Ưu tiên sau:

- Full hand.
- Mesh đẹp.
- RL phức tạp.
- Bimanual manipulation.

## Definition Of Done Cho Một Phiên Bản Humanoid

Một version humanoid được coi là ổn để tiếp tục phát triển khi:

- Pass:

```bash
.venv/bin/python scripts/validate_xml.py robots/<robot_name>/<robot_name>.xml --mujoco
```

- Chạy được:

```bash
ROBOT_XML=robots/<robot_name>/<robot_name>.xml STEPS=1000 .venv/bin/python test.py
```

- Mở viewer được:

```bash
SHOW_VIEWER=1 ROBOT_XML=robots/<robot_name>/<robot_name>.xml STEPS=10000 .venv/bin/python test.py
```

- Joint list đúng với thiết kế.
- Không có body thiếu mass/inertia.
- Không crash khi build scene.
- Không có link rời hoặc bay mất ngay khi start.
- Controller có thể điều khiển joint bằng tên.

## Gợi Ý Bước Tiếp Theo Trong Repo Này

1. Copy `robots/basic_humanoid/basic_humanoid.xml` thành `robots/my_humanoid_v1/my_humanoid_v1.xml`.
2. Đổi joint naming sang `pitch/roll/yaw` cho shoulder và hip.
3. Viết `src/robotics_genesis/controllers/stand_pose.py`.
4. Thêm wrist vào XML.
5. Thêm simple gripper 2 ngón.
6. Sau khi gripper ổn, mới thiết kế bàn tay nhiều ngón.
