#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m unittest discover -s tests -v
python3 -m vehicle_network.simulator --duration 2 --interval 0.1 --log logs/network_demo.jsonl
python3 -m vehicle_network.validator --log logs/network_demo.jsonl --min-valid 15 --max-gap-seconds 0.25
