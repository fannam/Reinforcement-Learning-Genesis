from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET


ONE_DOF_JOINT_TYPES = {"hinge", "slide"}
ASSET_FILE_TAGS = {"mesh", "texture", "hfield"}
INCLUDE_WRAPPER_TAGS = {"mujoco", "robot_part"}


def parse_mjcf(xml_path: str | Path) -> ET.ElementTree:
    path = Path(xml_path)
    if not path.exists():
        raise FileNotFoundError(f"Robot XML not found: {path}")

    tree = ET.parse(path)
    root = tree.getroot()
    if root.tag != "mujoco":
        raise ValueError(f"Expected root tag <mujoco>, got <{root.tag}>")
    return tree


def _include_path(base_dir: Path, include_node: ET.Element) -> Path:
    file_name = include_node.attrib.get("file")
    if not file_name:
        raise ValueError("<include> tag is missing required 'file' attribute")

    path = Path(file_name)
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()


def _iter_elements_with_includes(
    node: ET.Element,
    base_dir: Path,
    include_stack: tuple[Path, ...],
):
    if node.tag == "include":
        include_path = _include_path(base_dir, node)
        if include_path in include_stack:
            chain = " -> ".join(str(path) for path in (*include_stack, include_path))
            raise ValueError(f"Circular MJCF include detected: {chain}")

        include_tree = ET.parse(include_path)
        include_root = include_tree.getroot()
        include_base_dir = include_path.parent
        next_stack = (*include_stack, include_path)

        children = list(include_root) if include_root.tag in INCLUDE_WRAPPER_TAGS else [include_root]
        for child in children:
            yield from _iter_elements_with_includes(child, include_base_dir, next_stack)
        return

    yield node, base_dir

    for child in node:
        yield from _iter_elements_with_includes(child, base_dir, include_stack)


def iter_mjcf_elements(xml_path: str | Path):
    path = Path(xml_path).resolve()
    root = parse_mjcf(path).getroot()
    yield from _iter_elements_with_includes(root, path.parent, (path,))


def mjcf_has_includes(xml_path: str | Path) -> bool:
    path = Path(xml_path).resolve()
    root = parse_mjcf(path).getroot()
    return any(node.tag == "include" for node in root.iter())
