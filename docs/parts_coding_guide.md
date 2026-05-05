# Parts Coding Guide

Tài liệu này hướng dẫn cách code các file XML trong `robots/modular_humanoid/parts/`. Mục tiêu là giúp bạn thêm/sửa từng bộ phận của humanoid mà không làm vỡ cấu trúc MJCF chính.

## Nguyên Tắc Tổng Quát

Robot chính nằm ở:

```text
robots/modular_humanoid/modular_humanoid.xml
```

Các bộ phận nằm ở:

```text
robots/modular_humanoid/parts/
```

Mỗi part file hiện dùng root `<mujoco>` làm wrapper:

```xml
<mujoco>
  <!-- snippet được include vào file chính -->
</mujoco>
```

Quy tắc quan trọng:

- Tên `body`, `joint`, `geom`, `motor`, `material`, `mesh` phải unique trong toàn robot.
- Nếu thêm joint mới, phải thêm motor tương ứng trong `parts/actuators.xml`.
- Nếu đổi tên joint, phải cập nhật controller trong `src/robotics_genesis/controllers/sine_pose.py`.
- Nếu thêm material hoặc mesh, khai báo trong `parts/assets.xml`.
- Nếu thêm part mới, include nó từ đúng body cha.
- Luôn validate XML sau mỗi thay đổi nhỏ.

Lệnh validate:

```bash
.venv/bin/python scripts/validate_xml.py robots/modular_humanoid/modular_humanoid.xml --mujoco
```

Lệnh chạy nhanh:

```bash
.venv/bin/python scripts/run_sim.py --steps 1
```

Lệnh mở viewer:

```bash
SHOW_VIEWER=1 .venv/bin/python scripts/run_sim.py --steps 10000
```

## Hệ Trục Và Đơn Vị

MJCF dùng đơn vị SI:

```text
length: meter
mass: kg
angle: radian
```

Quy ước hướng trong robot hiện tại:

```text
X: trước/sau
Y: trái/phải
Z: lên/xuống
```

Trong robot hiện tại:

- `pelvis` bắt đầu ở `pos="0 0 1.05"`.
- Tay phải nằm phía `Y âm`.
- Tay trái nằm phía `Y dương`.
- Chân kéo xuống theo `Z âm`.
- Foot kéo về phía trước theo `X dương`.

Axis joint thường dùng:

```text
axis="0 1 0"  pitch
axis="1 0 0"  roll
axis="0 0 1"  yaw
```

## Giải Thích Các Trường Và Con Số

Phần này giải thích các thuộc tính xuất hiện nhiều nhất trong các file `parts/*.xml`.

### `name`

Ví dụ:

```xml
<body name="right_upper_arm" pos="0 -0.18 0.34">
```

`name` là định danh của object trong MJCF. Nó nên unique trong toàn robot.

Quy ước nên dùng:

```text
<bộ_phận>_<bên>
right_upper_arm
left_foot
shoulder_pitch_right
ankle_pitch_left
```

Nếu đổi `name` của joint, phải đổi luôn trong:

- `parts/actuators.xml`
- `src/robotics_genesis/controllers/sine_pose.py`
- `tests/test_project_structure.py`

### `pos`

Ví dụ:

```xml
<body name="pelvis" pos="0 0 1.05">
```

`pos="x y z"` là vị trí tương đối so với body cha, đơn vị mét.

Ý nghĩa:

```text
x = vị trí theo trục X
y = vị trí theo trục Y
z = vị trí theo trục Z
```

Ví dụ `pos="0 0 1.05"` nghĩa là pelvis nằm cao 1.05 m so với world origin.

Ví dụ:

```xml
<body name="right_upper_arm" pos="0 -0.18 0.34">
```

Ý nghĩa:

```text
x = 0       không dịch trước/sau so với torso
y = -0.18   dịch sang phải 0.18 m
z = 0.34    dịch lên 0.34 m từ torso
```

