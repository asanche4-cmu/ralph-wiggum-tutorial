"""Server-authoritative Minesweeper game logic.

This module is the *only* place board rules live. The browser never runs any of
this; it merely sends reveal/flag coordinates and renders whatever the redacting
serializer returns. Keeping the rules here (and dimension-driven rather than
hard-coded to 9x9) is what makes the game cheat-resistant and lets Step 2 add
difficulty presets without touching reveal/flood-fill/win logic.

Key invariants enforced here:
- First-click safety: mines are placed only on the first reveal, excluding the
  clicked cell *and its 8 neighbors*, so the opening click never loses.
- Flood-fill is iterative (explicit stack), never recursive, so a large empty
  region on a big board can't overflow the Python call stack.
- ``revealed`` never contains a mine: revealing a mine ends the game instead.
  That invariant is what makes win detection a simple count comparison.
"""
from __future__ import annotations

import random
from datetime import datetime
from typing import Iterator

from ..models.game import Coord, Game

# Difficulty presets: the single source of truth for board dimensions and mine
# budgets. ``(rows, cols, mine_count)`` per difficulty. The engine below is fully
# dimension-driven, so adding presets never touches reveal/flood-fill/win logic.
DIFFICULTIES: dict[str, tuple[int, int, int]] = {
    'beginner': (9, 9, 10),
    'intermediate': (16, 16, 40),
    'expert': (16, 30, 99),
}

# Beginner is the default so a no-body ``POST /api/games`` (and the island's
# mount) keeps the base 9x9/10 behaviour that existing tests/E2E assert.
DEFAULT_DIFFICULTY = 'beginner'

# Base-system board preset (Beginner) kept as bare constants for the engine's
# ``new_game`` defaults and unit tests that construct boards dimension-by-hand.
ROWS, COLS, MINE_COUNT = DIFFICULTIES[DEFAULT_DIFFICULTY]

# Game status values surfaced to the client.
STATUS_PLAYING = 'playing'
STATUS_WON = 'won'
STATUS_LOST = 'lost'


class UnknownDifficulty(ValueError):
    """Raised when a caller requests a difficulty not in ``DIFFICULTIES``.

    The API layer turns this into a 400 so the client learns the value was
    rejected rather than silently coerced.
    """


def neighbors(row: int, col: int, rows: int, cols: int) -> Iterator[tuple[int, int]]:
    """Yield the in-bounds coordinates of the 8 cells surrounding (row, col)."""
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, col + dc
            if 0 <= r < rows and 0 <= c < cols:
                yield r, c


def count_adjacent(mines: set[tuple[int, int]], row: int, col: int,
                   rows: int, cols: int) -> int:
    """Number of mines in the 8 cells surrounding (row, col)."""
    return sum(1 for nb in neighbors(row, col, rows, cols) if nb in mines)


def _as_set(coords: list[Coord] | None) -> set[tuple[int, int]]:
    """Convert a stored JSON list of [row, col] pairs into a set of tuples."""
    if not coords:
        return set()
    return {(int(r), int(c)) for r, c in coords}


def _as_list(coords: set[tuple[int, int]]) -> list[Coord]:
    """Convert a set of tuples back into a sorted JSON-serializable list."""
    return [[r, c] for r, c in sorted(coords)]


def new_game(
    rows: int = ROWS,
    cols: int = COLS,
    mine_count: int = MINE_COUNT,
    difficulty: str = DEFAULT_DIFFICULTY,
) -> Game:
    """Create a fresh game with no mines placed yet (first-click safety).

    ``difficulty`` is stored purely as a label (the leaderboard partitions by
    it); the board shape comes from ``rows``/``cols``/``mine_count``. Prefer
    :func:`new_game_for_difficulty` when creating from a preset name so the label
    and dimensions can never drift apart.
    """
    return Game(
        rows=rows,
        cols=cols,
        mine_count=mine_count,
        difficulty=difficulty,
        mine_positions=None,
        revealed=[],
        flags=[],
        status=STATUS_PLAYING,
    )


