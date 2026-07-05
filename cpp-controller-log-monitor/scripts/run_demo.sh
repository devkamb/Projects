#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

make all
./build/controller_log_monitor --input sample_data/controller_run.log --summary || true

set +e
./build/controller_log_monitor --input sample_data/controller_run.log --summary --fail-on ERROR
STATUS=$?
set -e

echo "Exit code with --fail-on ERROR: $STATUS"
if [[ "$STATUS" -ne 2 ]]; then
  echo "Expected exit code 2 when ERROR entries are present"
  exit 1
fi