Vì tay phải nằm phía `Y âm`, nên `right_upper_arm` dùng `-0.18`. Tay trái dùng `+0.18`.

### `type`

`type` mô tả kiểu của joint hoặc geom.

Geom types đang dùng:

```xml
<geom type="capsule"/>
<geom type="sphere"/>
<geom type="box"/>
<geom type="plane"/>
```

Ý nghĩa:

```text
capsule: hình con nhộng, tốt cho tay/chân
sphere: hình cầu, tốt cho đầu hoặc joint marker
box: hình hộp, tốt cho foot/palm
plane: mặt phẳng vô hạn/tương đối lớn, tốt cho floor
mesh: mesh STL/OBJ, thường dùng cho visual
```

Joint types hay dùng:

```xml
<joint type="hinge"/>
<joint type="slide"/>
```

Ý nghĩa:

```text
hinge: khớp quay 1 trục
slide: khớp tịnh tiến 1 trục
```

Humanoid hiện tại chủ yếu dùng `hinge`.

### `fromto`

Ví dụ:

```xml
<geom name="right_thigh_geom" type="capsule" fromto="0 0 0 0 0 -0.42" size="0.055"/>
```

`fromto="x1 y1 z1 x2 y2 z2"` định nghĩa hai đầu của capsule trong local frame của body.

Ý nghĩa ví dụ:

```text
đầu 1: (0, 0, 0)
đầu 2: (0, 0, -0.42)
```

Tức là capsule dài 0.42 m, kéo xuống theo trục `Z âm`.

Ví dụ tay phải:

```xml
<geom name="right_upper_arm_geom" type="capsule" fromto="0 0 0 0 -0.26 0" size="0.04"/>
```

Ý nghĩa:

```text
đầu 1: (0, 0, 0)
đầu 2: (0, -0.26, 0)
```

Tức là upper arm dài 0.26 m, kéo sang phía `Y âm`.

### `size`

Ý nghĩa của `size` phụ thuộc vào `type`.

Capsule:

```xml
<geom type="capsule" fromto="0 0 0 0 0 -0.42" size="0.055"/>
```

`size="0.055"` là bán kính capsule, tức radius 5.5 cm.

Sphere:

```xml
<geom type="sphere" size="0.11"/>
```

`size="0.11"` là bán kính sphere, tức radius 11 cm.

Box:

```xml
<geom type="box" size="0.16 0.06 0.035"/>
```

Với box, `size="x_half y_half z_half"` là nửa kích thước theo từng trục, không phải full size.

Ví dụ:

```text
size="0.16 0.06 0.035"
full X = 0.32 m
full Y = 0.12 m
full Z = 0.07 m
```

Plane:

```xml
<geom type="plane" size="4 4 0.05"/>
```

Với plane, hai số đầu thường dùng làm kích thước hiển thị theo X/Y; số thứ ba liên quan độ dày/visual convention.

### `axis`

Ví dụ:

```xml
<joint name="hip_pitch_right" type="hinge" axis="0 1 0"/>
```

`axis="x y z"` là trục quay của joint hinge trong local frame.

Các axis thường dùng:

```text
axis="0 1 0"  quay quanh Y, thường dùng cho pitch
axis="1 0 0"  quay quanh X, thường dùng cho roll
axis="0 0 1"  quay quanh Z, thường dùng cho yaw
```

Ví dụ:

```xml
<joint name="elbow_pitch_right" type="hinge" axis="0 1 0" range="-1.7 0.1"/>
```

Elbow quay quanh trục Y. Nếu khi mở viewer thấy joint quay sai hướng, thường cần đổi `axis` hoặc đổi dấu trong `range`/controller.

### `range`

Ví dụ:

```xml
<joint name="knee_pitch_right" type="hinge" axis="0 1 0" range="-1.8 0.05"/>
```

`range="min max"` là giới hạn joint theo radian.

Một vài mốc radian:

