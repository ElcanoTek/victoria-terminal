#!/bin/bash
# macOS double-click launcher for Victoria
cd "$(dirname "$0")"
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
exec python3 victoria.py
