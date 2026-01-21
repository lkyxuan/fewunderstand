#!/bin/bash
# migrate.sh - Run database migrations
# Usage: ./scripts/migrate.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MIGRATIONS_DIR="$PROJECT_DIR/db/migrations"

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

# Check if PostgreSQL is running
if ! docker compose exec -T postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" > /dev/null 2>&1; then
    echo "Error: PostgreSQL is not running. Start services first with ./scripts/start.sh"
    exit 1
fi

echo "Running database migrations..."
echo ""

# Find and execute migration files in order
MIGRATION_COUNT=0
for file in "$MIGRATIONS_DIR"/*.sql; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "Applying: $filename"
        docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "/migrations/$filename"
        MIGRATION_COUNT=$((MIGRATION_COUNT + 1))
    fi
done

if [ $MIGRATION_COUNT -eq 0 ]; then
    echo "No migration files found in db/migrations/"
else
    echo ""
    echo "Applied $MIGRATION_COUNT migration(s) successfully."
fi
