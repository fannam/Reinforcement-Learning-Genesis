#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from robotics_genesis.controllers import HoverConfig, HoverController, WaypointMission
from robotics_genesis.paths import project_path
from robotics_genesis.viewer_env import configure_pyglet_options, configure_viewer_environment
from robotics_genesis.xml_robot import prepare_mjcf_for_genesis


def strip_world_decorations(src: Path, dst: Path) -> Path:
    """Drop top-level <geom name='floor'> and <light> from worldbody so
    a robot MJCF can be loaded into another scene without duplicate floor/lights."""
    tree = ET.parse(src)
    root = tree.getroot()
    wb = root.find("worldbody")
    if wb is not None:
        for child in list(wb):
            if child.tag == "light":
                wb.remove(child)
            elif child.tag == "geom" and child.attrib.get("name") == "floor":
                wb.remove(child)
    dst.parent.mkdir(parents=True, exist_ok=True)
    tree.write(dst, encoding="utf-8", xml_declaration=False)
    return dst


def _cuda_available() -> bool:
    try:
        import torch
    except ImportError:
        return False
    return torch.cuda.is_available()


def _select_backend(gs, name: str):
    normalized = name.strip().lower()
    if normalized in ("gpu", "cuda"):
        if not _cuda_available():
            print("[run_warehouse] CUDA not available, falling back to CPU backend.")
            return gs.cpu
        return gs.gpu
    if normalized == "cpu":
        return gs.cpu
    raise ValueError("backend must be 'cpu' or 'gpu'")


def _resolve_mission_log(path: str) -> Path:
    log_path = Path(path)
    if not log_path.is_absolute():
        log_path = (
            project_path("outputs", "logs", log_path.name)
            if len(log_path.parts) == 1
            else PROJECT_ROOT / log_path
        )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    return log_path


def _to_numpy(value):
    try:
        return value.detach().cpu().numpy()
    except AttributeError:
        return value


def _count_valid_contacts(contact_data: dict) -> int:
    valid_mask = contact_data.get("valid_mask")
    if valid_mask is None:
        return 0
    return int(_to_numpy(valid_mask).sum())


