#!/usr/bin/env python3
"""Generate assets/worlds/warehouse.xml — Amazon-style fulfillment center.

Layout: back-to-back pallet rack rows + Kiva pod field + loading dock +
packing stations + conveyors + charging pads. Deterministic via SEED.
"""
from __future__ import annotations

import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "assets" / "worlds" / "warehouse.xml"

SEED = 11
RNG = random.Random(SEED)

# ---------- Arena (44 x 28 x 7) ----------
ARENA_HX = 22.0
ARENA_HY = 14.0
WALL_HZ = 3.5
WALL_T = 0.05

# ---------- Box variants (half-size x, y, z) ----------
BOX_VARIANTS = [
    (0.30, 0.40, 0.25),
    (0.25, 0.30, 0.20),
    (0.40, 0.30, 0.30),
    (0.35, 0.25, 0.20),
    (0.20, 0.20, 0.20),
    (0.45, 0.40, 0.30),
    (0.30, 0.30, 0.30),
    (0.15, 0.15, 0.15),
    (0.22, 0.18, 0.18),
    (0.28, 0.22, 0.16),
    (0.18, 0.28, 0.14),
]

# ---------- Pallet rack rows (Amazon-style selective racking) ----------
# Each "pair" = 2 racks back-to-back. Pairs span the X axis; aisles along Y.
RACK_X_C = -4.0
RACK_HALF_X = 8.0           # rack length along X (16 m)
RACK_HALF_Y = 0.55          # individual rack depth
RACK_PAIR_GAP = 0.10        # back-to-back gap
RACK_PAIR_Y = [-11.0, -7.0, -3.5, 3.5, 7.0, 11.0]  # central aisle around y=0
RACK_LEVELS = [0.55, 1.75, 2.95, 4.15]
RACK_BOXES_PER_LEVEL = 10
RACK_YAW_RANGE = 18.0
RACK_STACK_PROB = 0.40
RACK_TRIPLE_STACK_PROB = 0.20

# ---------- Cross-aisle pallet rack (along east end, axis = Y) ----------
CROSS_X_C = 7.5
CROSS_HALF_X = 0.55
CROSS_HALF_Y = 12.0
CROSS_LEVELS = [0.55, 1.75, 2.95]
CROSS_BOXES_PER_LEVEL = 14

# ---------- Kiva-style pod field (west zone) ----------
POD_X_RANGE = (-19.0, -14.0)
POD_Y_RANGE = (-6.0, 6.0)
POD_HALF = (0.45, 0.45, 0.80)   # each pod ~0.9x0.9x1.6
POD_PITCH_X = 1.3
POD_PITCH_Y = 1.3
POD_BOXES_PER_FACE = 2

# ---------- Loading dock (south wall) ----------
DOCK_Y = -12.5
DOCK_PALLET_X = [round(-17.0 + i * 3.0, 2) for i in range(10)]
DOCK_PALLET_HALF = (0.55, 0.55, 0.05)

# ---------- Packing stations ----------
PACK_STATIONS = [
    (-18.0, -2.0),
    (-18.0,  2.0),
    ( 11.0, -2.0),
    ( 11.0,  2.0),
]
PACK_TABLE_HALF = (0.65, 0.45, 0.45)

# ---------- Conveyor segments (long elevated boxes) ----------
CONVEYORS = [
    {"axis": "x", "start": -8.0, "end": 7.0, "y": 0.0, "z": 0.55},
    {"axis": "y", "x": 3.0,       "start": -10.0, "end": 10.0, "z": 0.55},
]
CONVEYOR_HALF_W = 0.30
CONVEYOR_HALF_T = 0.05

# ---------- Charging pads ----------
CHARGE_PADS = [
    (-20.0, -12.0),
    (-20.0,  12.0),
    ( 10.0, -12.0),
    ( 10.0,  12.0),
]
CHARGE_R = 0.35
CHARGE_HZ = 0.04