```text
0.1 rad  ≈ 5.7 độ
0.5 rad  ≈ 28.6 độ
0.8 rad  ≈ 45.8 độ
1.0 rad  ≈ 57.3 độ
1.57 rad ≈ 90 độ
1.8 rad  ≈ 103 độ
```

Ví dụ `range="-1.8 0.05"` nghĩa là joint có thể quay từ khoảng `-103 độ` tới `+2.9 độ`.

Gợi ý:

- Nếu joint bị gập quá mạnh, thu hẹp `range`.
- Nếu controller target vượt range, simulator sẽ clamp hoặc tạo lực lớn tùy actuator/control.
- Khi mới test robot, nên dùng range nhỏ trước.

### `rgba`

Ví dụ:

```xml
<material name="limb_mat" rgba="0.18 0.42 0.78 1"/>
```

`rgba="r g b a"` định nghĩa màu:

```text
r = red   từ 0 tới 1
g = green từ 0 tới 1
b = blue  từ 0 tới 1
a = alpha/opacity từ 0 tới 1
```

Ví dụ:

```text
0.18 0.42 0.78 1
ít đỏ, xanh lá vừa, xanh dương cao, không trong suốt
```

### `material`

Ví dụ:

```xml
<geom name="torso_geom" material="limb_mat"/>
```

`material` trỏ tới một material đã khai báo trong `assets.xml`.

Nếu material không tồn tại, XML sẽ lỗi khi load.

### `density`

Ví dụ trong `modular_humanoid.xml`:

```xml
<geom density="650" friction="1.0 0.1 0.1"/>
```

`density` là mật độ khối lượng của geom, đơn vị kg/m^3. MuJoCo dùng density và kích thước geom để tính mass/inertia khi `inertiafromgeom="true"`.

Gợi ý:

- Tăng density làm link nặng hơn.
- Giảm density làm link nhẹ hơn.
- Link quá nhẹ có thể dễ rung.
- Link quá nặng cần actuator gear lớn hơn.

### `friction`

Ví dụ:

```xml
<geom friction="1.0 0.1 0.1"/>
```

Trong MuJoCo, friction thường gồm 3 giá trị:

```text
sliding friction
torsional friction
rolling friction
```

Với foot/floor:

- Sliding friction cao giúp ít trượt hơn.
- Friction quá cao đôi khi làm contact khó ổn định.

Ở giai đoạn đầu, giữ mặc định `1.0 0.1 0.1` là hợp lý.

### `damping`

Ví dụ:

```xml
<joint damping="1.0" armature="0.02" limited="true"/>
```

`damping` là lực cản vận tốc joint.

Ý nghĩa:

- Damping cao hơn giúp joint bớt rung.
- Damping quá cao làm chuyển động ì.
- Damping quá thấp dễ dao động.

### `armature`

Ví dụ:

```xml
<joint armature="0.02"/>
```

`armature` thêm quán tính rotor/khớp vào DOF. Nó thường giúp simulation ổn định hơn với joint được motor điều khiển.

Gợi ý:

- Giá trị nhỏ như `0.01` tới `0.05` thường dùng để ổn định.
- Quá lớn làm joint phản ứng chậm.

### `limited`

Ví dụ:

```xml
<joint limited="true" range="-0.8 0.8"/>
```

`limited="true"` bật giới hạn joint theo `range`.

Nếu không bật limit, `range` có thể không được áp dụng cho một số cấu hình.

### `gear`

Ví dụ:

```xml
<motor name="knee_pitch_right_motor" joint="knee_pitch_right" gear="85"/>
```

`gear` là hệ số khuếch đại actuator. Với motor, gear lớn hơn nghĩa là motor có ảnh hưởng mạnh hơn lên joint.

Gợi ý:

```text
hip/knee: 80-120
ankle: 50-80
shoulder: 40-70
elbow: 30-60
wrist: 15-35
finger: 3-15
```

Nếu robot giật mạnh:

- Giảm `gear`.
- Giảm target amplitude.
- Tăng damping.

Nếu joint không đủ lực:

- Tăng `gear` từ từ.
- Không tăng quá mạnh ngay một lần.

