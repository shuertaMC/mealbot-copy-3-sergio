"""Tests for response format helpers.

Verifies that the Python response format matches Go's Message struct:
    type Message struct { Message string }
    -> {"Message": "..."}
"""

from mealbot_api.schemas.responses import (
    MessageResponse,
    error_response,
    message_response,
)


class TestMessageResponse:
    """Verify MessageResponse model matches Go's Message struct format."""

    def test_message_response_format(self):
        """MessageResponse JSON must have capitalized 'Message' key."""
        resp = MessageResponse(Message="Hello")
        data = resp.model_dump()
        assert "Message" in data
        assert data["Message"] == "Hello"

    def test_message_response_json(self):
        """MessageResponse JSON serialization matches Go format."""
        resp = MessageResponse(Message="test message")
        json_str = resp.model_dump_json()
        assert '"Message"' in json_str
        assert '"test message"' in json_str

    def test_message_response_helper(self):
        """message_response() returns correct status and body."""
        resp = message_response("Success", status_code=201)
        assert resp.status_code == 201
        assert resp.body == b'{"Message":"Success"}'

    def test_error_response_helper(self):
        """error_response() returns correct error body."""
        resp = error_response("Something went wrong", status_code=500)
        assert resp.status_code == 500
        assert resp.body == b'{"Message":"Something went wrong"}'

    def test_error_response_from_exception(self):
        """error_response() handles Exception objects."""
        exc = ValueError("Invalid input")
        resp = error_response(exc, status_code=400)
        assert resp.status_code == 400
        assert b"Invalid input" in resp.body
