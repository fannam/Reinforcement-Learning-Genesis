from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


def strip_world_decorations(src: str | Path, dst: str | Path) -> Path:
    """Drop top-level <light> and <geom name='floor'> from worldbody so the
    robot MJCF can be loaded into another scene without duplicate floor/lights."""
    src_path = Path(src)
    dst_path = Path(dst)
    tree = ET.parse(src_path)
    root = tree.getroot()
    worldbody = root.find("worldbody")
    if worldbody is not None:
        for child in list(worldbody):
            if child.tag == "light":
                worldbody.remove(child)
            elif child.tag == "geom" and child.attrib.get("name") == "floor":
                worldbody.remove(child)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(dst_path, encoding="utf-8", xml_declaration=False)
    return dst_path
