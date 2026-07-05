# System-Level Controller Test Automation Framework

This project is a Python automation framework for validating a simulated embedded implement controller. It models common validation work: define test cases, run them repeatedly, capture pass/fail logs, and analyze failure signatures.

## What It Demonstrates

- Python system-level automated testing
- Controller-style state-machine validation
- Data-driven test cases
- Linux and Bash automation
- Regression testing across repeated executions
- Log collection and failure analysis
- Test documentation and traceability

## Run It

```bash
bash scripts/run_tests.sh
```

Run a repeated regression:

```bash
bash scripts/run_regression.sh 10
```

Analyze the newest run:

```bash
python3 -m controller_framework.log_analyzer --run-dir logs/latest
```

## Project Structure

```text
controller_framework/
  virtual_controller.py   Controller state machine under test
  test_runner.py          Data-driven system test runner
  log_analyzer.py         Failure grouping and root-cause hints
test_cases/
  controller_test_cases.json
tests/
  test_virtual_controller.py
scripts/
  run_tests.sh
  run_regression.sh
```

## Engineering Focus

This project focuses on repeatable validation workflows: define test inputs, execute controller scenarios, collect structured run logs, and summarize failures in a way that supports debugging and regression analysis.
