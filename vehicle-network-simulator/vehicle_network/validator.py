from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def validate(records: list[dict[str, Any]], min_valid: int, max_gap_seconds: float) -> dict[str, Any]:
    valid = [record for record in records if record.get("event") == "frame_received" and record.get("valid")]
    invalid = [record for record in records if record.get("event") == "frame_received" and not record.get("valid")]
    by_id = Counter(hex(record["arbitration_id"]) for record in valid)

    gaps: list[float] = []
    for before, after in zip(valid, valid[1:]):
        gaps.append(round(after["monotonic"] - before["monotonic"], 4))

    failures: list[str] = []
    if len(valid) < min_valid:
        failures.append(f"expected at least {min_valid} valid frames, got {len(valid)}")
    if invalid:
        failures.append(f"expected zero invalid frames, got {len(invalid)}")
    if gaps and max(gaps) > max_gap_seconds:
        failures.append(f"max message gap {max(gaps):.4f}s exceeded {max_gap_seconds:.4f}s")

    return {
        "valid_frames": len(valid),
        "invalid_frames": len(invalid),
        "frames_by_arbitration_id": dict(by_id),
        "max_gap_seconds": max(gaps) if gaps else 0.0,
        "failures": failures,
        "passed": not failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate vehicle network simulator logs")
    parser.add_argument("--log", type=Path, default=Path("logs/network_demo.jsonl"))
    parser.add_argument("--min-valid", type=int, default=15)
    parser.add_argument("--max-gap-seconds", type=float, default=0.25)
    args = parser.parse_args()

    report = validate(load_records(args.log), args.min_valid, args.max_gap_seconds)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
