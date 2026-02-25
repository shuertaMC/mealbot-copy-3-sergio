"""
Tests for logging helper functions.

Validates that log helpers produce correct JSON response format
and status codes matching the Go implementation.
"""

from mealbot.log import (
    err_to_response,
    log_and_write,
    log_and_write_err,
    log_and_write_status_bad_request,
    log_and_write_status_internal_server_error,
    str_to_response,
)


def test_str_to_response():
    """Test that str_to_response produces {"Message": "..."} format."""
    result = str_to_response("hello")
    assert result == {"Message": "hello"}


def test_err_to_response_with_string():
    """Test err_to_response with a string."""
    result = err_to_response("some error")
    assert result == {"Message": "some error"}


def test_err_to_response_with_exception():
    """Test err_to_response with an exception."""
    result = err_to_response(ValueError("bad value"))
    assert result == {"Message": "bad value"}


def test_log_and_write_err(app):
    """Test log_and_write_err returns correct status and body."""
    with app.test_request_context():
        response = log_and_write_err("error msg", 400, "TestFunc")
        assert response.status_code == 400
        data = response.get_json()
        assert data["Message"] == "error msg"


def test_log_and_write_with_string(app):
    """Test log_and_write with a string message."""
    with app.test_request_context():
        response = log_and_write("success", 200, "TestFunc")
        assert response.status_code == 200
        data = response.get_json()
        assert data["Message"] == "success"


def test_log_and_write_with_dict(app):
    """Test log_and_write with a dict."""
    with app.test_request_context():
        response = log_and_write({"orgs": ["a", "b"]}, 200, "TestFunc")
        assert response.status_code == 200
        data = response.get_json()
        assert data == {"orgs": ["a", "b"]}


def test_log_and_write_status_bad_request(app):
    """Test log_and_write_status_bad_request returns 400."""
    with app.test_request_context():
        response = log_and_write_status_bad_request("bad request", "TestFunc")
        assert response.status_code == 400
        data = response.get_json()
        assert data["Message"] == "bad request"


def test_log_and_write_status_internal_server_error(app):
    """Test log_and_write_status_internal_server_error returns 500."""
    with app.test_request_context():
        response = log_and_write_status_internal_server_error(
            "server error", "TestFunc"
        )
        assert response.status_code == 500
        data = response.get_json()
        assert data["Message"] == "server error"
