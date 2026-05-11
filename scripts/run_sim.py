#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from robotics_genesis.simulation import run_genesis_simulation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the legacy single-robot Genesis simulation from an MJCF XML robot file."
    )
    parser.add_argument(
        "--robot",
        default="assets/robots/humanoid/humanoid.xml",
        help="Path to robot MJCF XML. Use scripts/run_warehouse.py for the primary drone + warehouse workflow.",
    )
    parser.add_argument("--steps", type=int, default=int(os.getenv("STEPS", "1000")), help="Number of simulation steps.")
    parser.add_argument("--viewer", action="store_true", default=os.getenv("SHOW_VIEWER", "0") == "1", help="Show Genesis viewer.")
    parser.add_argument("--backend", default=os.getenv("GENESIS_BACKEND", "gpu"), choices=("cpu", "gpu"), help="Genesis backend (default gpu, auto-fallback to cpu if CUDA unavailable).")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    robot_xml = (PROJECT_ROOT / args.robot).resolve() if not Path(args.robot).is_absolute() else Path(args.robot)
    run_genesis_simulation(robot_xml, steps=args.steps, show_viewer=args.viewer, backend=args.backend)


if __name__ == "__main__":
    main()
