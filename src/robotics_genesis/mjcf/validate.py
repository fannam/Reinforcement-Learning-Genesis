from __future__ import annotations

from pathlib import Path

from .parse import ASSET_FILE_TAGS, ONE_DOF_JOINT_TYPES, iter_mjcf_elements


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
