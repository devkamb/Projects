from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def load_events(run_dir: Path) -> list[dict[str, Any]]:
    events_path = run_dir / "events.jsonl"
    events: list[dict[str, Any]] = []
    with events_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                events.append(json.loads(line))
    return events


def root_cause_hint(event: dict[str, Any]) -> str:
    reason = event.get("actual", {}).get("reason", "")
    if "hydraulic" in reason:
        return "Check pressure limits, sensor scaling, and hydraulic fault handling."
    if "emergency_stop" in reason:
        return "Check safety input state and fault-latch recovery path."
    if "rpm" in reason:
        return "Check preconditions for automatic mode and engine-speed setup."
    if "steering" in reason:
        return "Check steering-angle input range and calibration assumptions."
    if "unsupported_command" in reason:
        return "Check test case command spelling or missing controller feature."
    return "Compare expected state/output with command sequence and sensor inputs."


def analyze(events: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [event for event in events if not event["passed"]]
    by_case = Counter(event["case"] for event in failed)
    signatures: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for event in failed:
        actual = event.get("actual", {})
        signature = f"{event['case']}|step={event['step']}|reason={actual.get('reason')}|mode={actual.get('mode')}"
        signatures[signature].append(event)

    return {
        "total_steps": len(events),
        "failed_steps": len(failed),
        "failures_by_case": dict(by_case),
        "failure_signatures": [
            {
                "signature": signature,
                "count": len(group),
                "first_iteration": group[0]["iteration"],
                "first_step": group[0]["step"],
                "root_cause_hint": root_cause_hint(group[0]),
                "example_mismatches": group[0].get("mismatches", []),
            }
            for signature, group in sorted(signatures.items(), key=lambda item: len(item[1]), reverse=True)
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze controller regression logs")
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()

    report = analyze(load_events(args.run_dir))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["failed_steps"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
