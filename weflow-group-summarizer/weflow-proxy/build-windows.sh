#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "Cross-compiling weflow-proxy for Windows (amd64)..."
GOOS=windows GOARCH=amd64 go build -o weflow-proxy.exe .

echo "Done: $(ls -lh weflow-proxy.exe | awk '{print $5, $NF}')"