### `ctrlrange` Và `ctrllimited`

Ví dụ trong default:

```xml
<motor ctrllimited="true" ctrlrange="-1 1"/>
```

`ctrlrange="-1 1"` giới hạn input control của motor trong khoảng từ `-1` tới `1`.

`ctrllimited="true"` bật giới hạn đó.

Với project hiện tại, Python controller đang dùng position control của Genesis (`control_dofs_position`), nhưng motor vẫn nên có range hợp lý để MJCF rõ ràng và dễ mở rộng.

### `mass` Và `diaginertia`

Ví dụ:

```xml
<inertial pos="0 0 0" mass="0.02" diaginertia="0.0001 0.0001 0.0001"/>
```

`mass` là khối lượng body, đơn vị kg.

`diaginertia="ix iy iz"` là quán tính quay quanh ba trục chính.

Khi dùng:

- Dùng cho body trung gian có joint nhưng không có geom.
- Giá trị nhỏ giúp MuJoCo không báo lỗi body không có mass/inertia.
- Không nên lạm dụng để thay cho mass thật của link chính.

### `contype` Và `conaffinity`

Ví dụ:

```xml
<geom name="torso_visual" type="mesh" mesh="torso_mesh" contype="0" conaffinity="0"/>
```

`contype` và `conaffinity` điều khiển collision filtering.

Khi đặt cả hai bằng `0`, geom thường chỉ còn là visual, không tham gia collision.

Dùng pattern này cho mesh visual:

```xml
<geom name="torso_visual" type="mesh" mesh="torso_mesh" contype="0" conaffinity="0"/>
<geom name="torso_collision" type="capsule" fromto="0 0 0 0 0 0.42" size="0.11"/>
```

### `timestep`

Ví dụ trong file chính:

```xml
<option timestep="0.01" gravity="0 0 -9.81" integrator="RK4"/>
```

`timestep="0.01"` nghĩa là mỗi bước simulation là 0.01 giây, tức 100 Hz.

Nếu simulation không ổn định:

- Có thể giảm timestep, ví dụ `0.005`.
- Đổi timestep có thể làm simulation chậm hơn nhưng ổn định hơn.

### `gravity`

Ví dụ:

```xml
gravity="0 0 -9.81"
```

Ý nghĩa:

```text
X gravity = 0
Y gravity = 0
Z gravity = -9.81 m/s^2
```

Tức là trọng lực kéo xuống theo `Z âm`.

### `integrator`

Ví dụ:

```xml
integrator="RK4"
```

`integrator` là phương pháp tích phân simulation. `RK4` thường chính xác hơn Euler nhưng có thể tốn tính toán hơn.

Giai đoạn đầu cứ giữ `RK4`, chỉ đổi khi bạn có lý do rõ ràng.

### `compiler`

Ví dụ:

```xml
<compiler angle="radian" inertiafromgeom="true" autolimits="true"/>
```

Ý nghĩa:

```text
angle="radian"            range/joint angle dùng radian
inertiafromgeom="true"    tự tính mass/inertia từ geom nếu có thể
autolimits="true"         tự bật giới hạn khi có range ở một số trường hợp
```

Trong project này vẫn khai báo `limited="true"` ở default joint để rõ ràng.

### Đọc Một Dòng XML Thực Tế

Ví dụ:

```xml
<body name="left_foot" pos="0 0 -0.40">
  <joint name="ankle_pitch_left" type="hinge" axis="0 1 0" range="-0.7 0.7"/>
  <geom name="left_ankle_geom" type="sphere" size="0.045" material="joint_mat"/>
  <geom name="left_foot_geom" type="box" pos="0.08 0 -0.035" size="0.16 0.06 0.035" material="foot_mat"/>
</body>
```

Diễn giải:

