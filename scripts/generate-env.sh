#!/bin/bash
# generate-env.sh - Generate .env from config/settings.yaml
# Uses Python for YAML parsing (available on most systems)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_DIR/config/settings.yaml"
ENV_FILE="$PROJECT_DIR/.env"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: $CONFIG_FILE not found"
    exit 1
fi

# Generate .env from YAML using Python
python3 << 'PYTHON_SCRIPT' "$CONFIG_FILE" "$ENV_FILE"
import sys
import re

config_file = sys.argv[1]
env_file = sys.argv[2]

# Simple YAML parser for flat structure
config = {}
current_section = None

def parse_yaml_value(raw_value):
    """Parse YAML value, handling quotes and inline comments."""
    raw_value = raw_value.strip()
    # Handle quoted strings (preserve content including : and #)
    if raw_value.startswith('"') and '"' in raw_value[1:]:
        end = raw_value.index('"', 1)
        return raw_value[1:end]
    if raw_value.startswith("'") and "'" in raw_value[1:]:
        end = raw_value.index("'", 1)
        return raw_value[1:end]
    # Unquoted: strip inline comment (only if # has space before it)
    if '  #' in raw_value:
        raw_value = raw_value.split('  #')[0].strip()
    elif raw_value.endswith(' #'):
        raw_value = raw_value[:-2].strip()
    return raw_value

with open(config_file, 'r') as f:
    for line in f:
        line = line.rstrip()
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            continue
        # Section header (no leading spaces)
        if not line.startswith(' ') and line.endswith(':'):
            current_section = line[:-1].strip()
            continue
        # Key-value pair (indented)
        match = re.match(r'^\s+(\w+):\s*(.+)$', line)
        if match and current_section:
            key = match.group(1)
            value = parse_yaml_value(match.group(2))
            config[f"{current_section}.{key}"] = value

# Map to environment variables
env_mapping = {
    'POSTGRES_USER': config.get('database.user', 'lagos'),
    'POSTGRES_PASSWORD': config.get('database.password', 'lagos_dev_password'),
    'POSTGRES_DB': config.get('database.name', 'lagos'),
    'POSTGRES_PORT': config.get('database.port', '5432'),
    'HASURA_PORT': config.get('hasura.port', '8080'),
    'HASURA_GRAPHQL_ADMIN_SECRET': config.get('hasura.admin_secret', 'lagos_admin_secret'),
    'HASURA_GRAPHQL_ENABLE_CONSOLE': config.get('hasura.enable_console', 'true'),
    'HASURA_GRAPHQL_DEV_MODE': config.get('hasura.dev_mode', 'true'),
    'RETENTION_DAYS': config.get('retention.days', '30'),
}

# Build database URL
db_user = env_mapping['POSTGRES_USER']
db_pass = env_mapping['POSTGRES_PASSWORD']
db_name = env_mapping['POSTGRES_DB']
env_mapping['HASURA_GRAPHQL_DATABASE_URL'] = f'postgres://{db_user}:{db_pass}@postgres:5432/{db_name}'

# Write .env file
with open(env_file, 'w') as f:
    f.write('# Auto-generated from config/settings.yaml\n')
    f.write('# Do not edit directly - edit config/settings.yaml instead\n\n')
    for key, value in env_mapping.items():
        f.write(f'{key}={value}\n')

print(f"Generated {env_file} from {config_file}")
PYTHON_SCRIPT
