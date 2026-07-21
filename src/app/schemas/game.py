"""Pydantic schemas + the redacting serializer for Minesweeper.

This is the single choke point that guarantees hidden state never leaks. Every
API response is built by :func:`serialize_game`, which emits a board where:

- unrevealed cells carry **no** adjacency or mine information at all
  (``adjacent`` / ``mine`` are ``None`` and dropped from the JSON), and
- mine positions are exposed **only** once the game is lost.

Because this is the only path from ``Game`` to the wire, the "mines never leak
for a playing game" security property is enforced in exactly one place and can
be tested directly.
"""
from __future__ import annotations

from pydantic import BaseModel

from ..controllers.minesweeper import count_adjacent
from ..models.game import Game

# Cell states surfaced to the client.
STATE_HIDDEN = 'hidden'
STATE_FLAGGED = 'flagged'
STATE_REVEALED = 'revealed'


class MoveRequest(BaseModel):
    """A reveal/flag request body: the coordinates of the target cell."""

    row: int
    col: int


class CellView(BaseModel):
    """The client-visible view of a single cell.

    ``adjacent`` is set only for revealed non-mine cells; ``mine`` is set only
    for mine cells once the game is lost. For hidden/flagged cells both stay
    ``None`` and are excluded from the serialized JSON, so nothing about the
    hidden layout reaches the browser.
    """

    state: str
    adjacent: int | None = None
    mine: bool | None = None


class GameStateView(BaseModel):
    """The full redacted game state returned by every API endpoint."""

    gameId: int
    difficulty: str
    rows: int
    cols: int
    mineCount: int
    flagsUsed: int
    status: str
    board: list[list[CellView]]


def _coord_set(coords: list[list[int]] | None) -> set[tuple[int, int]]:
    """Convert a stored JSON list of [row, col] pairs into a set of tuples."""
    if not coords:
        return set()
    return {(int(r), int(c)) for r, c in coords}


def _cell_view(
    row: int,
    col: int,
    revealed: set[tuple[int, int]],
    flags: set[tuple[int, int]],
    mines: set[tuple[int, int]],
    lost: bool,
    rows: int,
    cols: int,
) -> CellView:
    """Build the redacted view of one cell."""
    # On loss, every mine is exposed so the UI can render the exploded board.
    if lost and (row, col) in mines:
        return CellView(state=STATE_REVEALED, mine=True)
    # Revealed non-mine cell: expose its adjacency count (0..8).
    if (row, col) in revealed:
        return CellView(
            state=STATE_REVEALED,
            adjacent=count_adjacent(mines, row, col, rows, cols),
        )
    # Flagged-but-not-revealed cell.
    if (row, col) in flags:
        return CellView(state=STATE_FLAGGED)
    # Hidden: no adjacency, no mine info — the redaction guarantee.
    return CellView(state=STATE_HIDDEN)


def serialize_game(game: Game) -> GameStateView:
    """Produce the redacted, client-facing view of a game."""
    revealed = _coord_set(game.revealed)
    flags = _coord_set(game.flags)
    mines = _coord_set(game.mine_positions)
    lost = game.status == 'lost'

    board = [
        [
            _cell_view(r, c, revealed, flags, mines, lost, game.rows, game.cols)
            for c in range(game.cols)
        ]
        for r in range(game.rows)
    ]

    return GameStateView(
        gameId=game.id,
        difficulty=game.difficulty,
        rows=game.rows,
        cols=game.cols,
        mineCount=game.mine_count,
        flagsUsed=len(flags),
        status=game.status,
        board=board,
    )


__all__ = [
    'MoveRequest',
    'CellView',
    'GameStateView',
    'serialize_game',
]