```text
left_foot nằm dưới left_shin 0.40 m.
ankle_pitch_left là khớp quay quanh Y.
range -0.7 tới 0.7 rad tương đương khoảng -40 tới +40 độ.
left_ankle_geom là sphere bán kính 4.5 cm.
left_foot_geom là box:
  tâm box dịch về phía trước 8 cm và xuống 3.5 cm
  full size là 32 cm x 12 cm x 7 cm
  dùng material foot_mat
```

## Vai Trò Từng File

### `modular_humanoid.xml`

File chính, chỉ khai báo global config và include các nhóm lớn:

```xml
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
```

Thường không sửa file này trừ khi:

- Thêm nhóm XML cấp cao mới như `<sensor>`.
- Đổi global `<option>`.
- Đổi default damping/friction/density.

### `assets.xml`

Chứa material, mesh, texture dùng chung.

Material hiện tại:

```xml
<material name="pelvis_mat" rgba="0.16 0.26 0.38 1"/>
<material name="torso_mat" rgba="0.18 0.42 0.78 1"/>
<material name="limb_mat" rgba="0.24 0.50 0.76 1"/>
<material name="joint_mat" rgba="0.94 0.70 0.24 1"/>
<material name="hand_mat" rgba="0.62 0.66 0.68 1"/>
<material name="foot_mat" rgba="0.10 0.12 0.14 1"/>
<material name="sole_mat" rgba="0.04 0.05 0.06 1"/>
<material name="floor_mat" rgba="0.82 0.84 0.86 1"/>
```

Thêm material:

```xml
<material name="hand_mat" rgba="0.72 0.72 0.68 1"/>
```

Thêm mesh:

```xml
<mesh name="torso_mesh" file="../meshes/torso.stl"/>
```

Lưu ý:

- Path mesh tương đối từ `parts/assets.xml`.
- Vì `parts/` nằm dưới `robots/modular_humanoid/parts/`, mesh trong `robots/modular_humanoid/meshes/` nên dùng `../meshes/file.stl`.
- Dùng mesh cho visual trước, primitive geom cho collision.

### `scene.xml`

Chứa môi trường test:

- Light
- Camera
- Floor

Ví dụ floor:

```xml
<geom name="floor" type="plane" size="4 4 0.05" material="floor_mat"/>
```

Khi debug robot:

- Có thể tăng `size` floor.
- Có thể thêm camera mới.
- Không nên đặt robot body ở đây; robot bắt đầu từ `body.xml`.

### `body.xml`

Chứa root body của robot:

```xml
<body name="pelvis" pos="0 0 1.08">
  <freejoint name="root"/>
  <geom name="pelvis_geom" type="capsule" fromto="-0.14 0 0 0.14 0 0" size="0.09" material="pelvis_mat"/>

  <include file="torso.xml"/>
  <include file="right_leg.xml"/>
  <include file="left_leg.xml"/>
</body>
```

Vai trò:

- `pelvis` là body gốc.
- `freejoint` cho phép robot rơi/chuyển động tự do.
- Include torso và hai chân.

Khi sửa:

- Đổi `pos` của pelvis nếu robot bị spawn quá cao/thấp.
- Thêm geom pelvis nếu cần collision tốt hơn.
- Không thêm actuator ở đây.

### `torso.xml`

Chứa waist 3 DOF, torso, neck 2 DOF, head và include hai tay:

```xml
<body name="waist_yaw" pos="0 0 0.12">
  <joint name="abdomen_yaw" type="hinge" axis="0 0 1" range="-0.65 0.65"/>
  <inertial pos="0 0 0" mass="0.04" diaginertia="0.0002 0.0002 0.0002"/>

  <body name="waist_roll">
    <joint name="abdomen_roll" type="hinge" axis="1 0 0" range="-0.45 0.45"/>

    <body name="torso" pos="0 0 0.02">
      <joint name="abdomen_pitch" type="hinge" axis="0 1 0" range="-0.55 0.55"/>
      <geom name="spine_geom" type="capsule" fromto="0 0 -0.03 0 0 0.42" size="0.075" material="torso_mat"/>
      <geom name="chest_geom" type="box" pos="0 0 0.28" size="0.12 0.18 0.16" material="torso_mat"/>

      <body name="neck_yaw" pos="0 0 0.50">
        <joint name="neck_yaw" type="hinge" axis="0 0 1" range="-0.9 0.9"/>
        <body name="head" pos="0 0 0.11">
          <joint name="neck_pitch" type="hinge" axis="0 1 0" range="-0.55 0.55"/>
          <geom name="head_geom" type="sphere" size="0.105" material="joint_mat"/>
        </body>
      </body>
    </body>
  </body>
</body>
```

