#!/bin/bash
# start.sh - Start all services
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Generate .env from config/settings.yaml
echo "Loading configuration from config/settings.yaml..."
"$SCRIPT_DIR/generate-env.sh"

# Load environment variables
if [ -f .env ]; then
    set -a
    source .env
    set +a
else
    echo "Error: Failed to generate .env file"
    exit 1
fi

# Use environment variables with defaults
POSTGRES_USER="${POSTGRES_USER:-lagos}"
POSTGRES_DB="${POSTGRES_DB:-lagos}"
HASURA_PORT="${HASURA_PORT:-8080}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

echo "Starting Lagos services..."

# Start services
docker compose up -d

echo ""
echo "Waiting for services to be healthy..."

# Wait for PostgreSQL
echo -n "PostgreSQL: "
timeout 60 bash -c "until docker compose exec -T postgres pg_isready -U $POSTGRES_USER -d $POSTGRES_DB 2>/dev/null; do sleep 2; done" && echo "ready" || echo "timeout"

# Wait for Hasura
echo -n "Hasura: "
timeout 60 bash -c "until curl -s http://localhost:$HASURA_PORT/healthz 2>/dev/null | grep -q OK; do sleep 2; done" && echo "ready" || echo "timeout"

# Inject RETENTION_DAYS into database and update retention policies
RETENTION_DAYS="${RETENTION_DAYS:-30}"
echo -n "Configuring retention policy ($RETENTION_DAYS days): "
docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -q << EOF 2>/dev/null && echo "done" || echo "skipped"
-- Update config table
INSERT INTO _config (key, value, description, updated_at)
VALUES ('retention_days', '$RETENTION_DAYS', 'Data retention period in days', NOW())
ON CONFLICT (key) DO UPDATE SET value = '$RETENTION_DAYS', updated_at = NOW();

-- Update retention policies for all hypertables
DO \$\$
DECLARE
    retention_interval INTERVAL := '$RETENTION_DAYS days'::INTERVAL;
    tbl TEXT;
    tables TEXT[] := ARRAY['prices', 'klines', 'indicators', 'signals', 'news', 'word_freq'];
BEGIN
    -- Remove old policies and add new ones with updated interval
    FOREACH tbl IN ARRAY tables LOOP
        PERFORM remove_retention_policy(tbl::regclass, if_exists => true);
        PERFORM add_retention_policy(tbl::regclass, retention_interval);
    END LOOP;
END \$\$;
EOF

echo ""
echo "Services started successfully!"
echo ""
echo "Access points:"
echo "  - Hasura Console: http://localhost:$HASURA_PORT"
echo "  - PostgreSQL:     localhost:$POSTGRES_PORT"
echo ""
echo "Run './scripts/health-check.sh' to verify all services."
