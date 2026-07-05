from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from time import time
from typing import Any


class ControllerMode(str, Enum):
    OFF = "OFF"
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    FAULT = "FAULT"


@dataclass(frozen=True)
class SensorFrame:
    engine_rpm: int
    hydraulic_pressure_psi: float
    steering_angle_deg: float
    implement_height_pct: float
    e_stop: bool = False
    timestamp: float = field(default_factory=time)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SensorFrame":
        return cls(
            engine_rpm=int(data.get("engine_rpm", 0)),
            hydraulic_pressure_psi=float(data.get("hydraulic_pressure_psi", 0.0)),
            steering_angle_deg=float(data.get("steering_angle_deg", 0.0)),
            implement_height_pct=float(data.get("implement_height_pct", 0.0)),
            e_stop=bool(data.get("e_stop", False)),
            timestamp=float(data.get("timestamp", time())),
        )


@dataclass(frozen=True)
class CommandResult:
    accepted: bool
    mode: ControllerMode
    reason: str
    outputs: dict[str, Any]
    faults: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "mode": self.mode.value,
            "reason": self.reason,
            "outputs": self.outputs,
            "faults": list(self.faults),
        }


class VirtualImplementController:
    """Small state-machine model used as the system under test."""

    MIN_AUTO_RPM = 900
    MAX_HYDRAULIC_PRESSURE_PSI = 3200.0
    MAX_STEERING_ANGLE_DEG = 35.0

    def __init__(self) -> None:
        self.mode = ControllerMode.OFF
        self._faults: list[str] = []
        self._last_height_pct = 50.0

    @property
    def faults(self) -> tuple[str, ...]:
        return tuple(self._faults)

    def apply_command(self, command: str, sensors: SensorFrame | None = None) -> CommandResult:
        command = command.strip().lower()

        if command == "boot":
            self.mode = ControllerMode.IDLE
            return self._result(True, "boot_complete", {"auto_enabled": False})

        if command == "shutdown":
            self.mode = ControllerMode.OFF
            self._last_height_pct = 50.0
            return self._result(True, "shutdown_complete", {"auto_enabled": False})

        if command == "clear_faults":
            self._faults.clear()
            self.mode = ControllerMode.IDLE
            return self._result(True, "faults_cleared", {"auto_enabled": False})

        if self.mode == ControllerMode.OFF:
            return self._result(False, "controller_not_booted", {"auto_enabled": False})

        if sensors is None:
            return self._enter_fault("missing_sensor_frame")

        validation_fault = self._validate_sensors(sensors)
        if validation_fault:
            return self._enter_fault(validation_fault)

        if self.mode == ControllerMode.FAULT:
            return self._result(False, "fault_latched", {"auto_enabled": False})

        if command == "start_auto":
            self.mode = ControllerMode.ACTIVE
            return self._result(True, "auto_started", {"auto_enabled": True, "valve_pwm": 45})

        if command == "stop_auto":
            self.mode = ControllerMode.IDLE
            return self._result(True, "auto_stopped", {"auto_enabled": False, "valve_pwm": 0})

        if command in {"raise", "lower", "hold"}:
            return self._handle_height_command(command, sensors)

        return self._result(False, f"unsupported_command:{command}", {"auto_enabled": self.mode == ControllerMode.ACTIVE})

    def _validate_sensors(self, sensors: SensorFrame) -> str | None:
        if sensors.e_stop:
            return "emergency_stop_active"
        if sensors.engine_rpm < 0:
            return "negative_engine_rpm"
        if sensors.hydraulic_pressure_psi > self.MAX_HYDRAULIC_PRESSURE_PSI:
            return "hydraulic_pressure_high"
        if abs(sensors.steering_angle_deg) > self.MAX_STEERING_ANGLE_DEG:
            return "steering_angle_out_of_range"
        if not 0.0 <= sensors.implement_height_pct <= 100.0:
            return "implement_height_out_of_range"
        if self.mode == ControllerMode.IDLE and sensors.engine_rpm < self.MIN_AUTO_RPM:
            return "engine_rpm_too_low_for_auto"
        return None

    def _handle_height_command(self, command: str, sensors: SensorFrame) -> CommandResult:
        if self.mode != ControllerMode.ACTIVE:
            return self._result(False, "auto_not_active", {"auto_enabled": False, "valve_pwm": 0})

        if command == "raise":
            self._last_height_pct = min(100.0, sensors.implement_height_pct + 5.0)
            valve_pwm = 60
        elif command == "lower":
            self._last_height_pct = max(0.0, sensors.implement_height_pct - 5.0)
            valve_pwm = -60
        else:
            self._last_height_pct = sensors.implement_height_pct
            valve_pwm = 0

        return self._result(
            True,
            f"{command}_accepted",
            {
                "auto_enabled": True,
                "target_height_pct": round(self._last_height_pct, 2),
                "valve_pwm": valve_pwm,
            },
        )

    def _enter_fault(self, reason: str) -> CommandResult:
        if reason not in self._faults:
            self._faults.append(reason)
        self.mode = ControllerMode.FAULT
        return self._result(False, reason, {"auto_enabled": False, "valve_pwm": 0})

    def _result(self, accepted: bool, reason: str, outputs: dict[str, Any]) -> CommandResult:
        return CommandResult(
            accepted=accepted,
            mode=self.mode,
            reason=reason,
            outputs=outputs,
            faults=self.faults,
        )
