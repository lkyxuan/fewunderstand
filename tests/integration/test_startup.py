"""
Integration tests for service startup.
Tests US1: One-click environment startup
"""
import os
import subprocess
import time

import pytest
import requests


# Load config from environment
HASURA_PORT = os.getenv("HASURA_PORT", "8080")
HASURA_URL = f"http://localhost:{HASURA_PORT}"


class TestServiceStartup:
    """Test that all services start correctly."""

    def test_hasura_healthz(self):
        """Hasura /healthz endpoint should return OK."""
        response = requests.get(f"{HASURA_URL}/healthz", timeout=5)
        assert response.status_code == 200
        assert "OK" in response.text

    def test_hasura_graphql_endpoint(self):
        """Hasura GraphQL endpoint should respond."""
        query = {"query": "{ __typename }"}
        response = requests.post(
            f"{HASURA_URL}/v1/graphql",
            json=query,
            timeout=5
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["__typename"] == "query_root"

    def test_postgres_connection_via_hasura(self):
        """PostgreSQL should be accessible via Hasura."""
        # Query to check if tables exist
        query = {
            "query": """
                query {
                    prices(limit: 1) { time }
                    signals(limit: 1) { id }
                    news(limit: 1) { id }
                }
            """
        }
        response = requests.post(
            f"{HASURA_URL}/v1/graphql",
            json=query,
            timeout=5
        )
        assert response.status_code == 200
        data = response.json()
        # Should not have errors (tables should exist)
        assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"


class TestHealthCheck:
    """Test the health-check.sh script."""

    def test_health_check_script_exists(self):
        """Health check script should exist."""
        script_path = "scripts/health-check.sh"
        assert os.path.exists(script_path), f"{script_path} not found"

    def test_health_check_script_executable(self):
        """Health check script should be executable."""
        script_path = "scripts/health-check.sh"
        assert os.access(script_path, os.X_OK), f"{script_path} is not executable"
