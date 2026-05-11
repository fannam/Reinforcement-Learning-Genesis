from pathlib import Path
import os
import subprocess
import sys
from xml.etree import ElementTree as ET

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]

from robotics_genesis.controllers import HoverConfig, HoverController, WaypointMission
from robotics_genesis.xml_robot import get_1d_joint_names, parse_mjcf
from scripts.run_warehouse import strip_world_decorations


DRONE_XML = PROJECT_ROOT / "assets" / "robots" / "drone" / "drone.xml"
WAREHOUSE_XML = PROJECT_ROOT / "assets" / "worlds" / "warehouse.xml"


def test_drone_xml_is_valid_and_free_body():
    tree = parse_mjcf(DRONE_XML)
    root = tree.getroot()
    drone_core = root.find("./worldbody/body[@name='drone_core']")

    assert drone_core is not None
    assert drone_core.find("./freejoint[@name='root']") is not None
    assert get_1d_joint_names(DRONE_XML) == []


def test_warehouse_xml_is_valid_and_contains_required_zones():
    tree = parse_mjcf(WAREHOUSE_XML)
    names = {
        geom.attrib["name"]
        for geom in tree.getroot().findall(".//geom")
        if "name" in geom.attrib
    }

    required_prefixes = [
        "wall_",
        "rack_",
        "cross_",
        "dock_",
        "pod_",
        "pack_table_",
        "conveyor_",
        "charge_pad_",
        "beam_",
        "hanging_",
    ]
    for prefix in required_prefixes:
        assert any(name.startswith(prefix) for name in names), prefix


def test_strip_world_decorations_removes_drone_floor_and_lights(tmp_path):
    output = strip_world_decorations(DRONE_XML, tmp_path / "drone.scene_ready.xml")
    root = ET.parse(output).getroot()
    worldbody = root.find("worldbody")

    assert worldbody is not None
    assert worldbody.find("./geom[@name='floor']") is None
    assert worldbody.findall("./light") == []
    assert worldbody.find("./body[@name='drone_core']") is not None


def test_hover_controller_wrench_changes_with_position_error():
    controller = HoverController.__new__(HoverController)
    controller.config = HoverConfig()
    controller.target_pos = np.array([1.0, 0.0, 2.0], dtype=np.float32)
    controller.target_yaw = 0.0
    controller.fz_max = controller.config.fz_max_factor * controller.config.mass * controller.config.gravity

    hover_fz, hover_tau = controller.compute_wrench(
        pos=np.array([1.0, 0.0, 2.0], dtype=np.float32),
        quat_wxyz=np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32),
        lin_vel=np.zeros(3, dtype=np.float32),
        ang_vel_world=np.zeros(3, dtype=np.float32),
    )
    offset_fz, offset_tau = controller.compute_wrench(
        pos=np.array([0.0, 0.0, 1.5], dtype=np.float32),
        quat_wxyz=np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32),
        lin_vel=np.zeros(3, dtype=np.float32),
        ang_vel_world=np.zeros(3, dtype=np.float32),
    )

    assert np.isclose(hover_fz, controller.config.mass * controller.config.gravity)
    assert np.allclose(hover_tau, np.zeros(3, dtype=np.float32))
    assert offset_fz > hover_fz
    assert offset_tau[1] > 0.0


def test_waypoint_mission_advances_after_radius_and_dwell():
    mission = WaypointMission(
        waypoints=[(0.0, 0.0, 1.0), (1.0, 0.0, 1.0)],
        radius=0.25,
        dwell_steps=2,
    )

    first = mission.update((0.0, 0.0, 1.0))
    second = mission.update((0.0, 0.0, 1.0))
    third = mission.update((1.0, 0.0, 1.0))
    fourth = mission.update((1.0, 0.0, 1.0))

    assert first.reached_count == 0
    assert second.reached_count == 1
    assert second.active_target == (1.0, 0.0, 1.0)
    assert third.completed is False
    assert fourth.completed is True


@pytest.mark.skipif(os.getenv("RUN_GENESIS_TESTS") != "1", reason="Genesis smoke tests are opt-in.")
def test_genesis_warehouse_hover_smoke():
    command = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "run_warehouse.py"),
        "--steps",
        "20",
        "--backend",
        "cpu",
        "--hover-log-every",
        "0",
    ]
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env={**os.environ, "SHOW_VIEWER": "0", "GENESIS_BACKEND": "cpu"},
        check=False,
        text=True,
        capture_output=True,
        timeout=60,
    )

    assert completed.returncode == 0, completed.stderr
    assert "[summary]" in completed.stdout
