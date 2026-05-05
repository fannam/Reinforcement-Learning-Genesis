# Modular Humanoid

Humanoid chi tiết được chia thành nhiều file XML nhỏ bằng MJCF `<include>`.

File chính:

```text
robots/modular_humanoid/modular_humanoid.xml
```

Cấu trúc:

```text
robots/modular_humanoid/
  modular_humanoid.xml         # main file: defaults (PD classes), <contact>, <sensor>
  parts/
    assets.xml                 # materials
    scene.xml                  # floor, light, world camera
    body.xml                   # pelvis + IMU site
    torso.xml                  # spine, neck, head (cam + IMU site)
    right_arm.xml / left_arm.xml
    right_hand.xml / left_hand.xml
    right_leg.xml / left_leg.xml   # foot force/sole/heel/toe sites
    actuators.xml              # 45 <position> PD actuators
    contacts.xml               # self-collision exclusions
    sensors.xml                # IMU + foot 6-axis F/T + sole touch
  meshes/
```

Kinematic structure:

- Torso 3 DOF: yaw, roll, pitch.
- Neck 2 DOF: yaw, pitch.
- Mỗi tay 13 DOF: shoulder 3 DOF, forearm yaw, elbow pitch, wrist 2 DOF, hand 6 DOF.
- Mỗi chân 7 DOF: hip 3 DOF, knee pitch, ankle 2 DOF, toe pitch.
- Tổng cộng 45 actuated hinge joints, cộng với floating root `freejoint`.

Actuator: tất cả là `<position>` PD với `kp/kv/forcerange` đặt qua default class
(`abdomen`, `neck`, `shoulder`, `forearm`, `elbow`, `wrist`, `finger`, `hip`,
`knee`, `ankle`, `toe`). `ctrl` là góc khớp (radian), `forcerange` cap torque.

Sensor (24 channel, 62 scalar):

- Pelvis IMU: gyro, accelerometer, velocimeter, framequat, framepos,
  framelinvel, frameangvel.
- Head IMU: gyro, accelerometer, framequat (cho gaze/vision stabilization).
- Mỗi bàn chân: `force` + `torque` ở ankle, `touch` ở sole/heel/toe tip,
  `framepos` + `framelinvel` ở sole.

Contact: 28 cặp `<exclude>` cho các đoạn cạnh nhau hoặc cross-chain
(thigh-thigh, hand-thigh, forearm-torso, ...) để tránh self-collision giả.

Camera: `front` (world), `head_cam` (gắn trên đầu, FOV 70°).

Lệnh test:

```bash
.venv/bin/python scripts/validate_xml.py robots/modular_humanoid/modular_humanoid.xml --mujoco
SHOW_VIEWER=1 .venv/bin/python scripts/run_sim.py --robot robots/modular_humanoid/modular_humanoid.xml --steps 10000
```

Khi phát triển robot thật, copy folder này thành `robots/my_humanoid_v1/` rồi sửa từng file trong `parts/`.