def new_game_for_difficulty(difficulty: str = DEFAULT_DIFFICULTY) -> Game:
    """Create a game from a named preset, keeping label and dimensions in sync.

    Raises :class:`UnknownDifficulty` for any name not in :data:`DIFFICULTIES`
    so the API can reject it with a 400 rather than fabricating a board.
    """
    if difficulty not in DIFFICULTIES:
        raise UnknownDifficulty(difficulty)
    rows, cols, mine_count = DIFFICULTIES[difficulty]
    return new_game(rows, cols, mine_count, difficulty)


def place_mines(game: Game, safe_row: int, safe_col: int) -> None:
    """Place ``mine_count`` mines, excluding the safe cell and its 8 neighbors.

    Called exactly once, on the first reveal. Records ``first_move_at`` so the
    Step 2 leaderboard can derive an authoritative duration.
    """
    safe = {(safe_row, safe_col)}
    safe.update(neighbors(safe_row, safe_col, game.rows, game.cols))

    candidates = [
        (r, c)
        for r in range(game.rows)
        for c in range(game.cols)
        if (r, c) not in safe
    ]
    # Guard against pathologically small boards; never sample more than exist.
    count = min(game.mine_count, len(candidates))
    chosen = random.sample(candidates, count)

    game.mine_positions = _as_list(set(chosen))
    game.first_move_at = datetime.utcnow()


def reveal(game: Game, row: int, col: int) -> None:
    """Reveal (row, col), placing mines on first reveal and flood-filling zeros.

    No-op if the game is over, or the target cell is flagged or already
    revealed. Revealing a mine loses the game; revealing a zero-adjacency cell
    iteratively flood-fills the contiguous empty region and its numbered border.
    """
    if game.status != STATUS_PLAYING:
        return

    revealed = _as_set(game.revealed)
    flags = _as_set(game.flags)
    if (row, col) in revealed or (row, col) in flags:
        return

    # First reveal: generate the mine field now that we know the safe cell.
    if game.mine_positions is None:
        place_mines(game, row, col)

    mines = _as_set(game.mine_positions)

    # Stepped on a mine -> loss. Record the cell so the UI can show the boom.
    if (row, col) in mines:
        revealed.add((row, col))
        game.revealed = _as_list(revealed)
        game.status = STATUS_LOST
        game.ended_at = datetime.utcnow()
        return

    # Iterative flood-fill. A zero-adjacency cell expands to its neighbors;
    # numbered cells are revealed but do not expand. Mines and flagged cells are
    # never auto-revealed.
    stack = [(row, col)]
    while stack:
        r, c = stack.pop()
        if (r, c) in revealed or (r, c) in flags or (r, c) in mines:
            continue
        revealed.add((r, c))
        if count_adjacent(mines, r, c, game.rows, game.cols) == 0:
            stack.extend(neighbors(r, c, game.rows, game.cols))

    game.revealed = _as_list(revealed)
    is_won(game)


def toggle_flag(game: Game, row: int, col: int) -> None:
    """Toggle a flag on (row, col).

    Rejected (no-op) if the game is over or the cell is already revealed.
    Over-flagging (more flags than mines) is allowed and does not affect win
    detection, which is based solely on revealed non-mine cells.
    """
    if game.status != STATUS_PLAYING:
        return

    revealed = _as_set(game.revealed)
    if (row, col) in revealed:
        return

    flags = _as_set(game.flags)
    if (row, col) in flags:
        flags.discard((row, col))
    else:
        flags.add((row, col))
    game.flags = _as_list(flags)


def is_won(game: Game) -> bool:
    """Return True (and finalize the win) when every non-mine cell is revealed."""
    if game.mine_positions is None:
        return False
    non_mine_cells = game.rows * game.cols - game.mine_count
    if len(game.revealed) >= non_mine_cells:
        game.status = STATUS_WON
        if game.ended_at is None:
            game.ended_at = datetime.utcnow()
        return True
    return False
