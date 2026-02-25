"""
Tests for query parameter utility functions.

Validates that get_query_param and get_query_params correctly extract
parameters and raise errors for missing/duplicate params.
"""

import pytest

from mealbot.utils import get_query_param, get_query_params


def test_get_query_param_success(app):
    """Test extracting a single query parameter."""
    with app.test_request_context("/?admin=test@example.com"):
        result = get_query_param("admin")
        assert result == "test@example.com"


def test_get_query_param_missing(app):
    """Test that missing param raises ValueError."""
    with app.test_request_context("/"):
        with pytest.raises(ValueError, match="Request query parameters must contain admin"):
            get_query_param("admin")


def test_get_query_param_multiple_values(app):
    """Test that multiple values for same param raises ValueError."""
    with app.test_request_context("/?admin=a&admin=b"):
        with pytest.raises(ValueError, match="Request query parameters must contain admin"):
            get_query_param("admin")


def test_get_query_params_success(app):
    """Test extracting multiple query parameters."""
    with app.test_request_context("/?org=test&admin=admin@example.com"):
        result = get_query_params(["org", "admin"])
        assert result == ["test", "admin@example.com"]


def test_get_query_params_missing_one(app):
    """Test that missing one of multiple params raises ValueError."""
    with app.test_request_context("/?org=test"):
        with pytest.raises(ValueError, match="Request query parameters does not contain admin"):
            get_query_params(["org", "admin"])


def test_get_query_params_empty_keys(app):
    """Test with empty keys list returns empty list."""
    with app.test_request_context("/"):
        result = get_query_params([])
        assert result == []