# ---------- Floor pile zones (chaotic stacks) ----------
PILE_ZONES = [
    {"x": (-21.0, -18.0), "y": (-10.0,  -8.0), "n": 8},
    {"x": (-21.0, -18.0), "y": (  8.0,  10.0), "n": 8},
    {"x": ( 12.0,  15.0), "y": (-10.0,  -8.0), "n": 6},
    {"x": ( 12.0,  15.0), "y": (  8.0,  10.0), "n": 6},
    {"x": ( -1.5,   1.5), "y": (-13.0, -11.5), "n": 6},
    {"x": ( 15.0,  20.5), "y": ( -6.0,  -1.0), "n": 18},
    {"x": ( 15.0,  20.5), "y": (  1.0,   6.0), "n": 12},
]

# ---------- Overhead truss beams ----------
BEAM_Z = 5.6
BEAM_HALF_T = 0.10
BEAMS_ALONG_X_Y = [-9.0, -3.0, 3.0, 9.0]
BEAMS_ALONG_Y_X = [-15.0, -7.0, 0.0, 7.0, 15.0]

# ---------- Hanging cylinders (lights/sprinklers) ----------
HANGING = [
    (-12.0, -7.0, 4.6),
    (-12.0,  7.0, 4.6),
    (  0.0, -7.0, 4.6),
    (  0.0,  7.0, 4.6),
    (  8.0, -7.0, 4.6),
    (  8.0,  7.0, 4.6),
]
HANGING_HALF_H = 0.45
HANGING_R = 0.10

# ---------- Loose floor crates ----------
FLOOR_CRATES = [
    ( -1.0, -11.0, (0.5, 0.4, 0.4)),
    (-12.0,   0.0, (0.5, 0.6, 0.5)),
    (  6.0, -11.5, (0.6, 0.5, 0.4)),
    ( -3.0,  12.5, (0.4, 0.5, 0.4)),
    ( 13.0,   0.0, (0.5, 0.5, 0.5)),
    ( -17.0,  0.0, (0.4, 0.4, 0.4)),
]


def fmt_geom(name, gtype, pos, size, material, cls=None, euler=None, collision=True, rgba=None) -> str:
    """Emit visual geom (group=2, no collision, with material) plus an optional
    collision twin (group=3, contype=1, no material)."""
    pos_str = " ".join(f"{v:.3f}" for v in pos)
    size_str = " ".join(f"{v:.3f}" for v in size)
    extra = ""
    if euler is not None:
        extra = ' euler="' + " ".join(f"{v:.2f}" for v in euler) + '"'
    if rgba is not None:
        rgba_str = " ".join(f"{v:.2f}" for v in rgba)
        extra += f' rgba="{rgba_str}"'
    
    cls_str = f' class="{cls}"' if cls else ' class="env_visual"'
    parts = [
        f'<geom{cls_str} name="{name}" type="{gtype}" '
        f'pos="{pos_str}" size="{size_str}"{extra} material="{material}"/>'
    ]
    if collision:
        parts.append(
            f'<geom class="env_solid" name="{name}_col" type="{gtype}" '
            f'pos="{pos_str}" size="{size_str}"{extra}/>'
        )
    return "\n        ".join(parts)


def fmt_body(name, gtype, pos, size, material, euler=None, density=100.0) -> str:
    """Emit a body with a free joint and a geom. Used for dynamic objects."""
    pos_str = " ".join(f"{v:.3f}" for v in pos)
    size_str = " ".join(f"{v:.3f}" for v in size)
    euler_str = ""
    if euler is not None:
        euler_str = ' euler="' + " ".join(f"{v:.2f}" for v in euler) + '"'
    
    return f"""<body name="dyn_{name}" pos="{pos_str}"{euler_str}>
            <freejoint name="joint_{name}"/>
            <geom name="{name}" type="{gtype}" size="{size_str}" material="{material}" density="{density}" contype="1" conaffinity="1" group="3"/>
            <geom name="{name}_visual" type="{gtype}" size="{size_str}" material="{material}" contype="0" conaffinity="0" group="2"/>
        </body>"""


def post_dims(top_z: float):
    total = top_z + 0.2
    return total / 2, total / 2  # half_h, pos_z


