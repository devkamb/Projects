# Design Notes: C++ Linux Systems Programming Project

## Core Idea

Automated tests often produce logs. A useful engineering tool can parse those logs, count warnings and errors, identify repeated failure signatures, and return an exit code that scripts can use.

This project is a small C++17 Linux utility that does exactly that.

## Code Layout

1. `include/LogEntry.h`
   - Data structure used to represent one parsed log line.
2. `include/LogParser.h` and `src/LogParser.cpp`
   - Converts a line of text into structured data.
3. `include/FailureAnalyzer.h` and `src/FailureAnalyzer.cpp`
   - Summarizes and groups parsed entries.
4. `src/main.cpp`
   - Command-line argument parsing, file reading, output, and exit codes.
5. `Makefile`
   - Builds the app and test executable.
6. `tests/test_parser.cpp`
   - Basic C++ tests written with `assert`.

## Important Concepts

Modular design:

Parsing is separate from analysis, and analysis is separate from the command-line program. This keeps the code easier to test.

Exit codes:

The tool returns `0` when the requested threshold passes and `2` when `--fail-on` detects a warning or error. Automation scripts can use those exit codes.

Root-cause triage:

The analyzer groups repeated messages by level, subsystem, and message text. This helps identify whether a failure is recurring or isolated.

## Design Summary

This is a C++17 Linux command-line tool that parses controller-style logs and summarizes failures. It uses separate classes for parsing and analysis, builds with a Makefile, includes a small test binary, and supports exit codes for automation.

## Possible Extensions

1. Add CSV output.
2. Add a `--since` timestamp filter.
3. Add support for JSON log input.
4. Add a `make install` target that copies the binary into `/usr/local/bin`.
