from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from robotics_genesis.xml_robot import get_1d_joint_names, parse_mjcf, prepare_mjcf_for_genesis


def test_modular_humanoid_xml_is_valid():
    robot_xml = PROJECT_ROOT / "robots" / "modular_humanoid" / "modular_humanoid.xml"
    parse_mjcf(robot_xml)


def test_modular_humanoid_robot_resolves_included_joints():
    robot_xml = PROJECT_ROOT / "robots" / "modular_humanoid" / "modular_humanoid.xml"
    joint_names = get_1d_joint_names(robot_xml)

    assert len(joint_names) == 45
    assert "abdomen_yaw" in joint_names
    assert "abdomen_roll" in joint_names
    assert "abdomen_pitch" in joint_names
    assert "neck_yaw" in joint_names
    assert "neck_pitch" in joint_names
    assert "shoulder_yaw_right" in joint_names
    assert "shoulder_roll_right" in joint_names
    assert "shoulder_pitch_right" in joint_names
    assert "forearm_yaw_right" in joint_names
    assert "elbow_pitch_right" in joint_names
    assert "wrist_pitch_left" in joint_names
    assert "thumb_flexion_right" in joint_names
    assert "index_tip_left" in joint_names
    assert "hip_yaw_right" in joint_names
    assert "hip_roll_left" in joint_names
    assert "hip_pitch_right" in joint_names
    assert "knee_pitch_left" in joint_names
    assert "ankle_roll_right" in joint_names
    assert "ankle_pitch_left" in joint_names
    assert "toe_pitch_right" in joint_names


def test_modular_humanoid_expands_for_genesis():
    robot_xml = PROJECT_ROOT / "robots" / "modular_humanoid" / "modular_humanoid.xml"
    expanded_xml = prepare_mjcf_for_genesis(robot_xml, PROJECT_ROOT / "outputs" / "generated")

    assert expanded_xml.exists()
    assert expanded_xml.name == "modular_humanoid.expanded.xml"
