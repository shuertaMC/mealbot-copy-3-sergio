"""Utility functions for request handling.

Equivalent to the Go application's utils.go query parameter extraction helpers.
"""

from fastapi import HTTPException, Request


def get_query_param(request: Request, key: str) -> str:
    """Extract a single required query parameter from the request.

    Equivalent to Go's getQueryParam: returns the value if exactly one is
    present, raises HTTPException(400) if missing or multiple values provided.

    Args:
        request: The incoming FastAPI request.
        key: The query parameter name.

    Returns:
        The query parameter value.

    Raises:
        HTTPException: If the parameter is missing or has multiple values.
    """
    values = request.query_params.getlist(key)
    if len(values) == 0 or len(values) > 1:
        raise HTTPException(
            status_code=400,
            detail=f"Request query parameters must contain {key}",
        )
    return values[0]


def get_query_params(request: Request, keys: list[str]) -> list[str]:
    """Extract multiple required query parameters from the request.

    Equivalent to Go's getQueryParams: returns values for each key,
    raises HTTPException(400) if any key is missing or has multiple values.

    Args:
        request: The incoming FastAPI request.
        keys: List of query parameter names.

    Returns:
        List of query parameter values in the same order as keys.

    Raises:
        HTTPException: If any parameter is missing or has multiple values.
    """
    values: list[str] = []
    for key in keys:
        param_values = request.query_params.getlist(key)
        if len(param_values) == 0 or len(param_values) > 1:
            raise HTTPException(
                status_code=400,
                detail=f"Request query parameters does not contain {key}",
            )
        values.append(param_values[0])
    return values
