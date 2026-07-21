"""Leaderboard controller: authoritative score recording and listing.

This is the trust boundary for the leaderboard. Two rules matter and both are
enforced here, server-side, so the browser cannot game the board:

1. A score can be recorded only for a game the *server* marked ``won``, and only
   once (the unique ``scores.game_id`` FK is the concrete guard; we also check
   status explicitly for a clean error).
2. The completion time is computed from the game's stored ``first_move_at`` /
   ``ended_at`` timestamps — never from anything the client sends. The submit
   schema has no duration field precisely so this can't be bypassed.

Errors are raised as :class:`ScoreError` subclasses carrying the HTTP status the
view should return, keeping status-code policy in one place.
"""
from __future__ import annotations

from sqlalchemy import select

from ..controllers.minesweeper import STATUS_WON
from ..models import db
from ..models.game import Game
from ..models.score import Score

# Default number of rows returned per difficulty on the leaderboard.
DEFAULT_LIMIT = 10


class ScoreError(Exception):
    """Base for recoverable score-submission failures.

    ``status`` is the HTTP code the API layer should surface, so callers map an
    exception straight to a response without re-deciding the code.
    """

    status = 400


class GameNotFound(ScoreError):
    """No game exists for the submitted ``gameId``."""

    status = 404


class GameNotWon(ScoreError):
    """The referenced game is not in the ``won`` state (still playing or lost)."""

    status = 422


class DuplicateScore(ScoreError):
    """A score has already been recorded for this game."""

    status = 409


class InvalidTiming(ScoreError):
    """The game is won but is missing the timestamps needed to time it.

    This should not happen in normal play (a won game always has both marks) but
    is guarded so a corrupt row yields a clean 422 rather than a 500.
    """

    status = 422


def top_scores(difficulty: str, limit: int = DEFAULT_LIMIT) -> list[Score]:
    """Return the best (lowest ``seconds``) scores for one difficulty.

    Sorted ascending by time, then by ``created_at`` so ties are stable and the
    earliest achiever of a tied time ranks first. Filtered strictly by
    difficulty, so an Expert time never appears under Beginner.
    """
    stmt = (
        select(Score)
        .where(Score.difficulty == difficulty)
        .order_by(Score.seconds.asc(), Score.created_at.asc())
        .limit(limit)
    )
    return list(db.session.scalars(stmt))


def record_score(game_id: int, name: str) -> tuple[str, list[Score]]:
    """Validate and persist a score for a won game; return its leaderboard.

    Returns ``(difficulty, top_scores)`` so the caller can echo the updated
    board without re-querying the game. ``name`` is assumed already trimmed and
    length-checked by :class:`~app.schemas.score.SubmitScoreRequest`.
    """
    game = db.session.get(Game, game_id)
    if game is None:
        raise GameNotFound(f'No game with id {game_id}')
    if game.status != STATUS_WON:
        raise GameNotWon(f'Game {game_id} is not won (status={game.status})')

    existing = db.session.scalar(
        select(Score).where(Score.game_id == game_id)
    )
    if existing is not None:
        raise DuplicateScore(f'Game {game_id} already has a recorded score')

    if game.first_move_at is None or game.ended_at is None:
        raise InvalidTiming(f'Game {game_id} is missing timing information')

    # Authoritative elapsed time: derived solely from server-stored timestamps.
    # Rounded to the nearest whole second to match the display-only client timer.
    elapsed = (game.ended_at - game.first_move_at).total_seconds()
    seconds = max(0, round(elapsed))

    score = Score(
        game_id=game_id,
        name=name,
        difficulty=game.difficulty,
        seconds=seconds,
    )
    db.session.add(score)
    db.session.commit()

    return game.difficulty, top_scores(game.difficulty)