def _is_out_of_bounds(pos) -> bool:
    x, y, z = (float(v) for v in pos)
    return x < -22.0 or x > 22.0 or y < -14.0 or y > 14.0 or z < 0.05 or z > 7.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the drone in the warehouse Genesis scene.")
    parser.add_argument("--world", default="worlds/warehouse.xml", help="Path to warehouse MJCF.")
    parser.add_argument("--drone", default="robots/drone/drone.xml",
                        help="Drone MJCF spawned in warehouse. Pass empty string to disable.")
    parser.add_argument("--drone-pos", nargs=3, type=float, default=[-2.0, -2.0, 1.5],
                        metavar=("X", "Y", "Z"),
                        help="Drone spawn position inside warehouse.")
    parser.add_argument("--steps", type=int, default=int(os.getenv("STEPS", "2000")))
    parser.add_argument("--viewer", action=argparse.BooleanOptionalAction,
                        default=os.getenv("SHOW_VIEWER", "0") == "1",
                        help="Show Genesis viewer (default off unless SHOW_VIEWER=1).")
    parser.add_argument("--backend", default=os.getenv("GENESIS_BACKEND", "gpu"), choices=("cpu", "gpu"))
    parser.add_argument("--hover", action=argparse.BooleanOptionalAction, default=True,
                        help="Run a hover controller on the drone (default on).")
    parser.add_argument("--target-pos", nargs=3, type=float, default=None,
                        metavar=("X", "Y", "Z"),
                        help="Hover target position. Defaults to spawn position.")
    parser.add_argument("--hover-log-every", type=int, default=200,
                        help="Print drone state every N steps (0 to disable).")
    parser.add_argument("--follow", action=argparse.BooleanOptionalAction, default=True,
                        help="Third-person camera follows drone (default on).")
    parser.add_argument("--follow-smoothing", type=float, default=0.92,
                        help="Camera follow smoothing in (0,1). Higher = smoother / laggier.")
    parser.add_argument("--waypoint", nargs=3, action="append", type=float, default=[],
                        metavar=("X", "Y", "Z"),
                        help="Mission waypoint. Repeat for multi-waypoint missions.")
    parser.add_argument("--waypoint-radius", type=float, default=0.25,
                        help="Distance threshold for waypoint completion.")
    parser.add_argument("--waypoint-dwell-steps", type=int, default=20,
                        help="Consecutive in-radius steps required before advancing.")
    parser.add_argument("--stop-on-complete", action="store_true",
                        help="Stop simulation when all waypoints are complete.")
    parser.add_argument("--mission-log", default=None,
                        help="Optional CSV log path. Bare filenames are written under outputs/logs/.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.waypoint and not args.hover:
        raise SystemExit("--waypoint requires --hover because waypoints are tracked by HoverController.")

    world_path = Path(args.world)
    if not world_path.is_absolute():
        world_path = PROJECT_ROOT / world_path
    world_path = world_path.resolve()

    configure_viewer_environment(args.viewer)
    if args.viewer:
        import pyglet
        configure_pyglet_options(pyglet)

    import genesis as gs

    world_genesis = prepare_mjcf_for_genesis(world_path, project_path("outputs", "generated"))

    drone_genesis = None
    if args.drone:
        drone_path = Path(args.drone)
        if not drone_path.is_absolute():
            drone_path = PROJECT_ROOT / drone_path
        drone_prepared = prepare_mjcf_for_genesis(drone_path.resolve(), project_path("outputs", "generated"))
        drone_genesis = strip_world_decorations(
            drone_prepared,
            project_path("outputs", "generated") / f"{drone_prepared.stem}.scene_ready.xml",
        )

    gs.init(backend=_select_backend(gs, args.backend))

    viewer_options = None
    if args.viewer:
        run_in_thread = os.getenv("GENESIS_VIEWER_THREAD", "1") != "0"
        viewer_options = gs.options.ViewerOptions(
            run_in_thread=run_in_thread,
            res=(1280, 800),
            camera_pos=(-3.5, -3.5, 2.5),
            camera_lookat=(0.0, 0.0, 0.0),
            camera_fov=50,
        )

    rigid_options = gs.options.RigidOptions(enable_self_collision=False)
    scene = gs.Scene(
        show_viewer=args.viewer,
        viewer_options=viewer_options,
        rigid_options=rigid_options,
    )
    warehouse_material = gs.materials.Rigid(sdf_cell_size=0.05, sdf_max_res=32)
    warehouse_entity = scene.add_entity(
        gs.morphs.MJCF(file=str(world_genesis)),
        material=warehouse_material,
    )
    drone_entity = None
    if drone_genesis is not None:
        drone_entity = scene.add_entity(gs.morphs.MJCF(
            file=str(drone_genesis),
            pos=tuple(args.drone_pos),
        ))
    scene.build()

    controller = None
    target = None
    mission = None
    mission_status = None
    if args.hover and drone_entity is not None:
        spawn_pos = drone_entity.get_pos().detach().cpu().numpy()
        if args.waypoint:
            mission = WaypointMission(
                args.waypoint,
                radius=args.waypoint_radius,
                dwell_steps=args.waypoint_dwell_steps,
            )
            target = mission.active_target
        else:
            target = (
                tuple(float(v) for v in args.target_pos)
                if args.target_pos is not None
                else tuple(float(v) for v in spawn_pos)
            )
        controller = HoverController(drone_entity, HoverConfig(), target_pos=target)

    if args.viewer and args.follow and drone_entity is not None and scene.viewer is not None:
        scene.viewer.follow_entity(drone_entity, smoothing=args.follow_smoothing)

    log_file = None
    log_writer = None
    if args.mission_log:
        log_file = _resolve_mission_log(args.mission_log).open("w", newline="")
        log_writer = csv.DictWriter(
            log_file,
            fieldnames=[
                "step",
                "x",
                "y",
                "z",
                "target_index",
                "target_x",
                "target_y",
                "target_z",
                "target_error",
                "reached_count",
                "mission_completed",
                "contacts",
                "crashed",
                "fz",
                "tau_x",
                "tau_y",
                "tau_z",
            ],
        )
        log_writer.writeheader()

    total_contacts = 0
    crashed = False
    final_pos = None
    final_info = None

    for step_i in range(args.steps):
        if controller is not None:
            final_info = controller.step()
        scene.step()

        if drone_entity is not None:
            final_pos = _to_numpy(drone_entity.get_pos())
            contacts_this_step = _count_valid_contacts(drone_entity.get_contacts(with_entity=warehouse_entity))
            total_contacts += contacts_this_step
            crashed = crashed or contacts_this_step > 0 or _is_out_of_bounds(final_pos)
        else:
            contacts_this_step = 0

        if mission is not None and final_pos is not None:
            mission_status = mission.update(final_pos)
            if mission_status.active_target is not None:
                target = mission_status.active_target
                controller.set_target_pos(mission_status.active_target)
            else:
                target = mission.waypoints[-1]
                if args.stop_on_complete:
                    controller.set_target_pos(final_pos)

        if args.hover_log_every and step_i % args.hover_log_every == 0 and controller is not None and final_info:
            pos = final_pos if final_pos is not None else final_info["pos"]
            fz = final_info["fz"]
            tau = final_info["tau"]
            log_target = target if target is not None else tuple(float(v) for v in pos)
            err = (log_target[0] - pos[0], log_target[1] - pos[1], log_target[2] - pos[2])
            print(f"[hover] step={step_i:5d}  pos=({pos[0]:+.2f},{pos[1]:+.2f},{pos[2]:+.2f})  "
                  f"err=({err[0]:+.2f},{err[1]:+.2f},{err[2]:+.2f})  "
                  f"fz={fz:5.2f}  tau=[{tau[0]:+.2f} {tau[1]:+.2f} {tau[2]:+.2f}]  "
                  f"contacts={contacts_this_step}")

        if log_writer is not None and final_pos is not None:
            log_target = target if target is not None else tuple(float(v) for v in final_pos)
            target_error = float(((final_pos[0] - log_target[0]) ** 2
                                  + (final_pos[1] - log_target[1]) ** 2
                                  + (final_pos[2] - log_target[2]) ** 2) ** 0.5)
            tau = final_info["tau"] if final_info is not None else (0.0, 0.0, 0.0)
            log_writer.writerow({
                "step": step_i,
                "x": float(final_pos[0]),
                "y": float(final_pos[1]),
                "z": float(final_pos[2]),
                "target_index": mission_status.target_index if mission_status is not None else "",
                "target_x": float(log_target[0]),
                "target_y": float(log_target[1]),
                "target_z": float(log_target[2]),
                "target_error": target_error,
                "reached_count": mission_status.reached_count if mission_status is not None else "",
                "mission_completed": mission_status.completed if mission_status is not None else "",
                "contacts": contacts_this_step,
                "crashed": crashed,
                "fz": final_info["fz"] if final_info is not None else 0.0,
                "tau_x": float(tau[0]),
                "tau_y": float(tau[1]),
                "tau_z": float(tau[2]),
            })

        if mission_status is not None and mission_status.completed and args.stop_on_complete:
            break

    if log_file is not None:
        print(f"[mission] wrote log: {log_file.name}")
        log_file.close()

    if final_pos is not None:
        reached = mission_status.reached_count if mission_status is not None else 0
        completed = mission_status.completed if mission_status is not None else False
        final_target = target if target is not None else tuple(float(v) for v in final_pos)
        final_error = float(((final_pos[0] - final_target[0]) ** 2
                             + (final_pos[1] - final_target[1]) ** 2
                             + (final_pos[2] - final_target[2]) ** 2) ** 0.5)
        print(f"[summary] completed={completed} reached={reached} contacts={total_contacts} "
              f"crashed={crashed} final_error={final_error:.3f} "
              f"final_pos=({final_pos[0]:+.2f},{final_pos[1]:+.2f},{final_pos[2]:+.2f})")


if __name__ == "__main__":
    main()
