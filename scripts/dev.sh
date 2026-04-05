#!/bin/bash
set -e

cd "$(dirname "$0")/.."

trap 'kill 0' EXIT

echo "Starting backend..."
(cd backend && uv run fastapi dev --port 8000) &

echo "Starting frontend..."
(cd frontend && bun run dev) &

wait
