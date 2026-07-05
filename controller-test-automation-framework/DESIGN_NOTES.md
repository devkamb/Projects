# Design Notes: Controller Test Automation Framework

## Core Idea

Embedded-controller validation usually checks whether a controller responds correctly to inputs, commands, and fault conditions. In this project, `VirtualImplementController` acts like a small controller for an agricultural implement. It has states and safety checks:

- `OFF`: controller has not booted.
- `IDLE`: controller is ready but automation is not active.
- `ACTIVE`: controller is actively controlling implement output.
- `FAULT`: controller rejected operation because a safety or sensor condition failed.

## Code Layout

1. `controller_framework/virtual_controller.py`
   - Controller states, sensor validation, command handling, and fault latching.
2. `test_cases/controller_test_cases.json`
   - System-level scenarios represented as steps with expected results.
3. `controller_framework/test_runner.py`
   - Loads test cases, executes steps, validates expectations, and writes logs.
4. `controller_framework/log_analyzer.py`
   - Groups failures into useful debugging summaries.
5. `tests/test_virtual_controller.py`
   - Unit tests that protect controller behavior.

## Important Concepts

State machine:

A controller often behaves differently depending on its current mode. For example, `start_auto` is valid in `IDLE`, but not valid after an emergency stop places the controller in `FAULT`.

Fault latch:

Some embedded systems stay in a faulted state until an operator or technician explicitly clears the fault. This prevents unsafe automatic recovery.

Data-driven tests:

The test runner reads JSON instead of hardcoding every test in Python. This makes it easier to add or review test cases.

Regression testing:

Running a test once proves very little. Running the same tests repeatedly helps expose intermittent failures, timing problems, or state leakage.

Structured logs:

The runner writes JSON lines so a script can group and analyze failures without fragile text parsing.

## Design Summary

The framework validates a simulated controller using data-driven system tests. The controller has states such as OFF, IDLE, ACTIVE, and FAULT. The test runner executes JSON-defined scenarios, checks expected states and outputs, writes structured logs, and includes a failure analyzer that groups recurring failures by signature.

## Possible Extensions

1. Add a new command called `calibrate`.
2. Add a sensor limit for battery voltage.
3. Add a new test case for low battery fault behavior.
4. Modify the analyzer to print the first failing step for each failure signature.
