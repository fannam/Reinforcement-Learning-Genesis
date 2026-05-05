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
    """Simple named-joint pose wave for the starter humanoid."""
    return [
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
