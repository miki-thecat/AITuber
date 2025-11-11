#!/bin/bash
set -e

echo "Starting AITuber development environment..."

# Start overlay in background
echo "Starting Overlay server..."
uvicorn apps.overlay.server:app --host 0.0.0.0 --port 5173 &
OVERLAY_PID=$!

# Wait for overlay to be ready
sleep 2

# Start brain
echo "Starting Brain orchestrator..."
python -m apps.brain.main

# Cleanup on exit
trap "kill $OVERLAY_PID 2>/dev/null || true" EXIT
