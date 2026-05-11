# MJCF Reference (Tiếng Việt)

Tài liệu tham khảo nhanh MuJoCo MJCF XML, biên dịch từ bản gốc tại
`https://mujoco.readthedocs.io/en/stable/XMLreference.html`.

Mục đích: tra cứu offline khi viết file MJCF cho robot. Giữ nguyên tên
element, attribute, và thuật ngữ kỹ thuật (joint, geom, actuator, inertia,
quaternion, stiffness, damping, ...). Phần mô tả là tiếng Việt, rút gọn.

---

## Mục lục

- [Phần 1 — Cây schema MJCF](#phần-1--cây-schema-mjcf)
- [Phần 2 — Reference chi tiết](#phần-2--reference-chi-tiết)
  - [`<compiler>`](#compiler)
    - [`<lengthrange>`](#compilerlengthrange)
  - [`<option>`](#option)
    - [`<flag>`](#optionflag)
  - [`<default>`](#default)
    - [`default/mesh`](#defaultmesh)
    - [`default/material`](#defaultmaterial)
    - [`default/joint`](#defaultjoint)
    - [`default/geom`](#defaultgeom)
    - [`default/site`](#defaultsite)
    - [`default/camera`](#defaultcamera)
    - [`default/light`](#defaultlight)
    - [`default/pair`](#defaultpair)
    - [`default/equality`](#defaultequality)
    - [`default/tendon`](#defaulttendon)
    - [`default/general`](#defaultgeneral)
    - [`default/motor`](#defaultmotor)
    - [`default/position`](#defaultposition)
    - [`default/velocity`](#defaultvelocity)
    - [`default/cylinder`](#defaultcylinder)
    - [`default/muscle`](#defaultmuscle)
  - [`<asset>`](#asset)
    - [`<texture>`](#assettexture)
    - [`<hfield>`](#assethfield)
    - [`<mesh>`](#assetmesh)
    - [`<skin>`](#assetskin)
    - [`<material>`](#assetmaterial)
  - [`<worldbody>` & `<body>`](#worldbody--body)
    - [`<inertial>`](#inertial)
    - [`<joint>`](#joint)
    - [`<freejoint>`](#freejoint)
    - [`<geom>`](#geom)
    - [`<site>`](#site)
    - [`<camera>`](#camera)
    - [`<light>`](#light)
  - [`<contact>`](#contact)
    - [`<pair>`](#contactpair)
    - [`<exclude>`](#contactexclude)
  - [`<actuator>`](#actuator)
    - [`<general>`](#actuatorgeneral)
    - [`<motor>`](#actuatormotor)
    - [`<position>`](#actuatorposition)
    - [`<velocity>`](#actuatorvelocity)
    - [`<intvelocity>`](#actuatorintvelocity)
    - [`<damper>`](#actuatordamper)
    - [`<cylinder>`](#actuatorcylinder)
    - [`<muscle>`](#actuatormuscle)
    - [`<adhesion>`](#actuatoradhesion)
  - [`<sensor>`](#sensor)

---

## Phần 1 — Cây schema MJCF

Ý nghĩa marker (lấy từ doc gốc):

- *required, xuất hiện đúng 1 lần*
- *optional, có thể lặp đệ quy*
- *optional, đúng 1 lần*
- *(không marker) optional, có thể lặp nhiều lần*

```
mujoco                            (root, required)
├── compiler                      (optional, 1 lần)
│   └── lengthrange
├── option                        (optional, 1 lần)
│   └── flag
├── size                          (optional, 1 lần)        [bỏ qua trong tài liệu này]
├── visual                        (optional, 1 lần)        [bỏ qua]
├── statistic                     (optional, 1 lần)        [bỏ qua]
├── default                       (optional, đệ quy)
│   ├── mesh
│   ├── material
│   ├── joint
│   ├── geom
│   ├── site
│   ├── camera
│   ├── light
│   ├── pair
│   ├── equality
│   ├── tendon
│   ├── general / motor / position / velocity /
│   │   cylinder / muscle / damper / intvelocity / adhesion
│   └── default                   (lồng nhau, đệ quy)
├── custom                        [bỏ qua]
├── extension                     [bỏ qua]
├── asset                         (optional, 1 lần)
│   ├── texture
│   ├── hfield
│   ├── mesh
│   │   └── plugin
│   ├── skin
│   └── material
├── worldbody                     (required, 1 lần)
│   ├── geom
│   ├── site
│   ├── camera
│   ├── light
│   └── body                      (đệ quy)
│       ├── inertial              (1 lần)
│       ├── joint
│       ├── freejoint             (1 lần, thay cho joint)
│       ├── geom
│       ├── site
│       ├── camera
│       ├── light
│       ├── composite             [bỏ qua]
│       ├── flexcomp              [bỏ qua]
│       ├── plugin                [bỏ qua]
│       ├── attach                [bỏ qua]
│       ├── frame                 [bỏ qua]
│       └── body                  (đệ quy)
├── deformable                    [bỏ qua]
├── contact                       (optional, 1 lần)
│   ├── pair
│   └── exclude
├── equality                      [bỏ qua]
├── tendon                        [bỏ qua]
├── actuator                      (optional, 1 lần)
│   ├── general
│   ├── motor
│   ├── position
│   ├── velocity
│   ├── intvelocity
│   ├── damper
│   ├── cylinder
│   ├── muscle
│   └── adhesion
├── sensor                        (optional, 1 lần)
│   └── (touch, accelerometer, velocimeter, gyro, force,
│        torque, magnetometer, rangefinder, camprojection,
│        jointpos, jointvel, tendonpos, tendonvel,
│        actuatorpos, actuatorvel, actuatorfrc,
│        jointactuatorfrc, tendonactuatorfrc,
│        ballquat, ballangvel,
│        jointlimitpos, jointlimitvel, jointlimitfrc,
│        tendonlimitpos, tendonlimitvel, tendonlimitfrc,
│        framepos, framequat,
│        framexaxis, frameyaxis, framezaxis,
│        framelinvel, frameangvel,
│        framelinacc, frameangacc,
│        subtreecom, subtreelinvel, subtreeangmom,
│        insidesite, distance, normal, fromto, contact, tactile,
│        e_potential, e_kinetic, clock, user, plugin)
└── keyframe                      [bỏ qua]
```

Ghi chú: trong file MJCF thực tế, thứ tự các section ở mức root là cố định
(compiler, option, size, visual, statistic, default, custom, extension,
asset, worldbody, deformable, contact, equality, tendon, actuator, sensor,
keyframe). Sai thứ tự sẽ gây lỗi parser.

---

## Phần 2 — Reference chi tiết

---

## `<compiler>`

Cấu hình parser/compiler MJCF. Áp dụng global, không có hiệu lực sau khi
compile. Phải đặt ở mức root, trước `<asset>`/`<worldbody>`.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `autolimits` | bool, `true` | Nếu `true`, các attribute `limited` / `forcelimited` / `ctrllimited` / `actlimited` được suy ra tự động khi có `range`. Nếu `false`, phải khai báo cả `limited` và `range`. |
| `boundmass` | real, `0` | Cận dưới khối lượng cho mọi body (trừ world). Hữu ích để fix model URDF có dummy body khối lượng 0. |
| `boundinertia` | real, `0` | Cận dưới cho các phần tử đường chéo của ma trận inertia. |
| `settotalmass` | real, `-1` | Nếu `>0`, scale toàn bộ mass/inertia sao cho tổng khối lượng đúng giá trị này. Áp dụng sau cùng. |
| `balanceinertia` | bool, `false` | Nếu `true`, tự động sửa các inertia diagonal vi phạm `A+B>=C` thành trung bình của 3 giá trị. |
| `strippath` | bool, `false` | Nếu `true`, bỏ phần đường dẫn trong tên file (chỉ giữ tên file). Hữu ích khi load model từ máy khác. |
| `coordinate` | `local` \| `global`, `local` | Chỉ hỗ trợ `local`. `global` đã bị loại bỏ và sẽ gây error. |
| `angle` | `radian` \| `degree`, `degree` (MJCF) / `radian` (URDF) | Đơn vị góc trong file XML. mjModel luôn dùng radian sau compile. |
| `fitaabb` | bool, `false` | Nếu `true`, khi fit primitive vào mesh thì dùng AABB; ngược lại dùng equivalent-inertia box. |
| `eulerseq` | string, `"xyz"` | Thứ tự xoay cho Euler angle. 3 ký tự từ {x,y,z,X,Y,Z}. Chữ thường = intrinsic (xoay theo frame mới), chữ hoa = extrinsic (frame parent cố định). URDF "rpy" = "XYZ". |
| `meshdir` | string, optional | Thư mục chứa file mesh và height field. Path đầy đủ = `[meshdir]/[filename]`, hoặc relative tới file XML. |
| `texturedir` | string, optional | Thư mục chứa file texture. Tương tự `meshdir`. |
| `assetdir` | string, optional | Set cả `meshdir` lẫn `texturedir` cùng lúc. Bị override bởi 2 attribute trên nếu khai báo riêng. |
| `discardvisual` | bool, `false` (MJCF) / `true` (URDF) | Loại bỏ asset thuần visual: textures, materials, geom có `contype=conaffinity=0` không được tham chiếu, mesh không dùng. Mô hình kết quả có dynamics y hệt, mjModel nhỏ hơn, mô phỏng nhanh hơn. |
| `usethread` | bool, `true` | Compile multi-threaded (length range, parallel mesh load). |
| `fusestatic` | bool, `false` (MJCF) / `true` (URDF) | Gộp static body với parent (loại bỏ dummy body). Body bị skip nếu được tham chiếu bởi element khác hoặc chứa site dùng cho force/torque sensor. |
| `inertiafromgeom` | `false` \| `true` \| `auto`, `auto` | Suy mass/inertia từ geom: `false` không suy (phải có `<inertial>`); `true` luôn suy đè giá trị `<inertial>`; `auto` chỉ suy khi không có `<inertial>`. |
| `alignfree` | bool, `false` | Nếu `true`, body có free joint và không có con sẽ tự align body frame với inertia frame (nhanh & ổn định hơn). |
| `inertiagrouprange` | int(2), `"0 5"` | Range geom group dùng để suy mass/inertia. Geom có group ngoài range bị bỏ qua. |
| `saveinertial` | bool, `false` | Nếu `true`, compiler ghi explicit `<inertial>` cho mọi body khi save. |

Ví dụ:

```xml
<compiler angle="degree" coordinate="local" meshdir="meshes/" autolimits="true"/>
```

### `<compiler> / <lengthrange>`

Cấu hình tính length range cho actuator (đặc biệt cho muscle). Nếu omit thì
defaults vẫn áp dụng. Để tắt hoàn toàn, thêm element này với `mode="none"`.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `mode` | `none` \| `muscle` \| `muscleuser` \| `all`, `muscle` | Loại actuator được tính length range. `muscle` = chỉ những actuator có gain/bias type là muscle. `muscleuser` = thêm cả `user`. |
| `useexisting` | bool, `true` | Nếu `true` và length range đã định nghĩa (số đầu < số sau), bỏ qua tính tự động. |
| `uselimit` | bool, `false` | Nếu `true` và actuator gắn với joint/tendon có limit, copy limit thành length range. |
| `accel` | real, `20` | Scale lực dùng để đẩy actuator tới min/max length, sao cho gia tốc joint-space có norm bằng giá trị này. |
| `maxforce` | real, `0` | Giới hạn norm của lực push. `0` = không giới hạn. |
| `timeconst` | real, `1` | Time constant (s) cho damping nhân tạo dùng trong simulation tính range. |
| `timestep` | real, `0.01` | Timestep cho internal simulation. `0` = dùng timestep của model. |
| `inttotal` | real, `10` | Tổng thời gian (s) chạy internal simulation cho mỗi actuator/direction. |
| `interval` | real, `2` | Thời gian cuối simulation dùng để collect length data và detect divergence. |
| `tolrange` | real, `0.05` | Threshold detect divergence: nếu (range trong interval / range tổng) > tolrange thì compile error. |

---

## `<option>`

Cấu hình runtime của simulation. Tương ứng 1-1 với `mjModel.opt`. Có thể
sửa ở runtime nhưng nên đặt sẵn trong XML.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `timestep` | real, `0.002` | Timestep mô phỏng (s). Trade-off chính giữa tốc độ và độ chính xác. Nhỏ hơn = ổn định/chính xác hơn. |
| `impratio` | real, `1` | Tỷ lệ impedance giữa friction và normal cho elliptic friction cone. >1 làm friction "cứng" hơn normal, chống trượt. Không nên dùng giá trị cao với pyramidal cone. |
| `gravity` | real(3), `"0 0 -9.81"` | Vector gia tốc trọng trường. MuJoCo GUI giả định Z là up. |
| `wind` | real(3), `"0 0 0"` | Vận tốc môi trường. Bị trừ khỏi vận tốc body để tính lift/drag/viscous. |
| `magnetic` | real(3), `"0 -0.5 0"` | Magnetic flux toàn cục, dùng cho magnetometer sensor. |
| `density` | real, `0` | Mật độ môi trường (cho lift/drag, scale theo v²). Air ~1.2, nước ~1000. `0` = tắt. |
| `viscosity` | real, `0` | Độ nhớt môi trường (lực tỉ lệ với v). Air ~2e-5, nước ~9e-4. Để tạo damped sim, ưu tiên joint damping thay vì viscosity. |
| `o_margin` | real, `0` | Override margin của tất cả contact pair khi contact override bật. |
| `o_solref`, `o_solimp`, `o_friction` | array | Override solref/solimp/friction cho mọi contact pair khi override bật. |
| `integrator` | `Euler` \| `RK4` \| `implicit` \| `implicitfast`, `Euler` | Integrator số. `implicitfast` bỏ qua Coriolis/centrifugal, ổn định hơn cho damping/fluid. |
| `cone` | `pyramidal` \| `elliptic`, `pyramidal` | Loại friction cone. Elliptic chính xác hơn vật lý; pyramidal đôi khi làm solver nhanh/ổn định hơn. |
| `jacobian` | `dense` \| `sparse` \| `auto`, `auto` | Loại Jacobian. `auto`: dense nếu DOF ≤ 60, sparse nếu > 60. |
| `solver` | `PGS` \| `CG` \| `Newton`, `Newton` | Constraint solver algorithm. |
| `iterations` | int, `100` | Max iteration của constraint solver. |
| `tolerance` | real, `1e-8` | Threshold early termination solver. `0` = tắt early termination. |
| `ls_iterations` | int, `50` | Max linesearch iteration cho CG/Newton. |
| `ls_tolerance` | real, `0.01` | Threshold early termination linesearch. |
| `noslip_iterations` | int, `0` | Max iteration của Noslip post-solver (suppress slip do soft constraint). `0` = tắt. |
| `noslip_tolerance` | real, `1e-6` | Tolerance Noslip solver. |
| `ccd_iterations` | int, `50` | Max iteration của convex collision algorithm. |
| `ccd_tolerance` | real, `1e-6` | Tolerance convex collision. |
| `sleep_tolerance` | real, `1e-4` | Velocity threshold cho phép body sleep. |
| `sdf_iterations` | int, `10` | Số iteration cho SDF collision (per init point). |
| `sdf_initpoints` | int, `40` | Số starting point cho SDF collision search. |
| `actuatorgroupdisable` | int(31), optional | Danh sách actuator group bị disable (group `0..30`). Actuator trong group này không sinh lực. |

Ví dụ:

```xml
<option timestep="0.002" iterations="50" solver="Newton" integrator="implicitfast">
    <flag eulerdamp="disable" sensor="enable"/>
</option>
```

### `<option> / <flag>`

Bật/tắt các phần của simulation pipeline. Mặc định flag của standard
features là `enable`, flag của optional features là `disable`.

| Attribute | Default | Mô tả |
|---|---|---|
| `constraint` | `enable` | Tắt toàn bộ constraint solver computation. |
| `equality` | `enable` | Tắt equality constraint computation. |
| `frictionloss` | `enable` | Tắt friction loss constraint. |
| `limit` | `enable` | Tắt joint/tendon limit constraint. |
| `contact` | `enable` | Tắt collision detection và contact constraint. |
| `spring` | `enable` | Tắt passive spring (joint/tendon). Nếu cùng tắt `damper` thì TẤT CẢ passive force bị tắt (gồm gravity comp, fluid, callback). |
| `damper` | `enable` | Tắt passive damper. Xem `spring`. |
| `gravity` | `enable` | Khi disable, gravity = `(0,0,0)` ở runtime mà không sửa `mjOption`. |
| `clampctrl` | `enable` | Tắt clamping control input cho mọi actuator (override actuator-specific). |
| `warmstart` | `enable` | Tắt warm-start cho constraint solver. Tắt khi eval dynamics tại các state không tạo trajectory. |
| `filterparent` | `enable` | Tắt filter contact pair parent-child body. |
| `actuation` | `enable` | Tắt actuator force và actuator dynamics. |
| `refsafe` | `enable` | Bật safety: dùng `max(solref[0], 2*timestep)` để chống bất ổn. |
| `sensor` | `enable` | Tắt sensor computation. |
| `midphase` | `enable` | Tắt mid-phase collision filter (BVH). |
| `nativeccd` | `enable` | Bật native convex collision pipeline thay cho libccd. |
| `island` | `enable` | Bật constraint island (giải các nhóm constraint disjoint độc lập). PGS chưa support. |
| `eulerdamp` | `enable` | Bật implicit integration cho joint damping trong Euler integrator. |
| `autoreset` | `enable` | Bật auto-reset state khi phát hiện numerical issue. |
| `override` | `disable` | Bật contact override (dùng `o_margin`/`o_solref`/`o_solimp`/`o_friction`). |
| `energy` | `disable` | Bật tính potential & kinetic energy vào `mjData.energy`. Dùng để check accuracy. |
| `fwdinv` | `disable` | Bật so sánh tự động forward vs inverse dynamics; ghi vào `mjData.solver_fwdinv[2]`. |
| `invdiscrete` | `disable` | Bật discrete-time inverse dynamics; tắt midpoint integration cho free body. |
| `multiccd` | `enable` | Bật multi-contact detection cho convex-convex collider (hữu ích cho mesh-mesh có mặt phẳng). |
| `sleep` | `disable` | Bật sleeping. Phải set tại init time để sleep-init policy có hiệu lực. |

---

## `<default>`

Tạo defaults class. Có thể lồng nhau (inherit attribute từ parent class).
Top-level luôn tồn tại; tên là `"main"` nếu omit. Element con tham chiếu
class qua attribute `class="..."`.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `class` | string, required (trừ top-level) | Tên class. Phải duy nhất giữa các defaults class. Dùng để activate khi tạo element thực. |

Ví dụ:

```xml
<default>
    <joint armature="0.01" damping="1" limited="true"/>
    <geom contype="1" conaffinity="1" rgba="0.8 0.6 0.4 1"/>
    <default class="leg">
        <joint range="-90 90"/>
        <geom type="capsule" size="0.04"/>
    </default>
</default>

<worldbody>
    <body>
        <geom class="leg" fromto="0 0 0 0 0 -0.3"/>
        <joint class="leg" axis="0 1 0"/>
    </body>
</worldbody>
```

Mỗi sub-element của `<default>` set attribute mặc định cho element tương
ứng trong model. Các attribute như `name`, `class` luôn không được phép.
Một số attribute reference khác (joint reference, geom1/2, ...) cũng bị loại.

### `default/mesh`

Set defaults cho `<mesh>` (asset). Attribute hợp lệ: `scale`, `maxhullvert`.

### `default/material`

Set defaults cho `<material>` (asset). Tất cả attribute của `material`, trừ
`name`, `class`.

### `default/joint`

Set defaults cho `<joint>`. Tất cả attribute của joint, trừ `name`, `class`.

### `default/geom`

Set defaults cho `<geom>`. Tất cả attribute của geom, trừ `name`, `class`.

### `default/site`

Set defaults cho `<site>`. Tất cả attribute, trừ `name`, `class`.

### `default/camera`

Set defaults cho `<camera>`. Tất cả attribute, trừ `name`, `class`, `mode`,
`target`.

### `default/light`

Set defaults cho `<light>`. Tất cả attribute, trừ `name`, `class`.

### `default/pair`

Set defaults cho `<pair>` trong `<contact>`. Tất cả attribute, trừ `name`,
`class`, `geom1`, `geom2`.

### `default/equality`

Set defaults cho equality constraint chung (`active`, `solref`, `solimp`).

### `default/tendon`

Set defaults cho `<tendon>`. Tất cả attribute, trừ `name`, `class`.

### `default/general`

Set defaults cho `<general>` actuator. Tất cả attribute, trừ `name`,
`class`, và các reference (`joint`, `jointinparent`, `site`, `refsite`,
`tendon`, `slidersite`, `cranksite`).

### `default/motor`, `default/position`, `default/velocity`, `default/cylinder`, `default/muscle`

Đây là *actuator shortcuts* — set các attribute của `<general>` thông qua
shortcut tương ứng. Không nên dùng nhiều shortcut trong cùng class (chúng
override nhau). Loại trừ: `name`, `class`, các reference.


---

## `<asset>`

Element nhóm cho asset (mesh, texture, material, ...). Không có attribute.
Asset được khai báo để các element khác (geom, site, body) tham chiếu qua
tên. File asset xác định loại qua phần mở rộng hoặc `content_type`.

### `<asset> / <texture>`

Tạo texture asset, sau đó được tham chiếu từ `<material>`. Có thể load từ
PNG/KTX/định dạng MuJoCo riêng, hoặc generate procedural.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `name` | string, optional | Tên asset (lấy từ filename nếu omit). Skybox không bắt buộc tên. |
| `type` | `2d` \| `cube` \| `skybox`, `cube` | `2d`: map qua UV (chỉ mesh có sẵn UV) hoặc projection theo Z (plane/hfield). `cube`: shrink-wrap quanh object. `skybox`: rendering nền vô cực, chỉ texture skybox đầu tiên trong model được dùng. |
| `colorspace` | `auto` \| `linear` \| `sRGB`, `auto` | Color space của texture. `auto` đọc từ file, fallback `linear`. |
| `content_type` | string, optional | Media Type khi load file. Hỗ trợ `image/png`, `image/ktx`, `image/vnd.mujoco.texture`. |
| `file` | string, optional | Tên file ảnh (resolve qua `texturedir` của compiler). |
| `gridsize` | int(2), `"1 1"` | Khi cube/skybox load từ 1 file ghép, gridsize = (rows, cols). Tích ≤ 12. Ảnh phải chia đều cho grid. |
| `gridlayout` | string, `"............"` | Chuỗi ký tự `{., R, L, U, D, F, B}` map cell vào mặt cube. Ví dụ: `".U..LFRB.D.."` cho gridsize "3 4". |
| `fileright`, `fileleft`, `fileup`, `filedown`, `filefront`, `fileback` | string, optional | 6 file riêng cho 6 mặt cube/skybox. Map: Right=+X, Left=-X, Up=+Y, Down=-Y, Front=+Z, Back=-Z (regular object). |
| `builtin` | `none` \| `gradient` \| `checker` \| `flat`, `none` | Procedural texture: `gradient` (rgb1→rgb2 sigmoid), `checker` 2x2, `flat` đơn sắc. |
| `rgb1` | real(3), `"0.8 0.8 0.8"` | Màu chính cho procedural texture; cũng dùng fill mặt thiếu của cube/skybox. |
| `rgb2` | real(3), `"0.5 0.5 0.5"` | Màu phụ cho procedural texture. |
| `mark` | `none` \| `edge` \| `cross` \| `random`, `none` | Đánh dấu thêm trên procedural texture. |
| `markrgb` | real(3), `"0 0 0"` | Màu mark. |
| `random` | real, `0.01` | Xác suất bật pixel khi `mark=random`. |
| `width` | int, `0` | Chiều ngang procedural texture (px). |
| `height` | int, `0` | Chiều dọc. Cube/skybox: ignore, height = 6*width. |
| `hflip`, `vflip` | bool, `false` | Lật ảnh khi load từ file. |
| `nchannel` | int, `3` | Số channel (3=RGB, 4=RGBA, 1=PBR roughness/metallic). |

Ví dụ:

```xml
<asset>
    <texture name="grid" type="2d" builtin="checker" rgb1=".1 .2 .3" rgb2=".2 .3 .4"
             width="300" height="300" mark="edge" markrgb=".2 .3 .4"/>
    <texture name="skybox" type="skybox" builtin="gradient" rgb1=".4 .6 .8" rgb2="0 0 0"
             width="32" height="512"/>
</asset>
```

### `<asset> / <hfield>`

Height field (terrain): ma trận 2D độ cao. Dữ liệu lấy từ PNG (gray scale,
trắng = cao), file binary custom, hoặc `nrow`/`ncol` để allocate runtime.

Format binary custom: `int32 nrow, int32 ncol, float32 data[nrow*ncol]`.
Compiler luôn normalize về `[0,1]`. Position/orientation do geom tham chiếu
xác định; spatial extent do `size` của hfield. Collision: union of triangular
prism, max 50 contact với 1 geom.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `name` | string, optional | Tên (lấy từ filename nếu omit). |
| `content_type` | string, optional | `image/png` hoặc `image/vnd.mujoco.hfield`. |
| `file` | string, optional | File PNG hoặc binary. Nếu set, không được set `nrow`/`ncol`. |
| `nrow` | int, `0` | Số hàng (chỉ khi không có file). |
| `ncol` | int, `0` | Số cột. |
| `elevation` | real(nrow*ncol), optional | Mảng elevation trực tiếp. Tự normalize. Thứ tự XML là top-to-bottom; mjModel lưu bottom-to-top. |
| `size` | real(4), required | `(radius_x, radius_y, elevation_z, base_z)`. Hai số đầu là nửa kích thước XY. `elevation_z` scale max độ cao. `base_z` là độ dày đáy `-Z`. |

### `<asset> / <mesh>`

Mesh asset cho geom type `mesh`. Hỗ trợ STL, OBJ, MSH (custom), hoặc khai
báo trực tiếp `vertex`/`face` trong XML. Collision dùng convex hull của mesh.

Compiler tự pre-process: center về (0,0,0), align principal axes inertia với
trục tọa độ; lưu offset vào `mjModel.mesh_pos` / `mesh_quat`. Có thể tắt
align bằng cách dùng `refpos`/`refquat`.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `name` | string, optional | Tên mesh; mặc định = filename không extension. |
| `class` | string, optional | Defaults class. |
| `content_type` | string, optional | `model/stl`, `model/obj`, `model/vnd.mujoco.msh`. |
| `file` | string, optional | File mesh. Extension: `stl`, `msh`, `obj`. Nếu omit, phải có `vertex`. |
| `scale` | real(3), `"1 1 1"` | Scale theo từng trục. Giá trị âm = flip. |
| `inertia` | `convex` \| `exact` \| `legacy` \| `shell`, `legacy` | Cách tính inertia khi suy từ geom. `convex` (khuyến nghị) dùng convex hull. `exact` cần mesh watertight. `legacy` overcount với mesh không lồi. `shell` giả định mass trên bề mặt. |
| `smoothnormal` | bool, `false` | Generate smooth normal (weighted average face normal). `false` giữ sharp edge. |
| `maxhullvert` | int, `-1` | Max vertex của convex hull. `-1` = unlimited; nếu set phải `>3`. |
| `vertex` | real(3*nvert), optional | Vertex 3D position. Không cùng tồn tại với file. |
| `normal` | real(3*nvert), optional | Vertex normal. Số lượng = nvert. |
| `texcoord` | real(2*nvert), optional | UV coordinates trong [0,1]. |
| `face` | int(3*nface), optional | Index 3 đỉnh mỗi face, counter-clockwise, [0, nvert-1]. |
| `refpos` | real(3), `"0 0 0"` | Reference position để trừ khỏi vertex. |
| `refquat` | real(4), `"1 0 0 0"` | Reference quaternion để xoay (dùng conjugate). Tự normalize. |
| `builtin` | string, optional | Generate mesh thủ tục: `sphere(subdivision)`, `hemisphere(resolution)`, `cone(nvert, radius)`, `supersphere(resolution, e, n)`, `supertorus(resolution, radius, s, t)`, `wedge(...)`, `plate(res_x, res_y)`. |
| `params` | real(nparam), optional | Tham số cho `builtin`. |
| `material` | string, optional | Material fallback cho geom mesh không có material riêng. |

Ví dụ:

```xml
<asset>
    <mesh name="forearm" file="forearm.stl" scale="0.001 0.001 0.001"/>
    <mesh name="tetra" vertex="0 0 0  1 0 0  0 1 0  0 0 1"/>
</asset>
```

### `<asset> / <skin>`

Skin asset đã chuyển sang `<deformable>` element. Khai báo trong `<asset>`
là deprecated. Bỏ qua chi tiết trong tài liệu này.

### `<asset> / <material>`

Material asset, được tham chiếu từ geom/site/tendon/skin để set appearance
(beyond simple rgba).

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `name` | string, required | Tên material. |
| `class` | string, optional | Defaults class. |
| `texture` | string, optional | Tên texture asset (RGB). Để dùng PBR layer phải omit attribute này và dùng `<layer>`. |
| `texrepeat` | real(2), `"1 1"` | Số lần lặp texture 2d. |
| `texuniform` | bool, `false` | Cube: `true` map texture lên unit object trước khi scale. 2d: `true` lặp `texrepeat` lần trên 1 spatial unit (không phụ thuộc kích thước). |
| `emission` | real, `0` | Emission scalar. RGB emission = rgba * emission. |
| `specular` | real, `0.5` | Specular RGB (đều giá trị này). [0..1]. |
| `shininess` | real, `0.5` | Shininess. Nhân 128 trước khi truyền OpenGL. [0..1]. |
| `reflectance` | real, `0` | [0..1]. Chỉ có hiệu lực với plane và mặt +Z của box. Renderer dùng stencil buffer xấp xỉ. |
| `metallic` | real, `-1` | PBR metallic coefficient. `-1` = không dùng. |
| `roughness` | real, `-1` | PBR roughness coefficient. |
| `rgba` | real(4), `"1 1 1 1"` | Color & transparency. Nhân thành phần với texture color. Local rgba của geom có precedence. |

Sub-element `<layer>` (PBR rendering): mỗi layer = `texture` + `role` trong
{`rgb`, `normal`, `occlusion`, `roughness`, `metallic`, `opacity`,
`emissive`, `orm` (occlusion+roughness+metallic), `rgba`}.

```xml
<asset>
    <material name="floor" texture="grid" texrepeat="8 8" reflectance="0.2"/>
    <material name="self" rgba="0.7 0.5 0.3 1" specular="0.3"/>
</asset>
```


---

## `<worldbody>` & `<body>`

Tạo cây kinematic. `<worldbody>` là root (top-level), tên cố định "world",
không có attribute, không chứa `<inertial>` hay `<joint>`. `<body>` là body
con, có thể lồng đệ quy.

| Attribute (chỉ `<body>`) | Type / Default | Mô tả |
|---|---|---|
| `name` | string, optional | Tên body (để tham chiếu). |
| `childclass` | string, optional | Defaults class áp cho mọi descendant element (cho đến khi gặp body/frame có `childclass` khác). |
| `mocap` | bool, `false` | Body mocap (chỉ khi là con direct của world và không có joint). Position/quat lấy từ `mjData.mocap_pos`/`mocap_quat` mỗi step. Hữu ích cho stream motion capture, hoặc move bằng chuột trong viewer. |
| `pos` | real(3), `(0,0,0)` | Vị trí body frame trong frame của parent. |
| `quat` / `axisangle` / `xyaxes` / `zaxis` / `euler` | array | Orientation body frame. Chọn 1 trong 5 cách. `quat` (w,x,y,z), `euler` theo `eulerseq` của compiler. |
| `gravcomp` | real, `0` | Gravity compensation (fraction trọng lượng). `1` = bù trọng lực hoàn toàn. `>1` = lực nổi lên. |
| `sleep` | `auto` \| `never` \| `allowed` \| `init`, `auto` | Sleep policy của tree gốc body. `auto` để compiler quyết. `init` = init body asleep (chỉ áp dụng cho default config; keyframe có thể wake up). |
| `user` | real(nbody_user), `"0..."` | User parameters tự định nghĩa. |

Ví dụ:

```xml
<worldbody>
    <geom name="floor" type="plane" size="2 2 0.1"/>
    <body name="torso" pos="0 0 1" childclass="upper">
        <freejoint/>
        <inertial pos="0 0 0" mass="10" diaginertia="0.1 0.1 0.05"/>
        <geom type="capsule" fromto="0 0 -0.1 0 0 0.2" size="0.07"/>
        <body name="arm" pos="0.1 0 0.15">
            <joint name="shoulder" type="hinge" axis="0 1 0" range="-90 90"/>
            <geom type="capsule" fromto="0 0 0 0 0 -0.2" size="0.04"/>
        </body>
    </body>
</worldbody>
```

### `<inertial>`

Khai báo tường minh mass và inertia của body. Inertial frame: gốc tại
center of mass, các trục trùng principal axes (matrix inertia diagonal).
Nếu không khai báo, MuJoCo suy từ geom (nếu `compiler/inertiafromgeom` cho
phép). Khi save XML, inertial luôn được ghi explicit.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `pos` | real(3), required | Vị trí inertial frame (center of mass) trong body frame. **Required ngay cả khi suy từ geom**, vì sự hiện diện của element này tắt cơ chế suy tự động. |
| `quat` / `axisangle` / `xyaxes` / `zaxis` / `euler` | array | Orientation inertial frame. |
| `mass` | real, required | Mass body (≥0). |
| `diaginertia` | real(3), optional | Inertia diagonal trong inertial frame. Nếu omit thì `fullinertia` required. |
| `fullinertia` | real(6), optional | Full inertia matrix M (3x3 đối xứng): `M11 M22 M33 M12 M13 M23`. Compiler eigen-decompose để set frame và diaginertia. Phải positive-definite. |

```xml
<inertial pos="0 0 0.05" mass="2.5" diaginertia="0.012 0.012 0.005"/>
```

### `<joint>`

Joint cho body (DOF giữa body và parent). Body gốc world không thể có
joint. Nếu nhiều joint trong cùng body, transform áp theo thứ tự khai báo.
Vị trí lưu trong `mjData.qpos`, vận tốc trong `mjData.qvel` (chiều khác
nhau khi có ball/free joint do quaternion).

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `name` | string, optional | Tên joint. |
| `class` | string, optional | Defaults class. |
| `type` | `free` \| `ball` \| `slide` \| `hinge`, `hinge` | `free`: 6 DOF (3 trans + 3 rot quaternion), chỉ cho child của world, không kèm joint khác, không có limit. `ball`: 3 DOF rotation quaternion quanh `pos`, không kết hợp được rotation joint khác. `slide`: 1 DOF tịnh tiến theo `axis`. `hinge`: 1 DOF xoay quanh `axis` qua `pos` (mặc định, phổ biến nhất). |
| `group` | int, `0` | Group cho visualizer toggle. |
| `pos` | real(3), `"0 0 0"` | Vị trí joint trong body frame. Bị ignore với free. |
| `axis` | real(3), `"0 0 1"` | Trục xoay (hinge) hoặc hướng tịnh tiến (slide). Tự normalize. |
| `springdamper` | real(2), `"0 0"` | Nếu cả 2 dương, override `stiffness`/`damping` để có time constant + damping ratio mong muốn (tính theo joint inertia ở reference config). Format giống `solref`. |
| `solreflimit`, `solimplimit` | array | Solver param cho joint limit. |
| `solreffriction`, `solimpfriction` | array | Solver param cho dry friction. |
| `stiffness` | real(3), `"0 0 0"` | Hệ số stiffness `(a,b,c)`. `a>0` cho lực `f = -a*x`. Nếu set b/c thêm: `f(x) = -(a*x + b*x² + c*x³)` (polynomial spring). |
| `range` | real(2), `"0 0"` | Joint limit. Đơn vị tùy `compiler/angle` (deg/rad). Với ball: chỉ giá trị thứ 2 dùng (góc tổng), giá trị 1 phải là 0. Free joint không có limit. |
| `limited` | `false` \| `true` \| `auto`, `auto` | Bật limit. `auto` + `compiler/autolimits=true` → bật khi có `range`. |
| `actuatorfrcrange` | real(2), `"0 0"` | Clamp tổng actuator force trên joint. Chỉ hinge/slide. |
| `actuatorfrclimited` | `false` \| `true` \| `auto`, `auto` | Bật clamp force. |
| `actuatorgravcomp` | bool, `false` | Nếu `true`, gravity comp cộng vào `qfrc_actuator` thay vì `qfrc_passive`. Hữu ích khi clamp actuator force để bù trọng lực không vượt limit. |
| `margin` | real, `0` | Khoảng cách dưới đó limit kích hoạt. Cho phép soft limit. |
| `ref` | real, `0` | Reference position/angle (slide/hinge). Joint value tại config khởi tạo. Transform thực = `qpos - ref`. |
| `springref` | real, `0` | Joint value tại đó spring cân bằng. Lưu trong `mjModel.qpos_spring`. |
| `armature` | real, `0` | Inertia bổ sung (rotor/gearbox), reflected inertia. `armature_eff = I_rotor * gear_ratio²`. Cải thiện stability đáng kể, khuyên đặt giá trị nhỏ dương ngay cả khi không có gearbox. |
| `damping` | real(3), `"0 0 0"` | Damping `(a,b,c)`. `a>0`: `f(v) = -a*v`. Nếu thêm b/c: `f(v) = -(a*v + b*v|v| + c*v³)` (anti-symmetric). Euler integrator xử lý damping implicit. |
| `frictionloss` | real, `0` | Dry friction loss (chung cho mọi DOF của joint). |
| `user` | array | User parameters. |

```xml
<joint name="hip" type="hinge" axis="0 1 0" pos="0 0 0"
       range="-45 60" limited="true" damping="0.5" armature="0.01"/>
```

### `<freejoint>`

Shortcut cho free joint không inherit defaults (tránh việc default joint
gắn stiffness/damping/armature cho free joint). Tương đương:
`<joint type="free" stiffness="0" damping="0" frictionloss="0" armature="0"/>`.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `name` | string, optional | Tên joint. |
| `group` | int, `0` | Group. |
| `align` | `false` \| `true` \| `auto`, `auto` | Tự align body frame với inertial frame (cho simple free body — body có free joint, không con). `auto` theo `compiler/alignfree`. Thay đổi `qpos`/`qvel` semantics, có thể vô hiệu keyframe cũ. Không lưu vào XML; thay vào đó pose của body được sửa. |

```xml
<body name="object" pos="0 0 0.5">
    <freejoint/>
    <geom type="box" size="0.05 0.05 0.05"/>
</body>
```

### `<geom>`

Geometric shape gắn cứng với body. Quyết định appearance, collision, và
(một phần) inertia của body. Một body có thể có nhiều geom.

Mass/inertia của body được suy từ geom (nếu `inertiafromgeom`): tổng theo
shape + density (hoặc mass), giả định density đều. Chỉ geom có `group`
trong `inertiagrouprange` được dùng.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `name` | string, optional | Tên geom. |
| `class` | string, optional | Defaults class. |
| `type` | `plane` \| `hfield` \| `sphere` \| `capsule` \| `ellipsoid` \| `cylinder` \| `box` \| `mesh` \| `sdf`, `sphere` | Hình dạng. `plane` & `hfield` chỉ gắn world hoặc static child. `sphere/capsule/cylinder/box` là analytic primitive (collision nhanh). `ellipsoid/mesh/sdf` dùng convex collider general. |
| `contype` | int, `1` | Bitmask collision (32-bit). 2 geom va chạm khi `(contype1 & conaffinity2) \|\| (contype2 & conaffinity1)` ≠ 0. |
| `conaffinity` | int, `1` | Bitmask đối tác collision. |
| `condim` | int, `3` | Số chiều contact: `1` (chỉ normal), `3` (normal + 2 tangent friction), `4` (+rolling/torsional friction), `6` (+full torsional). |
| `group` | int, `0` | Group cho visualizer và inertia inference. |
| `priority` | int, `0` | Priority khi merge contact param từ 2 geom. Geom priority cao hơn quyết định param. Bằng nhau: trung bình. |
| `size` | real(3), `"0 0 0"` | Size theo type: sphere=radius; capsule/cylinder=(radius, half-length); box/ellipsoid=half-size XYZ; plane=(hx, hy, grid_spacing). Bị ignore với mesh/hfield. |
| `material` | string, optional | Material asset. |
| `rgba` | real(4), `"0.5 0.5 0.5 1"` | Color override. Local rgba ưu tiên hơn material rgba. |
| `friction` | real(3), `"1 0.005 0.0001"` | `(slide, spin, roll)` friction. |
| `mass` | real, optional | Mass geom (override density). |
| `density` | real, `1000` | Density để suy mass từ volume. |
| `shellinertia` | bool, `false` | `true` = inertia tính theo bề mặt (mass tập trung trên surface). |
| `solmix` | real, `1` | Trọng số mix solref/solimp với geom kia trong contact pair. |
| `solref`, `solimp` | array | Solver param contact. |
| `margin` | real, `0` | Detect contact ở khoảng cách dist < margin. |
| `gap` | real, `0` | Tạo "cushion": contact phát hiện trong [gap, margin] không sinh force, chỉ để smoothing. |
| `fromto` | real(6), optional | Cho capsule/cylinder/ellipsoid/box: `(x1 y1 z1 x2 y2 z2)` định 2 đầu, suy `pos`/`quat`/length. |
| `pos` | real(3), `"0 0 0"` | Vị trí trong body frame. Mesh: bị offset bởi mesh align. |
| `quat` / `axisangle` / `xyaxes` / `zaxis` / `euler` | array | Orientation. |
| `hfield` | string, optional | Tên hfield asset (khi type=hfield). |
| `mesh` | string, optional | Tên mesh asset (khi type=mesh, hoặc để fit primitive). |
| `fitscale` | real, `1` | Scale factor khi fit primitive vào mesh AABB. |
| `fluidshape` | `none` \| `ellipsoid`, `none` | `ellipsoid` bật ellipsoidal fluid model (lift+drag chính xác hơn cho body). |
| `fluidcoef` | real(5), `"0.5 0.25 1.5 1.0 1.0"` | 5 hệ số ellipsoidal fluid: blunt drag, slender drag, angular drag, kutta lift, magnus lift. |
| `user` | array | User parameters. |

```xml
<geom type="capsule" fromto="0 0 0 0 0 -0.3" size="0.04" rgba="0.6 0.4 0.3 1"
      friction="1 0.5 0.5" condim="3" group="1"/>
<geom type="mesh" mesh="forearm" material="self" density="800"/>
<geom type="plane" size="2 2 0.1" material="floor"/>
```

### `<site>`

Site là frame "nhẹ" gắn cứng với body, không tham gia collision/inertia.
Dùng để: actuator endpoint, sensor mount, tendon anchor, equality constraint
attach, debug visualization.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `name` | string, optional | Tên site. |
| `class` | string, optional | Defaults class. |
| `type` | `sphere` \| `capsule` \| `ellipsoid` \| `cylinder` \| `box`, `sphere` | Shape khi render (chỉ visual). |
| `group` | int, `0` | Group. |
| `material` | string, optional | Material visualization. |
| `rgba` | real(4), `"0.5 0.5 0.5 1"` | Color. |
| `size` | real(3), `"0.005 0.005 0.005"` | Size visual. |
| `fromto` | real(6), optional | Tương tự geom. |
| `pos` | real(3), `"0 0 0"` | Vị trí. |
| `quat` / `axisangle` / `xyaxes` / `zaxis` / `euler` | array | Orientation. |
| `user` | array | User parameters. |

```xml
<site name="ee" pos="0 0 -0.4" size="0.01" rgba="1 0 0 1"/>
<site name="imu" pos="0 0 0.05" type="box" size="0.01 0.01 0.005"/>
```

### `<camera>`

Camera gắn body. Render scene từ pov này. Mặc định: nhìn theo `-Z` của
camera frame, `Y` lên trên.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `name` | string, optional | Tên camera. |
| `class` | string, optional | Defaults class. |
| `mode` | `fixed` \| `track` \| `trackcom` \| `targetbody` \| `targetbodycom`, `fixed` | `fixed`: gắn cứng body parent. `track`: theo body parent nhưng không xoay. `trackcom`: theo COM tổng cây. `targetbody/com`: nhìn vào body chỉ định, vẫn xoay với parent. |
| `target` | string, optional | Body/site khi mode = targetbody*. |
| `fovy` | real, `45` | Field of view dọc (degree). |
| `ipd` | real, `0.068` | Interpupillary distance (cho stereo render). |
| `resolution` | int(2), `"1 1"` | Resolution camera (pixels). |
| `focal` | real(2), optional | Focal length (mm). Cần với physical camera model. |
| `focalpixel` | real(2), optional | Focal length (pixel). |
| `principal` | real(2), optional | Principal point (mm offset). |
| `principalpixel` | real(2), optional | Principal point (pixel). |
| `sensorsize` | real(2), optional | Kích thước sensor (mm). Đi cùng `focal` để mô phỏng physical camera. |
| `projection` | `orthographic` \| `perspective`, `perspective` | Loại projection. |
| `output` | string, optional | (rare) tag output. |
| `pos` / orientation | array | Vị trí và hướng camera trong body frame. |
| `user` | array | User parameters. |

```xml
<camera name="track" mode="trackcom" pos="0 -3 1" xyaxes="1 0 0 0 0.5 1"/>
<camera name="head" pos="0 0 1.7" euler="90 0 0" fovy="60"/>
```

### `<light>`

Đèn render. Có thể gắn body hoặc world.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `name` | string, optional | Tên. |
| `class` | string, optional | Defaults class. |
| `mode` | `fixed` \| `track` \| `trackcom` \| `targetbody` \| `targetbodycom`, `fixed` | Tương tự camera. |
| `target` | string, optional | Body/site khi targetbody*. |
| `directional` | bool, `false` | `true` = đèn hướng (như mặt trời). `false` = point light. |
| `castshadow` | bool, `true` | Có cast shadow không. |
| `active` | bool, `true` | Bật/tắt. |
| `pos` | real(3), `"0 0 0"` | Vị trí. |
| `dir` | real(3), `"0 0 -1"` | Hướng (cho directional/spot). |
| `attenuation` | real(3), `"1 0 0"` | Constant + linear + quadratic attenuation. |
| `cutoff` | real, `45` | Cutoff angle spot (deg). |
| `exponent` | real, `10` | Exponent spot light. |
| `bulbradius` | real, `0.02` | (legacy) bán kính bóng đèn. |
| `range` | real, `0` | Phạm vi soi (0 = vô hạn). |
| `intensity` | real, `0` | Cường độ (PBR renderer). |
| `ambient` | real(3), `"0 0 0"` | Ambient color. |
| `diffuse` | real(3), `"0.7 0.7 0.7"` | Diffuse color. |
| `specular` | real(3), `"0.3 0.3 0.3"` | Specular color. |
| `type` | `spot` \| `directional` \| `point`, `spot` | Loại đèn. |

```xml
<light name="top" pos="0 0 5" dir="0 0 -1" diffuse="0.8 0.8 0.8"
       castshadow="true"/>
```


---

## `<contact>`

Element nhóm (không có attribute) chứa các luật điều chỉnh contact pair
generation. Hai sub-element: `<pair>` (force collision check + custom
property) và `<exclude>` (chặn collision giữa 2 body).

### `<contact> / <pair>`

Định nghĩa cặp geom phải va chạm với property tự khai báo (không suy từ
geom). Đây là cách duy nhất tạo anisotropic friction.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `name` | string, optional | Tên pair. |
| `class` | string, optional | Defaults class. |
| `geom1` | string, required | Tên geom 1. |
| `geom2` | string, required | Tên geom 2. Force vector trong `mjData.efc_force` từ geom1 → geom2. |
| `condim` | int, `3` | Dimensionality contact (1/3/4/6). |
| `friction` | real(5), `"1 1 0.005 0.0001 0.0001"` | `(slide_x, slide_y, spin, roll_x, roll_y)`. Khác nhau giữa 2 chiều slide → anisotropic tangential. Khác giữa 2 roll → anisotropic rolling. Không phải mọi coef đều dùng (tùy `condim`). |
| `solref`, `solimp` | array | Solver param. |
| `solreffriction` | real(2), `"0 0"` | Reference acceleration friction. `"0 0"` = dùng `solref`. Chỉ có hiệu lực với elliptic cone. |
| `margin` | real, `0` | Distance threshold để detect contact. |
| `gap` | real, `0` | Inactive contact range `[margin-gap, margin]` (không sinh force, có trong `mjData.contact`). |

```xml
<contact>
    <pair geom1="finger_tip" geom2="object" friction="1.5 1.5 0.005 0.0001 0.0001"/>
</contact>
```

### `<contact> / <exclude>`

Loại trừ collision giữa 2 body (mọi cặp geom giữa 2 body đều bị skip).

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `name` | string, optional | Tên. |
| `body1` | string, required | Body 1. |
| `body2` | string, required | Body 2. |

```xml
<contact>
    <exclude body1="upper_arm" body2="forearm"/>
</contact>
```


---

## `<actuator>`

Element nhóm chứa actuator. Tất cả actuator đều là SISO. Mọi loại actuator
shortcut (motor/position/velocity/...) đều biên dịch thành `<general>` với
`dyntype`/`gaintype`/`biastype` tương ứng.

13 attribute đầu tiên là common cho mọi loại actuator (chỉ document 1 lần
ở `<general>`).

### `<actuator> / <general>`

Actuator tổng quát, cho phép set tự do các thành phần activation dynamics,
gain, bias.

**Common attributes (mọi loại actuator share):**

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `name` | string, optional | Tên. |
| `class` | string, optional | Defaults class. |
| `group` | int, `0` | Group cho visualizer. |
| `nsample` | int, `0` | Kích thước ring buffer lịch sử ctrl. >0 yêu cầu cho `delay`. Đọc qua `mj_readCtrl`. |
| `interp` | `zoh` \| `linear` \| `cubic`, `zoh` | Phương pháp nội suy đọc lịch sử buffer. |
| `delay` | real, `0` | >0 = đọc ctrl từ buffer thay vì `mjData.ctrl` (mô phỏng latency). Cần `nsample>0`. Thường: `delay = nsample * timestep`. |
| `ctrllimited` | `false` \| `true` \| `auto`, `auto` | Clamp `ctrl` vào `ctrlrange`. `auto` + `autolimits=true` → tự bật khi có `ctrlrange`. Có thể tắt global qua `option/flag/clampctrl`. |
| `forcelimited` | `false` \| `true` \| `auto`, `auto` | Clamp force output vào `forcerange`. |
| `actlimited` | `false` \| `true` \| `auto`, `auto` | Clamp activation state. |
| `ctrlrange` | real(2), `"0 0"` | Range clamp ctrl. |
| `forcerange` | real(2), `"0 0"` | Range clamp force. |
| `actrange` | real(2), `"0 0"` | Range clamp activation. |
| `lengthrange` | real(2), `"0 0"` | Length range của transmission (cho muscle). |
| `gear` | real(6), `"1 0 0 0 0 0"` | Scale length/moment/velocity/force. Scalar transmission chỉ dùng phần tử đầu. Cho joint/site: 6 thành phần định 3D translation + rotation axis. |
| `damping` | real(3), `"0 0 0"` | Viscous damping coefficient `(linear, quadratic, cubic)` apply tại transmission target. Bị scale `gear²` (reflected damping). Khác với `kv` của shortcut: `damping` không bị forcerange clamp, polynomial, implicit integration với Euler. |
| `armature` | real, `0` | Armature inertia (rotor) tại transmission target. Scale `gear²` (reflected inertia). |
| `cranklength` | real, `0` | Độ dài thanh nối (slider-crank). |
| `joint` | string, optional | **Transmission**: actuator tác động lên joint. Hinge/slide: length = qpos * gear[0]. Ball: gear[0..2] là trục xoay trong child frame, length = dot(gear, axis-angle). Free: gear[0..2] tịnh tiến world frame, gear[3..5] xoay child frame, length=0. |
| `jointinparent` | string, optional | Như `joint`, nhưng axis cho ball/free định nghĩa trong parent frame. |
| `site` | string, optional | Apply force/torque tại site. gear[0..2]+gear[3..5] là 6 trục local trong site frame. Length=0 (trừ khi có refsite). |
| `refsite` | string, optional | Đo translation/rotation từ site này tới refsite. Cho phép length≠0, có thể dùng position servo điều khiển end-effector trực tiếp. |
| `body` | string, optional | Adhesion: apply force normal tại các contact của body. Length=0. |
| `tendon` | string, optional | Apply lên tendon (spatial hoặc fixed). length = tendon_length * gear. |
| `cranksite`, `slidersite` | string | Slider-crank transmission. `slidersite` required cho slider-crank, slider trượt theo Z site. |
| `user` | array | User parameters. |
| `actdim` | real, `-1` | Dimension activation state. `-1` = compiler suy theo dyntype. >1 chỉ cho user-defined dynamics. |
| `dyntype` | `none` \| `integrator` \| `filter` \| `filterexact` \| `muscle` \| `user`, `none` | Activation dynamics: `none` (stateless), `integrator` (`act_dot=ctrl`), `filter` (`act_dot=(ctrl-act)/dynprm[0]`), `filterexact` (filter với integration chính xác), `muscle`, `user`. |
| `gaintype` | `fixed` \| `affine` \| `muscle` \| `user`, `fixed` | Force = gain_term * (act|ctrl) + bias_term. `fixed`: gain=gainprm[0]. `affine`: gain = gainprm[0] + gainprm[1]*length + gainprm[2]*velocity. |
| `biastype` | `none` \| `affine` \| `muscle` \| `user`, `none` | `none`: bias=0. `affine`: bias = biasprm[0] + biasprm[1]*length + biasprm[2]*velocity. |
| `dynprm` | real(10), `"1 0 ..."` | Tham số activation dynamics. |
| `gainprm` | real(10), `"1 0 ..."` | Tham số gain. |
| `biasprm` | real(10), `"0 0 ..."` | Tham số bias. |
| `actearly` | bool, `false` | `true` dùng act giá trị bước kế thay vì hiện tại → giảm 1 timestep delay giữa ctrl và acceleration. |

**Transmission**: phải khai báo đúng 1 trong `joint`/`jointinparent`/
`site`/`tendon`/`body`/`cranksite`+`slidersite`.

```xml
<actuator>
    <general name="hip_motor" joint="hip" gear="100" ctrlrange="-1 1"
             dyntype="none" gaintype="fixed" gainprm="1" biastype="none"/>
</actuator>
```

### `<actuator> / <motor>`

Direct-drive actuator (control trực tiếp = force). Underlying:
`dyntype=none`, `gaintype=fixed`, `biastype=none`, `gainprm="1 0 0"`.
Chỉ dùng common attributes, không có custom attribute riêng.

```xml
<motor name="elbow" joint="elbow" gear="50" ctrlrange="-1 1" forcerange="-30 30"/>
```

### `<actuator> / `position`

Position servo (P controller, tùy chọn first-order filter trên ctrl).
Underlying:

| Attr | Setting |
|---|---|
| `dyntype` | `none` (timeconst=0) hoặc `filterexact` (timeconst>0) |
| `gainprm` | `kp 0 0` |
| `biasprm` | `0 -kp -kv` |

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `kp` | real, `1` | Position feedback gain. |
| `kv` | real, `0` | Damping của actuator (mapping vào `-biasprm[2]`). Khuyến nghị implicit/implicitfast integrator. Khác với common `damping`: không scale `gear²`, không polynomial, bị forcerange clamp. |
| `dampratio` | real, `0` | Damping ở đơn vị damping ratio. Loại trừ `kv`. `1` = critical damping. Mass tính từ `qpos0` + armature joint (không gồm passive damping/frictionloss). |
| `timeconst` | real, `0` | Time-constant của first-order filter (>0 → `filterexact`). |
| `inheritrange` | real, `0` | Auto-set `ctrlrange` từ `range` của transmission target. `X=1.0` đúng range, `0.8`/`1.2` thu hẹp/mở rộng quanh midpoint. Loại trừ `ctrlrange`. Chỉ joint/tendon transmission có range. |

```xml
<position name="hip_pos" joint="hip" kp="100" kv="10" ctrlrange="-1.5 1.5"/>
<position name="ee" site="grip" refsite="target" gear="0 1 0 0 0 0" kp="200" inheritrange="1"/>
```

### `<actuator> / <velocity>`

Velocity servo. Khuyến nghị implicit/implicitfast integrator. Underlying:
`gainprm="kv 0 0"`, `biasprm="0 0 -kv"`.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `kv` | real, `1` | Velocity feedback gain. |

Để tạo PD controller phải dùng 2 actuator (1 position + 1 velocity) vì
actuator MuJoCo là SISO.

```xml
<velocity name="wheel_vel" joint="wheel" kv="5" ctrlrange="-10 10"/>
```

### `<actuator> / <intvelocity>`

Integrated-velocity servo (output là position, dùng integrator).
Underlying: `dyntype=integrator`, `gainprm="kp 0 0"`, `biasprm="0 -kp -kv"`,
`actlimited=true`.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `kp` | real, `1` | Position feedback gain. |
| `kv` | real, `0` | Damping. |
| `dampratio` | real, `0` | Như `position/dampratio`. |
| `inheritrange` | real, `0` | Set `actrange` (length semantics) thay vì `ctrlrange` (velocity semantics). |

### `<actuator> / <damper>`

Active damper. `F = -kv * velocity * ctrl`. `kv ≥ 0`. `ctrlrange` required
và phải `≥ 0`. Underlying: `gaintype=affine`, `gainprm="0 0 -kv"`,
`ctrllimited=true`.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `kv` | real, `1` | Velocity feedback gain. |

### `<actuator> / <cylinder>`

Mô phỏng pneumatic/hydraulic cylinder. Underlying: `dyntype=filter`,
`dynprm="timeconst 0 0"`, `gainprm="area 0 0"`, `biastype=affine`.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `timeconst` | real, `1` | Time constant activation dynamics. |
| `area` | real, `1` | Diện tích piston (dùng làm gain). |
| `diameter` | real, optional | Đường kính piston (precedence hơn `area`). |
| `bias` | real(3), `"0 0 0"` | Bias param (copy vào biasprm). |

### `<actuator> / <muscle>`

Muscle actuator (mô hình Hill). Yêu cầu `lengthrange` được tính (compiler
tự tính nếu không khai báo). Underlying: `dyntype=muscle`,
`gaintype=biastype=muscle`.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `timeconst` | real(2), `"0.01 0.04"` | Time constant activation/deactivation. |
| `tausmooth` | real, `0` | Smooth transition giữa 2 timeconst (units of ctrl, ≥0). |
| `range` | real(2), `"0.75 1.05"` | Operating length range (units L0). |
| `force` | real, `-1` | Peak active force at rest. `-1` = tự tính qua `scale`. |
| `scale` | real, `200` | Khi `force<0`: peak_force = scale / `actuator_acc0`. Cho lực lớn hơn cho muscle kéo nhiều khối lượng. |
| `lmin` | real, `0.5` | Lower length normalized FLV curve (units L0). |
| `lmax` | real, `1.6` | Upper length. |
| `vmax` | real, `1.5` | Shortening velocity ở đó force = 0 (L0/s). |
| `fpmax` | real, `1.3` | Passive force tại lmax (relative to peak rest). |
| `fvmax` | real, `1.2` | Active force tại saturating lengthening velocity. |

### `<actuator> / <adhesion>`

Adhesion actuator (gecko/insect-like). Inject lực normal vào tất cả
contact của geom thuộc `body`. Lực chia đều giữa các contact. `length=0`.
`ctrlrange` required và phải `≥0` (chỉ hút, không đẩy). Để hút "from
distance" dùng `margin` + `gap` trên geom của body. Underlying:
`trntype=body`, `ctrllimited=true`, `gainprm="gain 0 0"`.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `body` | string, required | Body chứa geom có contact bị adhesion. |
| `gain` | real, `1` | Total adhesion force = ctrl * gain (chia đều cho các contact). |

```xml
<adhesion name="foot_grip" body="foot" gain="50" ctrlrange="0 1"/>
```


---

## `<sensor>`

Element nhóm cho sensor. Output của tất cả sensor được nối liên tiếp trong
`mjData.sensordata`, kích thước `mjModel.nsensordata`. Sensor không ảnh
hưởng dynamics.

**Common attributes** (có ở mọi sensor type):

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `name` | string, optional | Tên sensor. |
| `noise` | real, `0` | Std deviation của Gaussian noise thêm vào output. |
| `cutoff` | real, `0` | Clip giá trị output (`abs(value) > cutoff` → cắt). `0` = tắt clip. (Khác semantics cho collision sensor — xem dưới.) |
| `nsample` | int, `0` | Ring buffer history cho sensor (cho `delay`). |
| `interp` | `zoh`/`linear`/`cubic`, `zoh` | Nội suy khi đọc history. |
| `interval` | real, `0` | Update interval (s). `0` = mỗi step. |
| `delay` | real, `0` | Delay đọc giá trị từ history. |
| `user` | array | User parameters. |

### Nhóm sensor IMU/site-mounted

Các sensor sau gắn lên `site` (bắt buộc), output trong site frame:

| Sensor | Dim | Output |
|---|---|---|
| `<touch>` | 1 | Tổng normal force của contact rơi vào volume site (geom cùng body với site). |
| `<accelerometer>` | 3 | Linear acceleration tại site (gồm gravity), local frame. |
| `<velocimeter>` | 3 | Linear velocity tại site, local frame. |
| `<gyro>` | 3 | Angular velocity tại site, local frame. (Combine với accelerometer = IMU.) |
| `<force>` | 3 | Lực interaction child→parent body (site gắn child body), site frame. Thường cần dummy body welded tới parent. |
| `<torque>` | 3 | Torque tương ứng. |
| `<magnetometer>` | 3 | Magnetic flux tại site (= `option/magnetic` xoay về site frame). |

**Attributes**: chỉ `site` (required) + common.

```xml
<sensor>
    <accelerometer name="imu_acc" site="imu"/>
    <gyro name="imu_gyro" site="imu"/>
    <touch name="finger_touch" site="finger_pad"/>
    <force name="ee_force" site="ee_force_site"/>
</sensor>
```

### `<rangefinder>`

Đo khoảng cách qua tia. Output -1 nếu tia không trúng geom. Geom cùng body
với site/camera bị loại trừ. Geom có alpha=0 cũng bị loại trừ.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `site` | string, optional | Site phát tia (theo +Z site). 1 đo khoảng cách. |
| `camera` | string, optional | Camera phát tia (theo -Z camera, theo từng pixel). Output `width*height` đo. |
| `data` | string, `dist` | Subset của `[dist, dir, origin, point, normal, depth]`, đúng thứ tự. Ví dụ `"dist point normal"` = 7 số/tia. `dist` = scalar khoảng cách. `point` = giao điểm global. `normal` = pháp tuyến mặt geom. `depth` = depth theo camera plane. |

Bắt buộc đúng 1 trong `site`/`camera`.

### `<camprojection>`

Project 1 site lên image plane của camera, output 2D pixel coord (origin
top-left, không clip). Hữu ích cho visual servoing/keypoint tracking.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `site` | string, required | Site được project. |
| `camera` | string, required | Camera (cần `resolution>0`). |

### Nhóm scalar sensor (joint/tendon/actuator)

Output 1 số, copy từ `mjData`:

| Sensor | Required attr | Output (copy from) |
|---|---|---|
| `<jointpos>` | `joint` (scalar) | `mjData.qpos` cho joint đó. |
| `<jointvel>` | `joint` (scalar) | `mjData.qvel`. |
| `<tendonpos>` | `tendon` | `mjData.ten_length`. |
| `<tendonvel>` | `tendon` | `mjData.ten_velocity`. |
| `<actuatorpos>` | `actuator` | `mjData.actuator_length`. |
| `<actuatorvel>` | `actuator` | `mjData.actuator_velocity`. |
| `<actuatorfrc>` | `actuator` | `mjData.actuator_force` (scalar force, không phải generalized). |
| `<jointactuatorfrc>` | `joint` (scalar) | `mjData.qfrc_actuator`. Tổng lực actuator + (nếu `actuatorgravcomp=true`) gravity comp. Quan trọng khi nhiều actuator share joint. |
| `<tendonactuatorfrc>` | `tendon` | Tổng force actuator lên tendon. |

### Nhóm ball joint sensor

| Sensor | Dim | Output |
|---|---|---|
| `<ballquat>` | 4 | Quaternion ball joint (từ `qpos`). |
| `<ballangvel>` | 3 | Angular velocity (rad/s, axis = direction, speed = norm). |

Required attr: `joint` (must be ball joint).

### Nhóm joint/tendon limit sensor

Đo trạng thái constraint khi limit bị vi phạm. Returns 0 nếu không vi phạm.

| Sensor | Required attr | Output |
|---|---|---|
| `<jointlimitpos>` | `joint` | `efc_pos - efc_margin` (âm khi vi phạm; nếu vi phạm cả 2 phía, trả side đầu). |
| `<jointlimitvel>` | `joint` | `efc_vel`. |
| `<jointlimitfrc>` | `joint` | `efc_force`. |
| `<tendonlimitpos>` | `tendon` | `efc_pos - efc_margin`. |
| `<tendonlimitvel>` | `tendon` | `efc_vel`. |
| `<tendonlimitfrc>` | `tendon` | `efc_force`. |

### Nhóm frame sensor

Đo position/orientation/velocity/acceleration của spatial frame của object,
trong global hoặc relative tới frame khác.

| Sensor | Dim | Output |
|---|---|---|
| `<framepos>` | 3 | Vị trí frame (global hoặc relative `refname` frame). |
| `<framequat>` | 4 | Quaternion orientation frame. |
| `<framexaxis>` | 3 | Vector unit X-axis của frame. |
| `<frameyaxis>` | 3 | Vector Y-axis. |
| `<framezaxis>` | 3 | Vector Z-axis. |
| `<framelinvel>` | 3 | Linear velocity frame. |
| `<frameangvel>` | 3 | Angular velocity frame. |
| `<framelinacc>` | 3 | Linear acceleration. |
| `<frameangacc>` | 3 | Angular acceleration. |

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `objtype` | `body` \| `xbody` \| `geom` \| `site` \| `camera`, required | Loại object. `body` = inertial frame; `xbody` = body frame thông thường (thường ở joint với parent). |
| `objname` | string, required | Tên object. |
| `reftype` | enum (như `objtype`), optional | Frame tham chiếu. Nếu omit, dùng global frame. |
| `refname` | string, optional | Tên reference object. |

### Nhóm subtree sensor

Tính từ subtree kinematic gốc tại `body` (required attribute).

| Sensor | Dim | Output |
|---|---|---|
| `<subtreecom>` | 3 | Center of mass của subtree (global). |
| `<subtreelinvel>` | 3 | Linear velocity của COM subtree. |
| `<subtreeangmom>` | 3 | Angular momentum quanh COM subtree. |

### `<insidesite>`

Trả 1 nếu object nằm trong volume của site, 0 nếu không.

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `objtype` | enum, required | Loại object kiểm tra. |
| `objname` | string, required | Tên object. |
| `site` | string, required | Site định nghĩa volume. |

### Collision sensors: `<distance>`, `<normal>`, `<fromto>`

Đo khoảng cách signed nhỏ nhất / pháp tuyến / segment giữa 2 geom (hoặc giữa
geom của 2 body). Tính độc lập với standard collision filter pipeline. Khuyến
nghị `nativeccd` để chính xác.

**Attributes chung:**

| Attribute | Type / Default | Mô tả |
|---|---|---|
| `cutoff` | real, `0` | Khác sensor thường: định max distance cho collision detection (đối số `dismax` của `mj_geomDistance`). `0` = chỉ phát hiện penetration. >0 cần thiết để đo khoảng cách non-penetration. |
| `geom1` / `body1` | string, optional | Geom hoặc body 1. Phải khai báo đúng 1 trong 2. |
| `geom2` / `body2` | string, optional | Geom hoặc body 2. Có thể mix `geom1` + `body2`. Nếu là body, sensor lấy collision có signed distance nhỏ nhất giữa các geom. |

| Sensor | Dim | Output |
|---|---|---|
| `<distance>` | 1 | Signed distance nhỏ nhất. Trả `cutoff` nếu không phát hiện collision. |
| `<normal>` | 3 | Vector pháp tuyến tại điểm gần nhất, global frame. |
| `<fromto>` | 6 | `(from_xyz, to_xyz)` đoạn thẳng nối 2 điểm gần nhất. |

### Sensor đặc biệt khác

| Sensor | Dim | Required attr | Mô tả |
|---|---|---|---|
| `<contact>` | varies | (nhiều attr) | Collect contact info filtered (data type `force`/`torque`/`dist`/`pos`/...). Xem doc gốc nếu cần. |
| `<tactile>` | nvert*3 | `mesh` (wedge/plate), `site` | Tactile sensor mảng vertex. |
| `<e_potential>` | 1 | (none) | Potential energy `mjData.energy[0]`. Bật flag `energy`. |
| `<e_kinetic>` | 1 | (none) | Kinetic energy `mjData.energy[1]`. |
| `<clock>` | 1 | (none) | Simulation time `mjData.time`. |
| `<user>` | `dim` | `dim`, callback | User-defined sensor (gọi `mjcb_sensor`). |
| `<plugin>` | varies | `plugin`/`instance` | Plugin sensor. |

```xml
<sensor>
    <jointpos name="hip_pos" joint="hip"/>
    <jointvel name="hip_vel" joint="hip"/>
    <framepos name="base_pos" objtype="xbody" objname="torso"/>
    <framequat name="base_quat" objtype="xbody" objname="torso"/>
    <framelinvel name="base_lvel" objtype="xbody" objname="torso"/>
    <frameangvel name="base_avel" objtype="xbody" objname="torso"/>
    <accelerometer name="imu_acc" site="imu"/>
    <gyro name="imu_gyro" site="imu"/>
    <distance name="ee_to_target" geom1="ee_geom" geom2="target_geom" cutoff="1.0"/>
</sensor>
```

---

## Phụ lục — Frame orientation

Mọi element có spatial frame (`body`, `geom`, `site`, `camera`, `light`,
`inertial`) đều cho phép định orientation theo nhiều cách (chọn 1 cách):

| Attribute | Format | Mô tả |
|---|---|---|
| `quat` | real(4) | Unit quaternion `(w, x, y, z)`. Default `(1, 0, 0, 0)`. Compiler tự normalize. |
| `axisangle` | real(4) | `(ax, ay, az, angle)`. Trục xoay + góc (deg/rad theo `compiler/angle`). |
| `xyaxes` | real(6) | 2 vector: X-axis và Y-axis (Z suy bằng cross). Compiler trực giao hoá. |
| `zaxis` | real(3) | Vector Z-axis (mặc định ban đầu `+Z`). Compiler suy X/Y bằng quay nhỏ nhất. |
| `euler` | real(3) | 3 góc Euler theo `compiler/eulerseq`. |

Nếu không khai báo, default = identity (không xoay).

---

## Ghi chú khi viết MJCF cho robot

- **Thứ tự root section** cố định: `compiler` → `option` → `size` →
  `visual` → `statistic` → `default` → `custom` → `extension` → `asset` →
  `worldbody` → `deformable` → `contact` → `equality` → `tendon` →
  `actuator` → `sensor` → `keyframe`. Đặt sai thứ tự → parser error.
- **`autolimits`**: nên bật (default mới = `true`) để khỏi phải khai báo
  `limited="true"` mọi lúc.
- **Free joint**: ưu tiên `<freejoint/>` thay vì `<joint type="free"/>` để
  tránh inherit defaults không mong muốn.
- **Inertia**: nếu suy từ geom thì geom phải có `density` (hoặc `mass`) và
  `group` trong `inertiagrouprange`. Nếu khai báo `<inertial>` tường minh,
  tự động suy bị tắt cho body đó.
- **Mesh STL**: không hỗ trợ texcoord; phải convert sang OBJ/MSH nếu cần
  texture mapping.
- **Friction**: anisotropic chỉ được qua `<contact><pair>`.
- **Implicit integrator** (`implicit`/`implicitfast`) khuyến nghị khi dùng
  position/velocity actuator có `kv`, vì Euler chỉ implicit cho `damping`.
- **PD control**: phải tạo 2 actuator (`<position>` + `<velocity>`) vì
  MuJoCo actuator là SISO. Hoặc dùng 1 `<position>` với `kv`/`dampratio`.
- **Site**: dùng cho mọi điểm tham chiếu (sensor mount, actuator endpoint,
  tendon anchor) — rẻ hơn dummy body nhiều.
- **`gear` armature**: armature `J_eff = J_motor * gear²` (reflected). Đặt
  `armature` nhỏ dương (~1e-4 đến 1e-2) thường cải thiện stability.

