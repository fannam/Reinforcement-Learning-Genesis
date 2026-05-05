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


def _clone_with_expanded_includes(
    node: ET.Element,
    base_dir: Path,
    include_stack: tuple[Path, ...],
) -> list[ET.Element]:
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
        expanded: list[ET.Element] = []
        for child in children:
            expanded.extend(_clone_with_expanded_includes(child, include_base_dir, next_stack))
        return expanded

    attrib = dict(node.attrib)
    if node.tag in ASSET_FILE_TAGS and "file" in attrib:
        asset_file = Path(attrib["file"])
        if not asset_file.is_absolute():
            attrib["file"] = str((base_dir / asset_file).resolve())

    cloned = ET.Element(node.tag, attrib)
    cloned.text = node.text
    cloned.tail = node.tail

    for child in node:
        for expanded_child in _clone_with_expanded_includes(child, base_dir, include_stack):
            cloned.append(expanded_child)

    return [cloned]


def write_expanded_mjcf(xml_path: str | Path, output_path: str | Path) -> Path:
    """Write an MJCF file with all <include> tags expanded.

    Genesis 0.4.x loads MJCF through mujoco.MjModel.from_xml_string in some paths,
    which loses the original XML base directory for relative includes. The expanded
    file avoids that issue and keeps asset file references absolute.
    """
    source_path = Path(xml_path).resolve()
    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    root = parse_mjcf(source_path).getroot()
    expanded_root = _clone_with_expanded_includes(root, source_path.parent, (source_path,))[0]
    ET.indent(expanded_root, space="  ")
    ET.ElementTree(expanded_root).write(output, encoding="utf-8", xml_declaration=False)
    return output


def prepare_mjcf_for_genesis(xml_path: str | Path, output_dir: str | Path) -> Path:
    path = Path(xml_path).resolve()
    if not mjcf_has_includes(path):
        return path

    output_path = Path(output_dir) / f"{path.stem}.expanded.xml"
    return write_expanded_mjcf(path, output_path)


def get_1d_joint_names(xml_path: str | Path) -> list[str]:
    """Return hinge/slide joint names in MJCF document order."""
    names: list[str] = []

    for joint, _ in iter_mjcf_elements(xml_path):
        if joint.tag != "joint":
            continue

        joint_type = joint.attrib.get("type", "hinge")
        name = joint.attrib.get("name")
        if name and joint_type in ONE_DOF_JOINT_TYPES:
            names.append(name)

    return names


def get_asset_files(xml_path: str | Path) -> list[Path]:
    """Return asset file paths referenced by mesh, texture, and hfield tags."""
    assets: list[Path] = []

    for node, base_dir in iter_mjcf_elements(xml_path):
        if node.tag not in ASSET_FILE_TAGS:
            continue

        file_name = node.attrib.get("file")
        if file_name:
            assets.append((base_dir / file_name).resolve())

    return assets


def validate_asset_files(xml_path: str | Path) -> list[Path]:
    return [asset for asset in get_asset_files(xml_path) if not asset.exists()]
