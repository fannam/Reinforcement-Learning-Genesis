from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class SineTarget:
    joint: str
    amplitude: float
    frequency: float
    phase: float = 0.0
    bias: float = 0.0

    def value(self, t: float) -> float:
        return self.bias + self.amplitude * math.sin(self.frequency * t + self.phase)


def default_modular_gait() -> list[SineTarget]:
    """Simple named-joint pose wave for the modular humanoid."""
    return [
        SineTarget("abdomen_yaw", amplitude=0.06, frequency=0.7),
        SineTarget("abdomen_roll", amplitude=0.04, frequency=0.9),
        SineTarget("abdomen_pitch", amplitude=0.08, frequency=0.8),
        SineTarget("neck_yaw", amplitude=0.15, frequency=0.5),
        SineTarget("neck_pitch", amplitude=0.08, frequency=0.6),

        SineTarget("shoulder_yaw_right", amplitude=0.18, frequency=1.2),
        SineTarget("shoulder_roll_right", amplitude=0.15, frequency=1.1),
        SineTarget("shoulder_pitch_right", amplitude=0.32, frequency=1.4),
        SineTarget("forearm_yaw_right", amplitude=0.16, frequency=1.3),
        SineTarget("elbow_pitch_right", amplitude=0.18, frequency=1.4, bias=-0.65),
        SineTarget("wrist_yaw_right", amplitude=0.12, frequency=1.4),
        SineTarget("wrist_pitch_right", amplitude=0.10, frequency=1.5),
        SineTarget("thumb_abduction_right", amplitude=0.08, frequency=1.6, bias=0.15),
        SineTarget("thumb_flexion_right", amplitude=0.12, frequency=1.6, bias=0.25),
        SineTarget("index_flexion_right", amplitude=0.12, frequency=1.6, bias=0.22),
        SineTarget("index_tip_right", amplitude=0.10, frequency=1.6, bias=0.18),
        SineTarget("middle_flexion_right", amplitude=0.12, frequency=1.6, bias=0.22),
        SineTarget("middle_tip_right", amplitude=0.10, frequency=1.6, bias=0.18),

        SineTarget("shoulder_yaw_left", amplitude=-0.18, frequency=1.2),
        SineTarget("shoulder_roll_left", amplitude=-0.15, frequency=1.1),
        SineTarget("shoulder_pitch_left", amplitude=-0.32, frequency=1.4),
        SineTarget("forearm_yaw_left", amplitude=-0.16, frequency=1.3),
        SineTarget("elbow_pitch_left", amplitude=-0.18, frequency=1.4, bias=-0.65),
        SineTarget("wrist_yaw_left", amplitude=-0.12, frequency=1.4),
        SineTarget("wrist_pitch_left", amplitude=-0.10, frequency=1.5),
        SineTarget("thumb_abduction_left", amplitude=-0.08, frequency=1.6, bias=-0.15),
        SineTarget("thumb_flexion_left", amplitude=0.12, frequency=1.6, bias=0.25),
        SineTarget("index_flexion_left", amplitude=0.12, frequency=1.6, bias=0.22),
        SineTarget("index_tip_left", amplitude=0.10, frequency=1.6, bias=0.18),
        SineTarget("middle_flexion_left", amplitude=0.12, frequency=1.6, bias=0.22),
        SineTarget("middle_tip_left", amplitude=0.10, frequency=1.6, bias=0.18),

        SineTarget("hip_yaw_right", amplitude=0.06, frequency=1.0),
        SineTarget("hip_roll_right", amplitude=0.05, frequency=1.1),
        SineTarget("hip_pitch_right", amplitude=0.18, frequency=1.2),
        SineTarget("knee_pitch_right", amplitude=0.16, frequency=1.2, bias=-0.22),
        SineTarget("ankle_roll_right", amplitude=0.04, frequency=1.1),
        SineTarget("ankle_pitch_right", amplitude=0.07, frequency=1.2),
        SineTarget("toe_pitch_right", amplitude=0.05, frequency=1.2),

        SineTarget("hip_yaw_left", amplitude=-0.06, frequency=1.0),
        SineTarget("hip_roll_left", amplitude=-0.05, frequency=1.1),
        SineTarget("hip_pitch_left", amplitude=-0.18, frequency=1.2),
        SineTarget("knee_pitch_left", amplitude=-0.16, frequency=1.2, bias=-0.22),
        SineTarget("ankle_roll_left", amplitude=-0.04, frequency=1.1),
        SineTarget("ankle_pitch_left", amplitude=-0.07, frequency=1.2),
        SineTarget("toe_pitch_left", amplitude=-0.05, frequency=1.2),
    ]
