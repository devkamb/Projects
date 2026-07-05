from __future__ import annotations

import json
from dataclasses import dataclass, field
from time import time
from typing import Any


class FrameError(ValueError):
    pass


@dataclass(frozen=True)
class CANFrame:
    arbitration_id: int
    payload: bytes
    timestamp: float = field(default_factory=time)

    def __post_init__(self) -> None:
        if not 0 <= self.arbitration_id <= 0x7FF:
            raise FrameError("classic CAN arbitration ID must be 11 bits")
        if len(self.payload) > 8:
            raise FrameError("classic CAN payload cannot exceed 8 bytes")

    @property
    def dlc(self) -> int:
        return len(self.payload)

    def checksum(self) -> int:
        total = self.arbitration_id & 0xFF
        total += (self.arbitration_id >> 8) & 0xFF
        total += self.dlc
        total += sum(self.payload)
        return total % 256

    def to_dict(self) -> dict[str, Any]:
        return {
            "arbitration_id": self.arbitration_id,
            "dlc": self.dlc,
            "payload_hex": self.payload.hex(),
            "timestamp": self.timestamp,
            "checksum": self.checksum(),
        }

    def encode(self) -> bytes:
        return json.dumps(self.to_dict(), sort_keys=True).encode("utf-8")

    @classmethod
    def decode(cls, data: bytes) -> "CANFrame":
        try:
            raw = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise FrameError("frame is not valid JSON") from exc

        required = {"arbitration_id", "dlc", "payload_hex", "timestamp", "checksum"}
        missing = required - set(raw)
        if missing:
            raise FrameError(f"frame missing required fields: {sorted(missing)}")

        try:
            payload = bytes.fromhex(raw["payload_hex"])
            frame = cls(
                arbitration_id=int(raw["arbitration_id"]),
                payload=payload,
                timestamp=float(raw["timestamp"]),
            )
            expected_checksum = int(raw["checksum"])
        except (TypeError, ValueError) as exc:
            raise FrameError("frame contains invalid field types") from exc

        if int(raw["dlc"]) != frame.dlc:
            raise FrameError("frame dlc does not match payload length")

        if expected_checksum != frame.checksum():
            raise FrameError("frame checksum mismatch")

        return frame
