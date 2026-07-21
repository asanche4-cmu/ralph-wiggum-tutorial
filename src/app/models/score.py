"""Leaderboard score model.

A ``Score`` is a permanent, DB-backed record of a completed (won) game's time.
It is what makes the leaderboard survive server restarts — the base game rows
are transient play state, but scores are the lasting record.

Design notes / why this shape:
- ``game_id`` is a foreign key to ``games`` *and* ``unique``. The uniqueness is
  the concrete mechanism that enforces "a game can be scored only once": a
  second submission for the same game hits the constraint. The FK also lets the
  controller re-check the game's ``status`` at submission time.
- ``difficulty`` and ``seconds`` are denormalized onto the score (rather than
  read through the FK every query) so the leaderboard — the hot read path — can
  filter and sort on a single table with no join.
- ``seconds`` is computed authoritatively on the server from the game's
  ``first_move_at``/``ended_at``; the client never supplies it, so the board
  cannot be gamed from the browser.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import db


class Score(db.Model):  # type: ignore[name-defined, misc]
    """A recorded completion time for a single won game."""

    __tablename__ = 'scores'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # One score per game: the unique FK both dedupes submissions and ties the
    # score back to the game whose status/timing it was derived from.
    game_id: Mapped[int] = mapped_column(
        ForeignKey('games.id'), nullable=False, unique=True
    )

    name: Mapped[str] = mapped_column(String(20), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(16), nullable=False)
    seconds: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f'<Score id={self.id} {self.difficulty} {self.seconds}s "{self.name}">'
