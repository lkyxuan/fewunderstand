# Configuration Directory

This directory contains all configuration files for the Lagos project. Following the principle of **"configuration over code"**, all configurable values are defined here rather than hardcoded in scripts or SQL.

## Files

| File | Purpose |
|------|---------|
| `settings.yaml` | **Runtime configuration** - Edit this to customize your environment |
| `database.yaml` | Database schema, table definitions, TimescaleDB settings |
| `services.yaml` | Docker service configurations, ports, resources |
| `scripts.yaml` | Shell script behaviors, timeouts, health checks |

## Usage

### For Runtime Configuration

Edit `settings.yaml` to customize your local environment:

```yaml
database:
  user: lagos
  password: your_password
  port: 5432

hasura:
  port: 8080

retention:
  days: 30
```

The `start.sh` script automatically generates `.env` from this file.

### For Database Schema

The `database.yaml` file defines:
- Table structures
- Field types and constraints
- Indexes
- TimescaleDB hypertable settings
- Retention policies

When adding a new table:
1. Add the definition to `database.yaml`
2. Create/update the SQL migration in `db/init/` or `db/migrations/`

### For Docker Services

The `services.yaml` file defines:
- Container images and versions
- Port mappings
- Environment variables
- Health checks
- Resource limits

## Environment Variables

All sensitive values and deployment-specific settings go in `.env`:

```bash
# Copy template
cp .env.example .env

# Edit values
vim .env
```

## Adding New Configuration

1. **Database changes**: Add to `database.yaml`, create SQL migration
2. **New service**: Add to `services.yaml`, update `docker-compose.yml`
3. **Script behavior**: Add to `scripts.yaml`, update shell scripts
4. **Environment variable**: Add to `.env.example` with documentation

## Principles

1. **No hardcoded values in code** - All configurable values come from config files or env vars
2. **Defaults in config, secrets in env** - Default values in YAML, sensitive values in `.env`
3. **Single source of truth** - Each setting defined in one place only
4. **Documentation inline** - Comments explain each setting's purpose
