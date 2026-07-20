"""Minesweeper game model.

Stores the *entire* authoritative game state on the server. The browser is a
thin renderer that only ever sees what the redacting serializer chooses to
expose, so every piece of hidden information (mine positions especially) lives
here and never leaves the server until the game is over.

Design notes / why this shape:
- ``mine_positions``, ``revealed`` and ``flags`` are ``JSON`` columns holding
  lists of ``[row, col]`` pairs. JSON is portable across the two backends this
  project targets (PostgreSQL in dev/prod, SQLite in tests) and keeps a game a
  single row — no join tables to reconstruct board state.
- ``mine_positions`` is ``None`` until the first reveal. First-click safety
  requires that we know the safe cell *before* placing mines, so mines are
  deliberately not generated at creation time.
- ``first_move_at`` / ``ended_at`` are recorded so the Step 2 leaderboard can
  compute an authoritative, un-gameable duration (``ended_at - first_move_at``)
  without trusting the client clock. They are nullable because a freshly
  created / in-progress game has not reached those moments yet.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import db

# Cell coordinates are stored/exchanged as ``[row, col]`` pairs.
Coord = list[int]


class Game(db.Model):  # type: ignore[name-defined, misc]
    """A single Minesweeper game and its full server-side state."""

    __tablename__ = 'games'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Board shape. Stored per-game so Step 2 difficulty presets need no schema
    # change — the game already carries its own dimensions and mine budget.
    rows: Mapped[int] = mapped_column(Integer, nullable=False)
    cols: Mapped[int] = mapped_column(Integer, nullable=False)
    mine_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Server-only hidden state. ``mine_positions`` is null until first reveal.
    mine_positions: Mapped[list[Coord] | None] = mapped_column(db.JSON, nullable=True)
    revealed: Mapped[list[Coord]] = mapped_column(db.JSON, nullable=False, default=list)
    flags: Mapped[list[Coord]] = mapped_column(db.JSON, nullable=False, default=list)

    # 'playing' | 'won' | 'lost'
    status: Mapped[str] = mapped_column(String(16), nullable=False, default='playing')

    started_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    first_move_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f'<Game id={self.id} status={self.status} {self.rows}x{self.cols}>'