def pick_variant(max_half_x=None, max_half_y=None, max_half_z=None):
    pool = BOX_VARIANTS
    if max_half_x is not None:
        pool = [v for v in pool if v[0] <= max_half_x]
    if max_half_y is not None:
        pool = [v for v in pool if v[1] <= max_half_y]
    if max_half_z is not None:
        pool = [v for v in pool if v[2] <= max_half_z]
    return RNG.choice(pool) if pool else BOX_VARIANTS[-1]


def stack_box(name, base_cx, base_cy, base_top_z, base_half, yaw_base, max_yaw_jitter=20.0):
    bhx, bhy, bhz = base_half
    top = pick_variant(max_half_x=bhx, max_half_y=bhy, max_half_z=bhz)
    thx, thy, thz = top
    tx = base_cx + RNG.uniform(-0.05, 0.05)
    ty = base_cy + RNG.uniform(-0.05, 0.05)
    tz = base_top_z + thz
    tyaw = yaw_base + RNG.uniform(-max_yaw_jitter, max_yaw_jitter)
    return fmt_geom(name, "box", (tx, ty, tz), top, "mat_box_yellow",
                    euler=(0, 0, tyaw)), (tx, ty, tz + thz, top, tyaw)


def gen_single_rack(prefix, x_c, y_c, half_x, half_y, levels):
    out = []
    half_h, post_z = post_dims(levels[-1])
    corners = [
        (-half_x, -half_y),
        (-half_x,  half_y),
        ( half_x, -half_y),
        ( half_x,  half_y),
    ]
    for pi, (dx, dy) in enumerate(corners):
        out.append(fmt_geom(f"{prefix}_post_{pi}", "cylinder",
                            (x_c + dx, y_c + dy, post_z),
                            (0.05, half_h), "mat_shelf_red"))
    for li, z in enumerate(levels):
        out.append(fmt_geom(f"{prefix}_plank_l{li}", "box",
                            (x_c, y_c, z),
                            (half_x, half_y, 0.015), "mat_shelf_red"))
        # cross-brace beam between rack uprights for Amazon look
        out.append(fmt_geom(f"{prefix}_beam_l{li}_f", "box",
                            (x_c, y_c - half_y, z + 0.05),
                            (half_x, 0.025, 0.04), "mat_beam"))
        out.append(fmt_geom(f"{prefix}_beam_l{li}_b", "box",
                            (x_c, y_c + half_y, z + 0.05),
                            (half_x, 0.025, 0.04), "mat_beam"))

        n = RACK_BOXES_PER_LEVEL
        bin_w = 2 * half_x / n
        for bi in range(n):
            half = pick_variant(max_half_y=half_y - 0.05)
            bhx, bhy, bhz = half
            bin_lo = -half_x + bi * bin_w + bhx + 0.04
            bin_hi = -half_x + (bi + 1) * bin_w - bhx - 0.04
            if bin_lo >= bin_hi:
                bin_lo = bin_hi = (bin_lo + bin_hi) / 2
            x_off = RNG.uniform(bin_lo, bin_hi)
            y_max = max(0.0, half_y - bhy - 0.02)
            y_off = RNG.uniform(-y_max, y_max)
            yaw = RNG.uniform(-RACK_YAW_RANGE, RACK_YAW_RANGE)
            cx = x_c + x_off
            cy = y_c + y_off
            cz = z + 0.015 + bhz
            out.append(fmt_geom(f"{prefix}_box_l{li}_b{bi}", "box",
                                (cx, cy, cz), half, "mat_box_yellow",
                                euler=(0, 0, yaw)))
            if RNG.random() < RACK_STACK_PROB:
                geom_str, top_state = stack_box(
                    f"{prefix}_box_l{li}_b{bi}_s1",
                    cx, cy, cz + bhz, half, yaw,
                )
                out.append(geom_str)
                if RNG.random() < RACK_TRIPLE_STACK_PROB:
                    tx, ty, t_top_z, top_half, t_yaw = top_state
                    geom_str2, _ = stack_box(
                        f"{prefix}_box_l{li}_b{bi}_s2",
                        tx, ty, t_top_z, top_half, t_yaw,
                    )
                    out.append(geom_str2)
    return out


