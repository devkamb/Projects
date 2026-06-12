from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from controller_framework.virtual_controller import SensorFrame, VirtualImplementController


DEFAULT_CASE_FILE = Path(__file__).resolve().parents[1] / "test_cases" / "controller_test_cases.json"


def load_cases(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        cases = json.load(handle)
    if not isinstance(cases, list):
        raise ValueError("Test case file must contain a JSON list")
    return cases


def run_case(case: dict[str, Any], iteration: int) -> tuple[bool, list[dict[str, Any]]]:
    controller = VirtualImplementController()
    events: list[dict[str, Any]] = []
    passed = True

    for step_index, step in enumerate(case.get("steps", []), start=1):
        sensors = SensorFrame.from_dict(step.get("sensors", {})) if "sensors" in step else None
        result = controller.apply_command(step["command"], sensors)
        expected = step.get("expect", {})
        step_passed, mismatches = _matches_expectation(result.to_dict(), expected)

        if not step_passed:
            passed = False

        events.append(
            {
                "timestamp": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
                "iteration": iteration,
                "case": case["name"],
                "requirement_ids": case.get("requirement_ids", []),
                "step": step_index,
                "command": step["command"],
                "expected": expected,
                "actual": result.to_dict(),
                "passed": step_passed,
                "mismatches": mismatches,
            }
        )

    return passed, events


def _matches_expectation(actual: dict[str, Any], expected: dict[str, Any]) -> tuple[bool, list[str]]:
    mismatches: list[str] = []

    for key, expected_value in expected.items():
        if key == "outputs_contains":
            outputs = actual.get("outputs", {})
            for output_key, output_value in expected_value.items():
                if outputs.get(output_key) != output_value:
                    mismatches.append(f"outputs.{output_key}: expected {output_value!r}, got {outputs.get(output_key)!r}")
            continue

        if key == "faults_contains":
            faults = set(actual.get("faults", []))
            missing = [fault for fault in expected_value if fault not in faults]
            if missing:
                mismatches.append(f"faults missing {missing!r}")
            continue

        if actual.get(key) != expected_value:
            mismatches.append(f"{key}: expected {expected_value!r}, got {actual.get(key)!r}")

    return not mismatches, mismatches


def write_run_logs(run_dir: Path, events: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    with (run_dir / "events.jsonl").open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
    with (run_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)


def update_latest_link(log_dir: Path, run_dir: Path) -> None:
    latest = log_dir / "latest"
    if latest.exists() or latest.is_symlink():
        latest.unlink()
    latest.symlink_to(run_dir.name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run controller system validation cases")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASE_FILE)
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--log-dir", type=Path, default=Path("logs"))
    args = parser.parse_args()

    cases = load_cases(args.cases)
    run_name = "run_" + datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_dir = args.log_dir / run_name
    all_events: list[dict[str, Any]] = []
    passed_cases = 0
    failed_cases = 0

    for iteration in range(1, args.iterations + 1):
        for case in cases:
            case_passed, events = run_case(case, iteration)
            all_events.extend(events)
            if case_passed:
                passed_cases += 1
            else:
                failed_cases += 1

    failed_steps = sum(1 for event in all_events if not event["passed"])
    summary = {
        "run_name": run_name,
        "case_file": str(args.cases),
        "iterations": args.iterations,
        "total_case_executions": passed_cases + failed_cases,
        "passed_case_executions": passed_cases,
        "failed_case_executions": failed_cases,
        "total_steps": len(all_events),
        "failed_steps": failed_steps,
        "pass_rate_pct": round(100.0 * (len(all_events) - failed_steps) / max(1, len(all_events)), 2),
    }

    write_run_logs(run_dir, all_events, summary)
    update_latest_link(args.log_dir, run_dir)

    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"Logs written to {run_dir}")
    return 0 if failed_steps == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
