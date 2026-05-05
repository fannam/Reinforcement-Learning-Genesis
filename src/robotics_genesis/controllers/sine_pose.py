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


def default_starter_gait() -> list[SineTarget]:
    """Simple named-joint pose wave for included starter robots."""
    return [
        SineTarget("shoulder", amplitude=0.55, frequency=1.4),
        SineTarget("elbow", amplitude=0.35, frequency=1.8, bias=-0.55),
        SineTarget("shoulder_right", amplitude=0.35, frequency=1.5),
        SineTarget("shoulder_pitch_right", amplitude=0.35, frequency=1.5),
        SineTarget("elbow_right", amplitude=0.20, frequency=1.5, bias=-0.65),
        SineTarget("wrist_pitch_right", amplitude=0.12, frequency=1.5),
        SineTarget("shoulder_left", amplitude=-0.35, frequency=1.5),
        SineTarget("shoulder_pitch_left", amplitude=-0.35, frequency=1.5),
        SineTarget("wrist_pitch_left", amplitude=-0.12, frequency=1.5),
        SineTarget("hip_right", amplitude=0.20, frequency=1.2),
        SineTarget("hip_pitch_right", amplitude=0.20, frequency=1.2),
        SineTarget("knee_right", amplitude=0.18, frequency=1.2, bias=-0.25),
        SineTarget("ankle_right", amplitude=0.08, frequency=1.2),
        SineTarget("ankle_pitch_right", amplitude=0.08, frequency=1.2),
        SineTarget("hip_left", amplitude=-0.20, frequency=1.2),
        SineTarget("hip_pitch_left", amplitude=-0.20, frequency=1.2),
        SineTarget("knee_left", amplitude=-0.18, frequency=1.2, bias=-0.25),
        SineTarget("ankle_left", amplitude=-0.08, frequency=1.2),
        SineTarget("ankle_pitch_left", amplitude=-0.08, frequency=1.2),
        SineTarget("abdomen_pitch", amplitude=0.08, frequency=0.8),
        SineTarget("abdomen_z", amplitude=0.12, frequency=1.2),
        SineTarget("abdomen_y", amplitude=0.08, frequency=0.8),
        SineTarget("abdomen_x", amplitude=0.08, frequency=0.8, phase=math.pi / 2),
        SineTarget("shoulder1_right", amplitude=0.55, frequency=2.0),
        SineTarget("shoulder2_right", amplitude=0.20, frequency=2.0, bias=-0.35),
        SineTarget("elbow_right", amplitude=0.25, frequency=2.0, bias=-0.70),
        SineTarget("shoulder1_left", amplitude=-0.55, frequency=2.0),
        SineTarget("shoulder2_left", amplitude=-0.20, frequency=2.0, bias=0.35),
        SineTarget("elbow_left", amplitude=-0.25, frequency=2.0, bias=-0.70),
    ]
