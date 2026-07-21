"""JSON API for the persistent leaderboard.

Routes (mounted at ``/api`` alongside the game API):
- ``GET  /api/leaderboard?difficulty=`` — top times for one difficulty
- ``POST /api/leaderboard``             — record a score for a won game

All verification (game exists, is won, not already scored) and the authoritative
time computation live in :mod:`app.controllers.leaderboard`; this layer only
translates HTTP <-> controller and maps controller errors to status codes.
"""
from __future__ import annotations

from flask import Blueprint, Response, jsonify, request
from pydantic import ValidationError

from ..controllers.leaderboard import ScoreError, record_score, top_scores
from ..controllers.minesweeper import DEFAULT_DIFFICULTY, DIFFICULTIES
from ..schemas.score import SubmitScoreRequest, serialize_leaderboard
from .responses import json_error as _error

leaderboard_bp = Blueprint('leaderboard', __name__)


@leaderboard_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard() -> tuple[Response, int]:
    """Return the top times for the requested difficulty (default Beginner)."""
    difficulty = request.args.get('difficulty', DEFAULT_DIFFICULTY)
    if difficulty not in DIFFICULTIES:
        return _error(f'Unknown difficulty: {difficulty!r}', 400)
    view = serialize_leaderboard(difficulty, top_scores(difficulty))
    return jsonify(view.model_dump()), 200


@leaderboard_bp.route('/leaderboard', methods=['POST'])
def submit_score() -> tuple[Response, int]:
    """Record a score for a won game and return the updated leaderboard.

    409 if the game was already scored, 422 if it is not won, 404 if it does not
    exist, 400 for a malformed body or invalid name.
    """
    data = request.get_json(silent=True)
    if data is None:
        return _error('Request body must be valid JSON', 400)
    try:
        req = SubmitScoreRequest.model_validate(data)
    except ValidationError as exc:
        return _error(f'Invalid score submission: {exc.errors()}', 400)

    try:
        difficulty, scores = record_score(req.gameId, req.name)
    except ScoreError as exc:
        return _error(str(exc), exc.status)

    view = serialize_leaderboard(difficulty, scores)
    return jsonify(view.model_dump()), 201
