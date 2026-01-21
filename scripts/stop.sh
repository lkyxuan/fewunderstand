#!/bin/bash
# stop.sh - Stop all services
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "Stopping Lagos services..."
docker compose down

echo "Services stopped."
echo ""
echo "Note: Data is preserved in Docker volumes."
echo "To remove all data: docker compose down -v"
