from __future__ import annotations

import math
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np


SUPPORTED_GEOM_TYPES = {"box", "cylinder", "sphere"}


def _parse_vec(attr: str | None, n: int | None = None) -> tuple[float, ...] | None:
    if attr is None:
        return None
    parts = attr.split()
    if n is not None and len(parts) != n:
        raise ValueError(f"Expected {n} floats, got {attr!r}")
    return tuple(float(p) for p in parts)


def _geom_world_aabb(geom: ET.Element) -> tuple[float, float, float, float, float, float] | None:
    """Return (xmin, ymin, zmin, xmax, ymax, zmax) for a geom or None to skip.

    Assumes geom is a direct worldbody child (no parent body transform). Handles
    Z-only rotations conservatively: rotated box AABB is expanded by the rotated
    extent on X/Y; cylinder/sphere are axis-symmetric and ignore rotation.
    """
    gtype = geom.attrib.get("type", "sphere")
    if gtype not in SUPPORTED_GEOM_TYPES:
        return None

    pos = _parse_vec(geom.attrib.get("pos", "0 0 0"), 3)
    size = _parse_vec(geom.attrib.get("size"))
    if pos is None or size is None:
        return None

    cx, cy, cz = pos

    if gtype == "box":
        if len(size) != 3:
            return None
        sx, sy, sz = size
        euler = geom.attrib.get("euler")
        if euler:
            ex, ey, ez = _parse_vec(euler, 3)
            theta = math.radians(ez)
            c, s = abs(math.cos(theta)), abs(math.sin(theta))
            hx = sx * c + sy * s
            hy = sx * s + sy * c
        else:
            hx, hy = sx, sy
        hz = sz
    elif gtype == "cylinder":
        if len(size) != 2:
            return None
        radius, half_height = size
        hx = hy = radius
        hz = half_height
    elif gtype == "sphere":
        if len(size) != 1:
            return None
        r = size[0]
        hx = hy = hz = r
    else:
        return None

    return (cx - hx, cy - hy, cz - hz, cx + hx, cy + hy, cz + hz)


def load_collision_aabbs(
    xml_path: str | Path,
    *,
    class_filter: str | None = "env_solid",
    skip_names: tuple[str, ...] = ("floor",),
) -> np.ndarray:
    """Parse MJCF and return Nx6 float32 array of world-space AABBs for
    collision geoms. Only direct worldbody children are considered.

    Args:
        xml_path: MJCF file path.
        class_filter: If set, only geoms with `class="<filter>"` are included.
            Pass None to include all geoms regardless of class.
        skip_names: Geom names to omit (floor by default).
    """
    path = Path(xml_path)
    tree = ET.parse(path)
    root = tree.getroot()
    worldbody = root.find("worldbody")
    if worldbody is None:
        return np.zeros((0, 6), dtype=np.float32)

    boxes: list[tuple[float, float, float, float, float, float]] = []
    for geom in worldbody.findall("geom"):
        if class_filter is not None and geom.attrib.get("class") != class_filter:
            continue
        if geom.attrib.get("name") in skip_names:
            continue
        aabb = _geom_world_aabb(geom)
        if aabb is not None:
            boxes.append(aabb)

    if not boxes:
        return np.zeros((0, 6), dtype=np.float32)
    return np.asarray(boxes, dtype=np.float32)


def point_inside_any(
    pos,
    aabbs: np.ndarray,
    margin: float = 0.0,
) -> bool:
    """Return True if pos lies inside any expanded AABB.

    aabbs shape: (N, 6) as returned by load_collision_aabbs.
    margin: positive number inflates each AABB symmetrically (e.g. drone radius).
    """
    if aabbs.size == 0:
        return False
    p = np.asarray(pos, dtype=np.float32).reshape(3)
    mins = aabbs[:, :3] - margin
    maxs = aabbs[:, 3:] + margin
    inside = np.all((p >= mins) & (p <= maxs), axis=1)
    return bool(np.any(inside))