def gen_rack_pairs():
    out = []
    for pair_i, y_c in enumerate(RACK_PAIR_Y):
        y_front = y_c - (RACK_HALF_Y + RACK_PAIR_GAP / 2)
        y_back  = y_c + (RACK_HALF_Y + RACK_PAIR_GAP / 2)
        out.extend(gen_single_rack(f"rack_p{pair_i}_f",
                                   RACK_X_C, y_front, RACK_HALF_X, RACK_HALF_Y,
                                   RACK_LEVELS))
        out.extend(gen_single_rack(f"rack_p{pair_i}_b",
                                   RACK_X_C, y_back, RACK_HALF_X, RACK_HALF_Y,
                                   RACK_LEVELS))
        # aisle floor markings (thin yellow strips)
        out.append(fmt_geom(f"aisle_mark_p{pair_i}_a", "box",
                            (RACK_X_C, y_c - 1.4, 0.005),
                            (RACK_HALF_X, 0.04, 0.005), "mat_marking",
                            collision=False))
        out.append(fmt_geom(f"aisle_mark_p{pair_i}_b", "box",
                            (RACK_X_C, y_c + 1.4, 0.005),
                            (RACK_HALF_X, 0.04, 0.005), "mat_marking",
                            collision=False))
    return out


def gen_cross_rack():
    out = []
    half_h, post_z = post_dims(CROSS_LEVELS[-1])
    corners = [
        (-CROSS_HALF_X, -CROSS_HALF_Y),
        (-CROSS_HALF_X,  CROSS_HALF_Y),
        ( CROSS_HALF_X, -CROSS_HALF_Y),
        ( CROSS_HALF_X,  CROSS_HALF_Y),
    ]
    for pi, (dx, dy) in enumerate(corners):
        out.append(fmt_geom(f"cross_post_{pi}", "cylinder",
                            (CROSS_X_C + dx, dy, post_z),
                            (0.05, half_h), "mat_shelf_red"))
    for li, z in enumerate(CROSS_LEVELS):
        out.append(fmt_geom(f"cross_plank_l{li}", "box",
                            (CROSS_X_C, 0.0, z),
                            (CROSS_HALF_X, CROSS_HALF_Y, 0.015), "mat_shelf_red"))
        n = CROSS_BOXES_PER_LEVEL
        bin_w = 2 * CROSS_HALF_Y / n
        for bi in range(n):
            half = pick_variant(max_half_x=CROSS_HALF_X - 0.05)
            bhx, bhy, bhz = half
            bin_lo = -CROSS_HALF_Y + bi * bin_w + bhy + 0.04
            bin_hi = -CROSS_HALF_Y + (bi + 1) * bin_w - bhy - 0.04
            if bin_lo >= bin_hi:
                bin_lo = bin_hi = (bin_lo + bin_hi) / 2
            y_off = RNG.uniform(bin_lo, bin_hi)
            x_max = max(0.0, CROSS_HALF_X - bhx - 0.02)
            x_off = RNG.uniform(-x_max, x_max)
            yaw = RNG.uniform(-RACK_YAW_RANGE, RACK_YAW_RANGE)
            cx = CROSS_X_C + x_off
            cy = y_off
            cz = z + 0.015 + bhz
            out.append(fmt_geom(f"cross_box_l{li}_b{bi}", "box",
                                (cx, cy, cz), half, "mat_box_yellow",
                                euler=(0, 0, yaw)))
            if RNG.random() < RACK_STACK_PROB:
                geom_str, _ = stack_box(
                    f"cross_box_l{li}_b{bi}_s1",
                    cx, cy, cz + bhz, half, yaw,
                )
                out.append(geom_str)
    return out


