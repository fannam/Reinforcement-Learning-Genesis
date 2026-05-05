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


def test_basic_arm_robot_has_expected_joints():
    robot_xml = PROJECT_ROOT / "robots" / "basic_arm" / "basic_arm.xml"
    joint_names = get_1d_joint_names(robot_xml)

    assert joint_names == ["shoulder", "elbow"]


def test_basic_humanoid_robot_has_expected_joints():
    robot_xml = PROJECT_ROOT / "robots" / "basic_humanoid" / "basic_humanoid.xml"
    joint_names = get_1d_joint_names(robot_xml)

    assert "abdomen_y" in joint_names
    assert "shoulder_right" in joint_names
    assert "elbow_left" in joint_names
    assert "hip_right" in joint_names
    assert "knee_left" in joint_names
    assert "ankle_left" in joint_names


def test_modular_humanoid_robot_resolves_included_joints():
    robot_xml = PROJECT_ROOT / "robots" / "modular_humanoid" / "modular_humanoid.xml"
    joint_names = get_1d_joint_names(robot_xml)

    assert "abdomen_pitch" in joint_names
    assert "shoulder_pitch_right" in joint_names
    assert "wrist_pitch_left" in joint_names
    assert "hip_pitch_right" in joint_names
    assert "ankle_pitch_left" in joint_names
