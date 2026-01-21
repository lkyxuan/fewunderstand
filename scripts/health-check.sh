#!/bin/bash
# health-check.sh - Check health of all services
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Load environment variables
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Use environment variables with defaults
POSTGRES_USER="${POSTGRES_USER:-lagos}"
POSTGRES_DB="${POSTGRES_DB:-lagos}"
HASURA_PORT="${HASURA_PORT:-8080}"

echo "Checking Lagos services health..."
echo ""

ALL_HEALTHY=true

# Check PostgreSQL
if docker compose exec -T postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" > /dev/null 2>&1; then
    echo "✓ PostgreSQL: healthy"
else
    echo "✗ PostgreSQL: unhealthy"
    ALL_HEALTHY=false
fi

# Check Hasura
if curl -s "http://localhost:$HASURA_PORT/healthz" 2>/dev/null | grep -q OK; then
    echo "✓ Hasura: healthy"
else
    echo "✗ Hasura: unhealthy"
    ALL_HEALTHY=false
fi

echo ""

if [ "$ALL_HEALTHY" = true ]; then
    echo "All services are running!"
    exit 0
else
    echo "Some services are unhealthy. Check logs with: docker compose logs"
    exit 1
fi
