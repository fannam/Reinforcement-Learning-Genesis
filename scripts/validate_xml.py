#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from robotics_genesis.mjcf import get_1d_joint_names, parse_mjcf, validate_asset_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an MJCF XML robot file.")
    parser.add_argument("xml", help="Path to MJCF XML file.")
    parser.add_argument("--mujoco", action="store_true", help="Also validate by loading the model with mujoco.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    xml_path = Path(args.xml)
    if not xml_path.is_absolute():
        xml_path = PROJECT_ROOT / xml_path

    try:
        parse_mjcf(xml_path)
        joints = get_1d_joint_names(xml_path)
        missing_assets = validate_asset_files(xml_path)
    except Exception as exc:
        print(f"XML validation failed: {exc}", file=sys.stderr)
        return 1

    if missing_assets:
        print("Missing referenced assets:", file=sys.stderr)
        for asset in missing_assets:
            print(f"  - {asset}", file=sys.stderr)
        return 1

    if args.mujoco:
        try:
            import mujoco

            mujoco.MjModel.from_xml_path(str(xml_path))
        except Exception as exc:
            print(f"MuJoCo model load failed: {exc}", file=sys.stderr)
            return 1

    print(f"OK: {xml_path}")
    print(f"1D joints ({len(joints)}): {', '.join(joints) if joints else 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