def gen_pod_field():
    out = []
    phx, phy, phz = POD_HALF
    x_lo, x_hi = POD_X_RANGE
    y_lo, y_hi = POD_Y_RANGE
    pi = 0
    x = x_lo
    while x <= x_hi:
        y = y_lo
        while y <= y_hi:
            # pod base (thin slab) + tall body (orange)
            out.append(fmt_geom(f"pod_{pi}_base", "box",
                                (x, y, 0.04),
                                (phx, phy, 0.04), "mat_pod_base"))
            out.append(fmt_geom(f"pod_{pi}_body", "box",
                                (x, y, 0.04 + phz),
                                (phx * 0.9, phy * 0.9, phz), "mat_pod"))
            # boxes on top of pod (Kiva pods carry inventory)
            top_z = 0.04 + 2 * phz
            for bi in range(POD_BOXES_PER_FACE):
                half = pick_variant(max_half_x=phx * 0.7, max_half_y=phy * 0.7)
                bhx, bhy, bhz = half
                bx = x + RNG.uniform(-phx * 0.5, phx * 0.5)
                by = y + RNG.uniform(-phy * 0.5, phy * 0.5)
                bz = top_z + bhz + bi * (2 * bhz + 0.005)
                yaw = RNG.uniform(-30, 30)
                out.append(fmt_geom(f"pod_{pi}_box_{bi}", "box",
                                    (bx, by, bz), half, "mat_box_yellow",
                                    euler=(0, 0, yaw)))
            pi += 1
            y += POD_PITCH_Y
        x += POD_PITCH_X
    return out


def gen_loading_dock():
    out = []
    phx, phy, phz = DOCK_PALLET_HALF
    # dock floor stripe (yellow safety zone)
    out.append(fmt_geom("dock_safety_zone", "box",
                        (-2.5, DOCK_Y + 1.0, 0.005),
                        (16.0, 0.06, 0.005), "mat_marking",
                        collision=False))
    for pi, px in enumerate(DOCK_PALLET_X):
        py = DOCK_Y
        out.append(fmt_geom(f"dock_pallet_{pi}", "box",
                            (px, py, phz),
                            (phx, phy, phz), "mat_pallet"))
        # 2-3 boxes stacked on each pallet
        prev_top = 2 * phz
        prev_half = (phx - 0.05, phy - 0.05, 0.30)
        prev_cx, prev_cy, prev_yaw = px, py, RNG.uniform(-15, 15)
        n_layers = RNG.randint(2, 4)
        for si in range(n_layers):
            half = pick_variant(max_half_x=prev_half[0], max_half_y=prev_half[1])
            thx, thy, thz = half
            sx = prev_cx + RNG.uniform(-0.06, 0.06)
            sy = prev_cy + RNG.uniform(-0.06, 0.06)
            sz = prev_top + thz
            syaw = prev_yaw + RNG.uniform(-15, 15)
            out.append(fmt_geom(f"dock_pallet_{pi}_box_{si}", "box",
                                (sx, sy, sz), half, "mat_box_yellow",
                                euler=(0, 0, syaw)))
            prev_top = sz + thz
            prev_half = half
            prev_cx, prev_cy, prev_yaw = sx, sy, syaw
    return out


def gen_packing_stations():
    out = []
    thx, thy, thz = PACK_TABLE_HALF
    for ti, (tx, ty) in enumerate(PACK_STATIONS):
        # table top
        out.append(fmt_geom(f"pack_table_{ti}_top", "box",
                            (tx, ty, thz),
                            (thx, thy, 0.03), "mat_table"))
        # 4 legs
        for li, (lx, ly) in enumerate([(-thx + 0.04, -thy + 0.04),
                                        (-thx + 0.04,  thy - 0.04),
                                        ( thx - 0.04, -thy + 0.04),
                                        ( thx - 0.04,  thy - 0.04)]):
            out.append(fmt_geom(f"pack_table_{ti}_leg_{li}", "cylinder",
                                (tx + lx, ty + ly, thz / 2),
                                (0.025, thz / 2), "mat_beam"))
        # boxes on the workstation
        for bi in range(RNG.randint(2, 4)):
            half = pick_variant(max_half_x=thx - 0.1, max_half_y=thy - 0.1, max_half_z=0.25)
            bhx, bhy, bhz = half
            bx = tx + RNG.uniform(-thx + bhx + 0.05, thx - bhx - 0.05)
            by = ty + RNG.uniform(-thy + bhy + 0.05, thy - bhy - 0.05)
            bz = thz + 0.03 + bhz
            yaw = RNG.uniform(-30, 30)
            out.append(fmt_geom(f"pack_table_{ti}_box_{bi}", "box",
                                (bx, by, bz), half, "mat_box_yellow",
                                euler=(0, 0, yaw)))
    return out


