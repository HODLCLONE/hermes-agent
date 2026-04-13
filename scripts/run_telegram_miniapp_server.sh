#!/usr/bin/env bash
set -euo pipefail
cd /opt/hermes-agent/source
source /opt/hermes-agent/runtime/venv/bin/activate
python scripts/run_telegram_miniapp_server.py
