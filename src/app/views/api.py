"""JSON API for server-authoritative Minesweeper.

Routes (mounted at ``/api``):
- ``POST /api/games``               — create a new game (no mines placed yet)
- ``POST /api/games/<id>/reveal``   — reveal a cell (first reveal places mines)
- ``POST /api/games/<id>/flag``     — toggle a flag
- ``GET  /api/games/<id>``          — fetch current state (resume after reload)

Every response is built by the redacting serializer, so hidden state never
leaks. Errors are returned as JSON *directly* (``jsonify(...), 4xx``) rather
than via ``abort()``: the shared error handlers only emit JSON when the request
carries ``Accept: application/json``, and API clients must get JSON regardless.
"""
from __future__ import annotations

from flask import Blueprint, Response, jsonify, request
from pydantic import ValidationError

from ..controllers import minesweeper
from ..models import db
from ..models.game import Game
from ..schemas.game import MoveRequest, serialize_game

api_bp = Blueprint('api', __name__)


def _state_response(game: Game, status: int = 200) -> tuple[Response, int]:
    """Serialize a game through the redacting serializer and return it as JSON.

    ``exclude_none=True`` drops the ``adjacent``/``mine`` keys from hidden and
    flagged cells, so unrevealed cells carry no board information at all.
    """
    view = serialize_game(game)
    return jsonify(view.model_dump(exclude_none=True)), status


def _error(message: str, status: int) -> tuple[Response, int]:
    """Build a JSON error response independent of the Accept header."""
    label = 'Not Found' if status == 404 else 'Bad Request'
    return jsonify(error=label, message=message), status


def _load_game(game_id: int) -> Game | None:
    """Load a game by id, or return None if it does not exist."""
    return db.session.get(Game, game_id)


def _parse_move(game: Game) -> tuple[MoveRequest | None, tuple[Response, int] | None]:
    """Validate the request body as a MoveRequest and bounds-check coordinates.

    Returns ``(move, None)`` on success or ``(None, error_response)`` on failure
    (400 for malformed bodies or out-of-range coordinates).
    """
    data = request.get_json(silent=True)
    if data is None:
        return None, _error('Request body must be valid JSON', 400)
    try:
        move = MoveRequest.model_validate(data)
    except ValidationError as exc:
        return None, _error(f'Invalid move: {exc.errors()}', 400)
    if not (0 <= move.row < game.rows and 0 <= move.col < game.cols):
        return None, _error('Cell coordinates out of range', 400)
    return move, None


@api_bp.route('/games', methods=['POST'])
def create_game() -> tuple[Response, int]:
    """Create a new game. Mines are placed on the first reveal, not here."""
    game = minesweeper.new_game()
    db.session.add(game)
    db.session.commit()
    return _state_response(game, 201)


@api_bp.route('/games/<int:game_id>', methods=['GET'])
def get_game(game_id: int) -> tuple[Response, int]:
    """Return the current redacted state of a game (for reload/resume)."""
    game = _load_game(game_id)
    if game is None:
        return _error(f'No game with id {game_id}', 404)
    return _state_response(game)


@api_bp.route('/games/<int:game_id>/reveal', methods=['POST'])
def reveal_cell(game_id: int) -> tuple[Response, int]:
    """Reveal a cell. On loss the response includes the full mine layout."""
    game = _load_game(game_id)
    if game is None:
        return _error(f'No game with id {game_id}', 404)
    move, error = _parse_move(game)
    if error is not None:
        return error
    assert move is not None
    minesweeper.reveal(game, move.row, move.col)
    db.session.commit()
    return _state_response(game)


@api_bp.route('/games/<int:game_id>/flag', methods=['POST'])
def flag_cell(game_id: int) -> tuple[Response, int]:
    """Toggle a flag on a cell and return the updated board + flag count."""
    game = _load_game(game_id)
    if game is None:
        return _error(f'No game with id {game_id}', 404)
    move, error = _parse_move(game)
    if error is not None:
        return error
    assert move is not None
    minesweeper.toggle_flag(game, move.row, move.col)
    db.session.commit()
    return _state_response(game)
