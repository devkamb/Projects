# C++ Linux Systems Programming Project

This project is a C++17 command-line tool that parses controller logs, summarizes warnings and errors, and detects repeated failure signatures. It is designed like a small Linux utility an engineer could use while debugging automated test failures.

## What It Demonstrates

- C++ modular design
- Linux command-line tooling
- Makefile-based builds
- Structured log parsing
- Failure analysis and root-cause support
- Exit codes useful for automation scripts

## Build And Test

```bash
make test
```

Run the demo:

```bash
bash scripts/run_demo.sh
```

Manual usage:

```bash
./build/controller_log_monitor --input sample_data/controller_run.log --summary
./build/controller_log_monitor --input sample_data/controller_run.log --summary --fail-on ERROR
```

## Project Structure

```text
include/
  LogEntry.h
  LogParser.h
  FailureAnalyzer.h
src/
  LogParser.cpp
  FailureAnalyzer.cpp
  main.cpp
tests/
  test_parser.cpp
Makefile
```

## How This Maps To RFA

The RFA posting lists Linux Ubuntu, Bash scripting, C++, debugging intermittent failures, and root-cause analysis. This project demonstrates those skills through a practical command-line utility.