Nếu tạo body trung gian không có geom, thêm inertial nhỏ:

```xml
<inertial pos="0 0 0" mass="0.02" diaginertia="0.0001 0.0001 0.0001"/>
```

### `right_arm.xml` Và `left_arm.xml`

Mỗi tay hiện có:

- Upper arm
- Forearm
- Wrist
- Hand 3 ngón đơn giản
- Shoulder yaw/roll/pitch
- Forearm yaw
- Elbow pitch
- Wrist yaw/pitch
- Thumb/index/middle finger joints

Right shoulder dùng `Y âm`:

```xml
<body name="right_shoulder_yaw" pos="0 -0.20 0.34">
```

Left shoulder dùng `Y dương`:

```xml
<body name="left_shoulder_yaw" pos="0 0.20 0.34">
```

Quy tắc mirror:

```text
right: pos Y âm, capsule fromto đi Y âm
left:  pos Y dương, capsule fromto đi Y dương
```

Ví dụ right upper arm:

```xml
<geom name="right_upper_arm_geom" type="capsule" fromto="0 0 0 0 -0.26 0" size="0.04" material="limb_mat"/>
```

Ví dụ left upper arm:

```xml
<geom name="left_upper_arm_geom" type="capsule" fromto="0 0 0 0 0.26 0" size="0.04" material="limb_mat"/>
```

Shoulder 3 DOF dùng nested body:

```xml
<body name="right_shoulder_yaw" pos="0 -0.20 0.34">
  <joint name="shoulder_yaw_right" type="hinge" axis="0 0 1" range="-1.2 1.2"/>

  <body name="right_shoulder_roll">
    <joint name="shoulder_roll_right" type="hinge" axis="1 0 0" range="-1.1 0.6"/>

    <body name="right_upper_arm">
      <joint name="shoulder_pitch_right" type="hinge" axis="0 1 0" range="-1.9 1.2"/>
      <geom name="right_upper_arm_geom" type="capsule" fromto="0 0 0 0 -0.28 0" size="0.042" material="limb_mat"/>
    </body>
  </body>
</body>
```

Sau khi thêm joint:

1. Thêm motor trong `actuators.xml`.
2. Thêm target nếu cần trong `sine_pose.py`.
3. Thêm assertion trong `tests/test_project_structure.py`.

### `right_leg.xml` Và `left_leg.xml`

Mỗi chân hiện có:

- Thigh
- Shin
- Foot
- Toe
- Hip yaw/roll/pitch
- Knee pitch
- Ankle roll/pitch
- Toe pitch

Right hip dùng `Y âm`:

```xml
<body name="right_hip_yaw" pos="0 -0.09 -0.04">
```

Left hip dùng `Y dương`:

```xml
<body name="left_hip_yaw" pos="0 0.09 -0.04">
```

Chân kéo xuống theo `Z âm`:

```xml
<geom name="right_thigh_geom" type="capsule" fromto="0 0 0 0 0 -0.42" size="0.055" material="limb_mat"/>
```

Foot kéo về phía trước `X dương`:

```xml
<geom name="right_foot_geom" type="box" pos="0.08 0 -0.035" size="0.16 0.06 0.035" material="foot_mat"/>
```

Khi chỉnh chân:

- Tăng `size` foot nếu robot khó đứng.
- Giữ knee range thường âm khi gập về sau/trước theo axis đã chọn.
- Chỉnh `hip` và `ankle` cẩn thận vì dễ làm foot xuyên floor.

