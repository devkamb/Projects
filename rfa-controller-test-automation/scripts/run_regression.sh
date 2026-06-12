#!/usr/bin/env bash
set -euo pipefail

ITERATIONS="${1:-10}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m controller_framework.test_runner --iterations "$ITERATIONS" --log-dir logs
python3 -m controller_framework.log_analyzer --run-dir logs/latest
