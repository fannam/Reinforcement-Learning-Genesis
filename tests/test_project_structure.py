from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from robotics_genesis.xml_robot import get_1d_joint_names, parse_mjcf


def test_starter_robot_xml_is_valid():
    robot_xml = PROJECT_ROOT / "robots" / "starter_humanoid" / "starter_humanoid.xml"
    parse_mjcf(robot_xml)


def test_starter_robot_has_expected_joints():
    robot_xml = PROJECT_ROOT / "robots" / "starter_humanoid" / "starter_humanoid.xml"
    joint_names = get_1d_joint_names(robot_xml)

    assert "abdomen_z" in joint_names
    assert "shoulder1_right" in joint_names
    assert "elbow_left" in joint_names
