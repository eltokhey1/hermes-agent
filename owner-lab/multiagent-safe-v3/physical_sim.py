"""Simulation-only reference safety boundary, NOT a robotics controller.

No network, ROS 2, Isaac, device drivers, hardware access, or model inference.
All movement takes place in a virtual 2D grid; a hard-coded policy rejects
unknown capabilities, collisions, oversize steps, and invalid coordinates.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import math


class SafetyStop(ValueError):
    pass


@dataclass(frozen=True)
class VirtualCommand:
    capability: str
    target_x: float
    target_y: float


@dataclass
class SimulationSafetyGate:
    position: tuple[float, float] = (0.0, 0.0)
    size: float = 10.0
    max_step: float = 1.5
    obstacles: tuple[tuple[float, float], ...] = ((3.0, 3.0),)
    stop_latched: bool = False
    records: list[dict] = field(default_factory=list)

    def _valid_xy(self, x: float, y: float) -> bool:
        return (type(x) in (float, int) and type(y) in (float, int)
                and math.isfinite(x) and math.isfinite(y)
                and 0 <= x <= self.size and 0 <= y <= self.size)

    def _segment_hits_obstacle(self, a: tuple[float, float], b: tuple[float, float]) -> bool:
        # Virtual obstacle radius; check the complete segment, not only endpoints.
        dx, dy = b[0] - a[0], b[1] - a[1]
        divisor = dx * dx + dy * dy
        for ox, oy in self.obstacles:
            projection = 0 if divisor == 0 else max(0, min(1, ((ox - a[0]) * dx + (oy - a[1]) * dy) / divisor))
            px, py = a[0] + projection * dx, a[1] + projection * dy
            if math.dist((px, py), (ox, oy)) <= 0.5:
                return True
        return False

    def apply(self, command: VirtualCommand) -> dict:
        if not isinstance(command, VirtualCommand) or command.capability not in {'virtual.move', 'virtual.stop', 'virtual.inspect'}:
            raise SafetyStop('Capability not permitted')
        if command.capability == 'virtual.stop':
            self.stop_latched = True
            outcome = {'status': 'STOPPED', 'position': self.position, 'simulated': True}
            self.records.append(outcome)
            return outcome
        if self.stop_latched:
            raise SafetyStop('Emergency stop is latched')
        if not self._valid_xy(*self.position) or not self._valid_xy(command.target_x, command.target_y):
            raise SafetyStop('Invalid virtual coordinates')
        if command.capability == 'virtual.inspect':
            outcome = {'status': 'OBSERVED', 'position': self.position, 'simulated': True}
        else:
            target = (command.target_x, command.target_y)
            if math.dist(self.position, target) > self.max_step:
                raise SafetyStop('Virtual step exceeds allowed bound')
            if self._segment_hits_obstacle(self.position, target):
                raise SafetyStop('Collision predicted in virtual world')
            self.position = target
            outcome = {'status': 'MOVED', 'position': self.position, 'simulated': True}
        self.records.append(outcome)
        return outcome

    def run_episode(self, commands: list[VirtualCommand], *, max_actions: int = 10) -> dict:
        if not isinstance(commands, list) or type(max_actions) is not int or not 0 <= max_actions <= 50 or len(commands) > max_actions:
            raise SafetyStop('Episode exceeds action budget')
        outcomes = []
        for command in commands:
            outcomes.append(self.apply(command))
        return {'status': 'SIMULATED_ONLY', 'steps': len(outcomes), 'position': self.position,
                'hardware_execution': False}
