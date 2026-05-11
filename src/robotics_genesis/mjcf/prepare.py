from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

from .parse import ASSET_FILE_TAGS, INCLUDE_WRAPPER_TAGS, _include_path, mjcf_has_includes, parse_mjcf


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
    """Write MJCF with all <include> tags expanded.

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