def gen_conveyors():
    out = []
    for ci, c in enumerate(CONVEYORS):
        if c["axis"] == "x":
            cx = (c["start"] + c["end"]) / 2
            half_x = (c["end"] - c["start"]) / 2
            out.append(fmt_geom(f"conveyor_{ci}_top", "box",
                                (cx, c["y"], c["z"]),
                                (half_x, CONVEYOR_HALF_W, CONVEYOR_HALF_T),
                                "mat_conveyor"))
            # support legs every 2 m
            x = c["start"]
            li = 0
            while x <= c["end"]:
                out.append(fmt_geom(f"conveyor_{ci}_leg_{li}", "cylinder",
                                    (x, c["y"], c["z"] / 2),
                                    (0.04, c["z"] / 2), "mat_beam"))
                x += 2.0
                li += 1
            # parcels riding the conveyor
            x = c["start"] + 0.4
            pi = 0
            while x < c["end"] - 0.4:
                half = pick_variant(max_half_x=0.3, max_half_y=CONVEYOR_HALF_W - 0.05)
                bhx, bhy, bhz = half
                bz = c["z"] + CONVEYOR_HALF_T + bhz
                yaw = RNG.uniform(-12, 12)
                out.append(fmt_geom(f"conveyor_{ci}_pkg_{pi}", "box",
                                    (x, c["y"] + RNG.uniform(-0.08, 0.08), bz),
                                    half, "mat_box_yellow", euler=(0, 0, yaw)))
                x += RNG.uniform(0.9, 1.4)
                pi += 1
        else:
            cy = (c["start"] + c["end"]) / 2
            half_y = (c["end"] - c["start"]) / 2
            out.append(fmt_geom(f"conveyor_{ci}_top", "box",
                                (c["x"], cy, c["z"]),
                                (CONVEYOR_HALF_W, half_y, CONVEYOR_HALF_T),
                                "mat_conveyor"))
            y = c["start"]
            li = 0
            while y <= c["end"]:
                out.append(fmt_geom(f"conveyor_{ci}_leg_{li}", "cylinder",
                                    (c["x"], y, c["z"] / 2),
                                    (0.04, c["z"] / 2), "mat_beam"))
                y += 2.0
                li += 1
            y = c["start"] + 0.4
            pi = 0
            while y < c["end"] - 0.4:
                half = pick_variant(max_half_x=CONVEYOR_HALF_W - 0.05, max_half_y=0.3)
                bhx, bhy, bhz = half
                bz = c["z"] + CONVEYOR_HALF_T + bhz
                yaw = RNG.uniform(-12, 12)
                out.append(fmt_geom(f"conveyor_{ci}_pkg_{pi}", "box",
                                    (c["x"] + RNG.uniform(-0.08, 0.08), y, bz),
                                    half, "mat_box_yellow", euler=(0, 0, yaw)))
                y += RNG.uniform(0.9, 1.4)
                pi += 1
    return out


def gen_charge_pads():
    out = []
    for ci, (cx, cy) in enumerate(CHARGE_PADS):
        out.append(fmt_geom(f"charge_pad_{ci}", "cylinder",
                            (cx, cy, CHARGE_HZ),
                            (CHARGE_R, CHARGE_HZ), "mat_charge",
                            collision=False))
    return out


def gen_pile_zones():
    out = []
    for zi, zone in enumerate(PILE_ZONES):
        x_lo, x_hi = zone["x"]
        y_lo, y_hi = zone["y"]
        for bi in range(zone["n"]):
            half = pick_variant(max_half_y=0.40, max_half_x=0.40)
            bhx, bhy, bhz = half
            mx = max(bhx, bhy) + 0.05
            if (x_hi - x_lo) < 2 * mx or (y_hi - y_lo) < 2 * mx:
                continue
            x = RNG.uniform(x_lo + mx, x_hi - mx)
            y = RNG.uniform(y_lo + mx, y_hi - mx)
            stack_lvl = RNG.choice([0, 0, 1, 1, 2])
            cz = bhz + stack_lvl * (2 * bhz + 0.01)
            yaw = RNG.uniform(0, 90)
            
            # Make some boxes dynamic
            if RNG.random() < 0.4: # 40% chance of being dynamic
                out.append(fmt_body(f"pile_z{zi}_b{bi}", "box",
                                   (x, y, cz), half, "mat_box_yellow",
                                   euler=(0, 0, yaw)))
            else:
                out.append(fmt_geom(f"pile_z{zi}_b{bi}", "box",
                                    (x, y, cz), half, "mat_box_yellow",
                                    euler=(0, 0, yaw)))
    return out


