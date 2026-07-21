"""Shared JSON-response helpers for the API blueprints.

The API returns errors as JSON *directly* (not via ``abort()``) because the
shared HTML error handlers only emit JSON when the client sends
``Accept: application/json``, and API clients must always get JSON. Centralizing
the status-code → label mapping here keeps every API error consistent — in
particular the leaderboard's 409/422, which the base game's original ad-hoc
helper labelled "Bad Request".
"""
from __future__ import annotations

from flask import Response, jsonify

# Canonical reason phrases for the status codes the API emits. Anything not
# listed falls back to a generic label rather than mislabelling (e.g. a 409 as
# "Bad Request").
_STATUS_LABELS: dict[int, str] = {
    400: 'Bad Request',
    404: 'Not Found',
    409: 'Conflict',
    422: 'Unprocessable Entity',
}


def json_error(message: str, status: int) -> tuple[Response, int]:
    """Build a JSON error response independent of the Accept header."""
    label = _STATUS_LABELS.get(status, 'Error')
    return jsonify(error=label, message=message), status
