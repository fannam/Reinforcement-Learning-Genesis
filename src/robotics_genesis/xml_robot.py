from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET


ONE_DOF_JOINT_TYPES = {"hinge", "slide"}


def parse_mjcf(xml_path: str | Path) -> ET.ElementTree:
    path = Path(xml_path)
    if not path.exists():
        raise FileNotFoundError(f"Robot XML not found: {path}")

    tree = ET.parse(path)
    root = tree.getroot()
    if root.tag != "mujoco":
        raise ValueError(f"Expected root tag <mujoco>, got <{root.tag}>")
    return tree


def get_1d_joint_names(xml_path: str | Path) -> list[str]:
    """Return hinge/slide joint names in MJCF document order."""
    root = parse_mjcf(xml_path).getroot()
    names: list[str] = []

    for joint in root.iter("joint"):
        joint_type = joint.attrib.get("type", "hinge")
        name = joint.attrib.get("name")
        if name and joint_type in ONE_DOF_JOINT_TYPES:
            names.append(name)

    return names


def get_asset_files(xml_path: str | Path) -> list[Path]:
    """Return asset file paths referenced by mesh, texture, and hfield tags."""
    path = Path(xml_path)
    root = parse_mjcf(path).getroot()
    assets: list[Path] = []

    for tag in ("mesh", "texture", "hfield"):
        for node in root.iter(tag):
            file_name = node.attrib.get("file")
            if file_name:
                assets.append((path.parent / file_name).resolve())

    return assets


def validate_asset_files(xml_path: str | Path) -> list[Path]:
    return [asset for asset in get_asset_files(xml_path) if not asset.exists()]
