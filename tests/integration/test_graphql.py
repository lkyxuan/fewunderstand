"""
Integration tests for GraphQL API.
Tests US3: GraphQL API auto-exposure
"""
import os

import pytest
import requests


# Load config from environment
HASURA_PORT = os.getenv("HASURA_PORT", "8080")
HASURA_URL = f"http://localhost:{HASURA_PORT}"
ADMIN_SECRET = os.getenv("HASURA_GRAPHQL_ADMIN_SECRET", "lagos_admin_secret")


def graphql_query(query: str, variables: dict = None):
    """Execute a GraphQL query."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = requests.post(
        f"{HASURA_URL}/v1/graphql",
        json=payload,
        headers={"x-hasura-admin-secret": ADMIN_SECRET},
        timeout=10
    )
    return response.json()


class TestGraphQLSchema:
    """Test that GraphQL schema is correctly exposed."""

    def test_prices_query(self):
        """Should be able to query prices table."""
        result = graphql_query("""
            query {
                prices(limit: 10) {
                    time
                    symbol
                    price
                }
            }
        """)
        assert "errors" not in result, f"Errors: {result.get('errors')}"
        assert "data" in result
        assert "prices" in result["data"]

    def test_signals_query(self):
        """Should be able to query signals table."""
        result = graphql_query("""
            query {
                signals(limit: 10, order_by: {time: desc}) {
                    id
                    time
                    symbol
                    signal_type
                    change_pct
                }
            }
        """)
        assert "errors" not in result, f"Errors: {result.get('errors')}"
        assert "data" in result
        assert "signals" in result["data"]

    def test_news_query(self):
        """Should be able to query news table."""
        result = graphql_query("""
            query {
                news(limit: 10, order_by: {time: desc}) {
                    id
                    time
                    source
                    title
                    url
                }
            }
        """)
        assert "errors" not in result, f"Errors: {result.get('errors')}"
        assert "data" in result
        assert "news" in result["data"]

    def test_word_freq_with_relationship(self):
        """Should be able to query word_freq with news relationship."""
        result = graphql_query("""
            query {
                word_freq(limit: 10) {
                    time
                    window
                    word
                    count
                    latest_news {
                        title
                    }
                }
            }
        """)
        assert "errors" not in result, f"Errors: {result.get('errors')}"
        assert "data" in result
        assert "word_freq" in result["data"]


class TestGraphQLAggregations:
    """Test GraphQL aggregation queries."""

    def test_prices_aggregate(self):
        """Should be able to get price aggregations."""
        result = graphql_query("""
            query {
                prices_aggregate {
                    aggregate {
                        count
                    }
                }
            }
        """)
        assert "errors" not in result, f"Errors: {result.get('errors')}"
        assert "data" in result
        assert result["data"]["prices_aggregate"]["aggregate"]["count"] >= 0


class TestGraphQLFiltering:
    """Test GraphQL filtering capabilities."""

    def test_filter_by_symbol(self):
        """Should be able to filter by symbol."""
        result = graphql_query("""
            query {
                prices(where: {symbol: {_eq: "BTCUSDT"}}, limit: 5) {
                    symbol
                    price
                }
            }
        """)
        assert "errors" not in result, f"Errors: {result.get('errors')}"
        # All returned prices should be for BTCUSDT
        for price in result["data"]["prices"]:
            assert price["symbol"] == "BTCUSDT"

    def test_filter_by_time_range(self):
        """Should be able to filter by time range."""
        result = graphql_query("""
            query {
                signals(
                    where: {
                        time: {_gte: "2024-01-01T00:00:00Z"}
                    }
                    limit: 10
                ) {
                    time
                    symbol
                }
            }
        """)
        assert "errors" not in result, f"Errors: {result.get('errors')}"