def gen_bollards():
    """Add safety bollards at the ends of rack aisles."""
    out = []
    bi = 0
    for y_c in RACK_PAIR_Y:
        for x in [RACK_X_C - RACK_HALF_X - 0.5, RACK_X_C + RACK_HALF_X + 0.5]:
            for dy in [-1.5, 1.5]:
                out.append(fmt_geom(f"bollard_{bi}", "cylinder",
                                   (x, y_c + dy, 0.4), (0.08, 0.4), "mat_marking"))
                bi += 1
    return out


def gen_floor_imperfections():
    """Add some visual noise to the floor (stains, wear)."""
    out = []
    for i in range(15):
        x = RNG.uniform(-ARENA_HX + 2, ARENA_HX - 2)
        y = RNG.uniform(-ARENA_HY + 2, ARENA_HY - 2)
        size = (RNG.uniform(0.3, 1.2), RNG.uniform(0.3, 1.2), 0.001)
        out.append(fmt_geom(f"wear_{i}", "box", (x, y, 0.002), size, "mat_floor_wear", collision=False))
    return out


def gen_beams():
    out = []
    for bi, by in enumerate(BEAMS_ALONG_X_Y):
        out.append(fmt_geom(f"beam_x_{bi}", "box",
                            (0.0, by, BEAM_Z),
                            (ARENA_HX, BEAM_HALF_T, BEAM_HALF_T), "mat_beam"))
    for bi, bx in enumerate(BEAMS_ALONG_Y_X):
        out.append(fmt_geom(f"beam_y_{bi}", "box",
                            (bx, 0.0, BEAM_Z),
                            (BEAM_HALF_T, ARENA_HY, BEAM_HALF_T), "mat_beam"))
    return out


def gen_hanging():
    out = []
    for hi, (hx, hy, hz) in enumerate(HANGING):
        out.append(fmt_geom(f"hanging_{hi}", "cylinder",
                            (hx, hy, hz), (HANGING_R, HANGING_HALF_H),
                            "mat_shelf_red", collision=False))
    return out


def gen_floor_crates():
    out = []
    for ci, (cx, cy, half) in enumerate(FLOOR_CRATES):
        yaw = RNG.uniform(-30, 30)
        out.append(fmt_geom(f"crate_{ci}", "box",
                            (cx, cy, half[2]), half, "mat_box_yellow",
                            euler=(0, 0, yaw)))
    return out


def gen_walls():
    return [
        fmt_geom("wall_north", "box", (0, ARENA_HY, WALL_HZ), (ARENA_HX, WALL_T, WALL_HZ), "mat_wall"),
        fmt_geom("wall_south", "box", (0, -ARENA_HY, WALL_HZ), (ARENA_HX, WALL_T, WALL_HZ), "mat_wall"),
        fmt_geom("wall_east",  "box", (ARENA_HX, 0, WALL_HZ), (WALL_T, ARENA_HY, WALL_HZ), "mat_wall"),
        fmt_geom("wall_west",  "box", (-ARENA_HX, 0, WALL_HZ), (WALL_T, ARENA_HY, WALL_HZ), "mat_wall"),
    ]


