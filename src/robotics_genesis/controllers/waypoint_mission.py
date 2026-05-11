from __future__ import annotations

from dataclasses import dataclass
from math import dist
from typing import Iterable, Sequence


Vector3 = tuple[float, float, float]


@dataclass(frozen=True)
class WaypointStatus:
    target_index: int
    active_target: Vector3 | None
    reached_count: int
    completed: bool
    advanced: bool
    distance: float
    dwell_count: int


class WaypointMission:
    """Radius-and-dwell waypoint queue for simple drone missions."""

    def __init__(
        self,
        waypoints: Iterable[Sequence[float]],
        *,
        radius: float = 0.25,
        dwell_steps: int = 20,
    ) -> None:
        self._waypoints: tuple[Vector3, ...] = tuple(
            (float(point[0]), float(point[1]), float(point[2])) for point in waypoints
        )
        if not self._waypoints:
            raise ValueError("WaypointMission requires at least one waypoint.")
        if radius <= 0:
            raise ValueError("waypoint radius must be positive.")
        if dwell_steps < 1:
            raise ValueError("waypoint dwell steps must be at least 1.")

        self.radius = float(radius)
        self.dwell_steps = int(dwell_steps)
        self.target_index = 0
        self.reached_count = 0
        self.dwell_count = 0
        self.completed = False

    @property
    def active_target(self) -> Vector3 | None:
        if self.completed:
            return None
        return self._waypoints[self.target_index]

    @property
    def waypoints(self) -> tuple[Vector3, ...]:
        return self._waypoints

    def update(self, position: Sequence[float]) -> WaypointStatus:
        if self.completed:
            return WaypointStatus(
                target_index=self.target_index,
                active_target=None,
                reached_count=self.reached_count,
                completed=True,
                advanced=False,
                distance=0.0,
                dwell_count=self.dwell_count,
            )

        target = self._waypoints[self.target_index]
        distance = float(dist((float(position[0]), float(position[1]), float(position[2])), target))
        advanced = False

        if distance <= self.radius:
            self.dwell_count += 1
        else:
            self.dwell_count = 0

        if self.dwell_count >= self.dwell_steps:
            self.reached_count += 1
            self.target_index += 1
            self.dwell_count = 0
            advanced = True
            if self.target_index >= len(self._waypoints):
                self.completed = True

        return WaypointStatus(
            target_index=self.target_index,
            active_target=self.active_target,
            reached_count=self.reached_count,
            completed=self.completed,
            advanced=advanced,
            distance=distance,
            dwell_count=self.dwell_count,
        )
