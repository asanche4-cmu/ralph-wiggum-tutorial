"""Pydantic schemas for the leaderboard wire format.

Mirrors the camelCase, no-alias convention already used by ``schemas/game.py``
(literal ``gameId``/``createdAt`` field names rather than Pydantic aliases) so
the whole API speaks one consistent JSON dialect.

Name validation lives here, in the request schema, so an empty or over-long
name is rejected as a 400 *before* the controller runs — the controller only
ever sees a trimmed, bounded name.
"""
from __future__ import annotations

from pydantic import BaseModel, field_validator

from ..models.score import Score

# Upper bound on a submitted leaderboard name. Kept small: names are display
# labels on a public board, not free text.
MAX_NAME_LENGTH = 20


class SubmitScoreRequest(BaseModel):
    """Body for ``POST /api/leaderboard``: which game, under what name.

    Note there is deliberately **no** duration/seconds field — the elapsed time
    is computed server-side from stored timestamps, so the client has no way to
    report (and thus fake) it. Any extra keys in the body are ignored.
    """

    gameId: int
    name: str

    @field_validator('name')
    @classmethod
    def _clean_name(cls, value: str) -> str:
        """Trim surrounding whitespace; reject empty or over-long names."""
        cleaned = (value or '').strip()
        if not cleaned:
            raise ValueError('Name must not be empty')
        if len(cleaned) > MAX_NAME_LENGTH:
            raise ValueError(f'Name must be at most {MAX_NAME_LENGTH} characters')
        return cleaned


class LeaderboardEntry(BaseModel):
    """One row of the leaderboard as seen by the client."""

    name: str
    seconds: int
    createdAt: str


class LeaderboardView(BaseModel):
    """The leaderboard for a single difficulty, best (lowest) times first."""

    difficulty: str
    entries: list[LeaderboardEntry]


def serialize_leaderboard(difficulty: str, scores: list[Score]) -> LeaderboardView:
    """Build the client-facing leaderboard view for one difficulty."""
    return LeaderboardView(
        difficulty=difficulty,
        entries=[
            LeaderboardEntry(
                name=score.name,
                seconds=score.seconds,
                createdAt=score.created_at.isoformat(),
            )
            for score in scores
        ],
    )


__all__ = [
    'MAX_NAME_LENGTH',
    'SubmitScoreRequest',
    'LeaderboardEntry',
    'LeaderboardView',
    'serialize_leaderboard',
]