def gen_lights():
    # ceiling grid of warm directional lights
    lights = []
    for x in (-15.0, -7.0, 0.0, 7.0, 15.0):
        for y in (-9.0, 0.0, 9.0):
            lights.append(
                f'<light pos="{x:.1f} {y:.1f} 6.0" dir="0 0 -1" '
                f'diffuse="0.4 0.4 0.4" specular="0.1 0.1 0.1"/>'
            )
    # corner fill lights
    lights.append('<light pos="-18 -10 5" dir="0.5 0.3 -1" diffuse="0.2 0.2 0.2"/>')
    lights.append('<light pos="18 10 5"   dir="-0.5 -0.3 -1" diffuse="0.2 0.2 0.2"/>')
    
    # aisle lights (blueish/cold for contrast)
    for y in RACK_PAIR_Y:
        lights.append(f'<light pos="0 {y:.1f} 4.0" dir="0 0 -1" diffuse="0.1 0.1 0.2"/>')
    
    return "\n        ".join(lights)


def main() -> None:
    geoms: list[str] = []
    geoms.extend(gen_walls())
    geoms.extend(gen_rack_pairs())
    geoms.extend(gen_cross_rack())
    geoms.extend(gen_pod_field())
    geoms.extend(gen_loading_dock())
    geoms.extend(gen_packing_stations())
    geoms.extend(gen_conveyors())
    geoms.extend(gen_charge_pads())
    geoms.extend(gen_pile_zones())
    geoms.extend(gen_beams())
    geoms.extend(gen_hanging())
    geoms.extend(gen_floor_crates())
    geoms.extend(gen_bollards())
    geoms.extend(gen_floor_imperfections())

    body_xml = "\n        ".join(geoms)
    lights_xml = gen_lights()
    template = f"""<mujoco model="warehouse">
    <compiler angle="degree" coordinate="local" autolimits="true"/>
    <option timestep="0.005" gravity="0 0 -9.81"/>

    <default>
        <default class="env_visual">
            <geom contype="0" conaffinity="0" group="2" density="0"/>
        </default>
        <default class="env_solid">
            <geom contype="1" conaffinity="1" group="3" rgba="0.4 0.4 0.4 0.25" friction="1 0.005 0.0001"/>
        </default>
    </default>

    <asset>
        <texture name="grid" type="2d" builtin="checker" rgb1=".2 .2 .2" rgb2=".3 .3 .3" width="512" height="512" mark="edge" markrgb=".4 .4 .4"/>
        <texture name="sky" type="skybox" builtin="gradient" rgb1=".1 .1 .1" rgb2="0 0 0" width="512" height="512"/>
        <material name="mat_floor"      texture="grid" texrepeat="22 14" texuniform="true" reflectance="0.2"/>
        <material name="mat_floor_wear" rgba="0.1 0.1 0.1 0.3" specular="0" shininess="0"/>
        <material name="mat_wall"       rgba="0.6 0.6 0.65 1" specular="0.1" shininess="0.1"/>
        <material name="mat_shelf_red"  rgba="0.6 0.1 0.1 1" specular="0.8" shininess="0.8"/>
        <material name="mat_box_yellow" rgba="0.8 0.6 0.2 1" specular="0.1" shininess="0.1"/>
        <material name="mat_beam"       rgba="0.3 0.3 0.35 1" specular="0.9" shininess="0.9"/>
        <material name="mat_pallet"     rgba="0.4 0.3 0.2 1" specular="0.05"/>
        <material name="mat_pod"        rgba="0.8 0.4 0.1 1" specular="0.2"/>
        <material name="mat_pod_base"   rgba="0.15 0.15 0.17 1" specular="0.5"/>
        <material name="mat_conveyor"   rgba="0.1 0.1 0.12 1" specular="0.8" shininess="0.8"/>
        <material name="mat_charge"     rgba="0.05 0.4 0.7 1" specular="0.8"/>
        <material name="mat_marking"    rgba="0.8 0.7 0.0 1" specular="0.3" shininess="0.3"/>
        <material name="mat_table"      rgba="0.5 0.5 0.55 1" specular="0.4"/>
    </asset>

    <worldbody>
        {lights_xml}
        <geom name="floor" type="plane" size="{ARENA_HX} {ARENA_HY} 0.5" material="mat_floor" pos="0 0 0"/>
        {body_xml}
    </worldbody>
</mujoco>
"""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(template)
    print(f"Wrote {OUTPUT} ({len(geoms)} geoms)")


if __name__ == "__main__":
    main()