Hip 3 DOF dùng nested body:

```xml
<body name="right_hip_yaw" pos="0 -0.09 -0.04">
  <joint name="hip_yaw_right" type="hinge" axis="0 0 1" range="-0.8 0.8"/>

  <body name="right_hip_roll">
    <joint name="hip_roll_right" type="hinge" axis="1 0 0" range="-0.55 0.45"/>

    <body name="right_thigh">
      <joint name="hip_pitch_right" type="hinge" axis="0 1 0" range="-1.25 1.0"/>
      <geom name="right_thigh_geom" type="capsule" fromto="0 0 0 0 0 -0.42" size="0.058" material="limb_mat"/>
    </body>
  </body>
</body>
```

### `actuators.xml`

Chứa motor cho joint:

```xml
<motor name="hip_pitch_right_motor" joint="hip_pitch_right" gear="110"/>
<motor name="knee_pitch_right_motor" joint="knee_pitch_right" gear="115"/>
```

Quy tắc:

- `name` nên là `<joint_name>_motor`.
- `joint` phải trùng chính xác với tên joint trong part file.
- Nếu joint không có motor, controller không điều khiển được joint đó.
- Gear quá lớn có thể làm simulation giật hoặc nổ contact.

Gợi ý gear:

```text
abdomen: 60-100
hip: 80-120
knee: 80-120
ankle: 50-80
shoulder: 40-70
elbow: 30-60
wrist: 15-35
finger: 3-15
```

## Cách Thêm Một Part Mới

Ví dụ thêm một `sensor_mount_right.xml` vào wrist.

### 1. Tạo file part

Tạo:

```text
robots/modular_humanoid/parts/sensor_mount_right.xml
```

Nội dung mẫu:

```xml
<mujoco>
  <body name="sensor_mount_right" pos="0 -0.04 0.04">
    <geom name="sensor_mount_right_geom" type="box" size="0.02 0.015 0.015" material="hand_mat" contype="0" conaffinity="0"/>
  </body>
</mujoco>
```

### 2. Include vào wrist

Trong `right_arm.xml`, thêm vào trong body `right_wrist`:

```xml
<body name="right_wrist" pos="0 -0.24 0">
  <joint name="wrist_pitch_right" type="hinge" axis="0 1 0" range="-0.8 0.8"/>
  <geom name="right_wrist_geom" type="sphere" size="0.035" material="joint_mat"/>

  <include file="sensor_mount_right.xml"/>
</body>
```

### 3. Thêm actuator nếu part có joint

Nếu part mới có joint, thêm motor trong `actuators.xml`:

```xml
<motor name="new_joint_right_motor" joint="new_joint_right" gear="10"/>
```

### 4. Validate

```bash
.venv/bin/python scripts/validate_xml.py robots/modular_humanoid/modular_humanoid.xml --mujoco
```

### 5. Chạy test ngắn

```bash
.venv/bin/python scripts/run_sim.py --steps 1
```

## Cách Thêm Mesh Visual

### 1. Đặt mesh vào folder

```text
robots/modular_humanoid/meshes/torso.stl
```

### 2. Khai báo trong `assets.xml`

```xml
<mesh name="torso_mesh" file="../meshes/torso.stl"/>
```

### 3. Dùng mesh cho visual

Trong body tương ứng:

```xml
<geom name="torso_visual" type="mesh" mesh="torso_mesh" contype="0" conaffinity="0"/>
<geom name="torso_collision" type="capsule" fromto="0 0 0 0 0 0.42" size="0.11" material="limb_mat"/>
```

Lưu ý:

- `contype="0" conaffinity="0"` biến mesh thành visual-only.
- Giữ primitive collision để simulation ổn định.
- Kiểm tra scale mesh theo mét.

## Cách Đặt Tên

Body:

```text
right_upper_arm
right_forearm
right_wrist
left_thigh
left_shin
left_foot
```

Joint:

