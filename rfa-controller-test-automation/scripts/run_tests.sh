#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m unittest discover -s tests -v
python3 -m controller_framework.test_runner --iterations 3 --log-dir logs
python3 -m controller_framework.log_analyzer --run-dir logs/latest
