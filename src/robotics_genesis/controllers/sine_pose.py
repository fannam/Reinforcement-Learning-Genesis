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
        SineTarget("abdomen_pitch", amplitude=0.08, frequency=0.8),
        SineTarget("shoulder_pitch_right", amplitude=0.35, frequency=1.5),
        SineTarget("elbow_right", amplitude=0.20, frequency=1.5, bias=-0.65),
        SineTarget("wrist_pitch_right", amplitude=0.12, frequency=1.5),
        SineTarget("shoulder_pitch_left", amplitude=-0.35, frequency=1.5),
        SineTarget("elbow_left", amplitude=-0.20, frequency=1.5, bias=-0.65),
        SineTarget("wrist_pitch_left", amplitude=-0.12, frequency=1.5),
        SineTarget("hip_pitch_right", amplitude=0.20, frequency=1.2),
        SineTarget("knee_right", amplitude=0.18, frequency=1.2, bias=-0.25),
        SineTarget("ankle_pitch_right", amplitude=0.08, frequency=1.2),
        SineTarget("hip_pitch_left", amplitude=-0.20, frequency=1.2),
        SineTarget("knee_left", amplitude=-0.18, frequency=1.2, bias=-0.25),
        SineTarget("ankle_pitch_left", amplitude=-0.08, frequency=1.2),
    ]