```text
shoulder_pitch_right
elbow_pitch_right
wrist_pitch_right
hip_pitch_left
knee_pitch_left
ankle_pitch_left
```

Geom:

```text
right_upper_arm_geom
right_elbow_geom
left_foot_geom
```

Motor:

```text
shoulder_pitch_right_motor
elbow_pitch_right_motor
ankle_pitch_left_motor
```

Material:

```text
limb_mat
joint_mat
foot_mat
hand_mat
```

## Checklist Sau Khi Sửa Part

Chạy:

```bash
.venv/bin/python scripts/validate_xml.py robots/modular_humanoid/modular_humanoid.xml --mujoco
```

Kiểm tra:

- XML parse được.
- MuJoCo load được.
- Joint mới xuất hiện trong output.
- Không có lỗi missing asset.
- Không có lỗi missing mass/inertia.
- Motor trỏ đúng joint.
- Tên không bị trùng.

Chạy:

```bash
.venv/bin/python scripts/run_sim.py --steps 1
```

Kiểm tra:

- Genesis build scene được.
- Không crash ở `scene.add_entity`.
- Không crash ở `scene.build`.

Mở viewer:

```bash
SHOW_VIEWER=1 .venv/bin/python scripts/run_sim.py --steps 10000
```

Kiểm tra:

- Body đúng vị trí.
- Left/right không bị đảo.
- Link không xuyên nhau quá nhiều.
- Foot không xuyên floor.
- Joint chuyển động đúng hướng.

## Lỗi Thường Gặp

### Include Sai Path

Sai:

```xml
<include file="parts/right_arm.xml"/>
```

Nếu bạn đang ở `parts/body.xml`, include sibling file phải là:

```xml
<include file="right_arm.xml"/>
```

Trong `modular_humanoid.xml`, include từ root robot:

```xml
<include file="parts/body.xml"/>
```

### Body Có Joint Nhưng Không Có Mass

Nếu body có joint nhưng không có geom, MuJoCo có thể báo lỗi mass/inertia.

Fix:

```xml
<inertial pos="0 0 0" mass="0.02" diaginertia="0.0001 0.0001 0.0001"/>
```

### Joint Có Trong XML Nhưng Không Chuyển Động

Kiểm tra:

- Joint có motor trong `actuators.xml` chưa.
- Controller có target cho joint đó chưa.
- Joint name trong motor có typo không.
- Joint có nằm trong list output của `validate_xml.py` không.

### Robot Bị Giật Mạnh

Thử:

- Giảm `gear`.
- Giảm amplitude trong `sine_pose.py`.
- Giảm joint range.
- Tăng damping.
- Kiểm tra self-collision ở neutral pose.

### Viewer Không Hiện

Chạy headless trước:

```bash
.venv/bin/python scripts/run_sim.py --steps 1
```

Sau đó thử:

```bash
SHOW_VIEWER=1 PYOPENGL_PLATFORM=glx .venv/bin/python scripts/run_sim.py --steps 10000
```

## Quy Trình Chuẩn Khi Thêm DOF

Ví dụ thêm `shoulder_roll_right`:

1. Sửa `right_arm.xml`.
2. Thêm body trung gian nếu cần.
3. Thêm joint `shoulder_roll_right`.
4. Nếu body trung gian không có geom, thêm inertial.
5. Thêm motor trong `actuators.xml`.
6. Thêm target trong `sine_pose.py` nếu muốn test chuyển động.
7. Thêm test joint trong `tests/test_project_structure.py`.
8. Validate XML.
9. Chạy simulation 1 step.
10. Mở viewer kiểm tra hướng quay.

## Definition Of Done

Một thay đổi trong `parts/` được coi là ổn khi:

- `validate_xml.py --mujoco` pass.
- `scripts/run_sim.py --steps 1` pass.
- Viewer mở được.
- Joint list đúng.
- Motor list đúng.
- Không có body thiếu mass/inertia.
- Không có asset path sai.
- Không có tên trùng.
- Controller không reference joint đã bị xóa.
