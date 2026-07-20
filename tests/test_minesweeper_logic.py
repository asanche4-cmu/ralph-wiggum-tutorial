"""Unit tests for the server-authoritative Minesweeper engine.

These are the highest-value tests: the board rules (first-click safety,
flood-fill, win/loss) are pure and deterministic once mine positions are fixed,
so they are exercised directly by injecting ``mine_positions`` (which suppresses
random placement on the first reveal) rather than relying on RNG.
"""
from __future__ import annotations

from app.controllers import minesweeper as ms


def make_game(rows: int = 9, cols: int = 9, mine_count: int = 10):  # type: ignore[no-untyped-def]
    """A fresh game with no mines placed yet."""
    return ms.new_game(rows, cols, mine_count)


def revealed_set(game) -> set[tuple[int, int]]:  # type: ignore[no-untyped-def]
    return {(r, c) for r, c in game.revealed}


class TestMinePlacement:
    def test_place_mines_count(self) -> None:
        game = make_game()
        ms.place_mines(game, 4, 4)
        assert game.mine_positions is not None
        assert len(game.mine_positions) == ms.MINE_COUNT

    def test_first_click_and_neighbors_are_safe(self) -> None:
        """Neither the clicked cell nor its 8 neighbors may hold a mine."""
        game = make_game()
        ms.place_mines(game, 4, 4)
        mines = {(r, c) for r, c in game.mine_positions}
        safe = {(4, 4), *ms.neighbors(4, 4, 9, 9)}
        assert mines.isdisjoint(safe)

    def test_place_mines_records_first_move_time(self) -> None:
        game = make_game()
        ms.place_mines(game, 0, 0)
        assert game.first_move_at is not None


class TestFirstRevealSafety:
    def test_first_reveal_never_loses(self) -> None:
        """Repeated fresh first-clicks must never hit a mine (RNG placement)."""
        for _ in range(50):
            game = make_game()
            ms.reveal(game, 0, 0)
            assert game.status != ms.STATUS_LOST
            assert (0, 0) in revealed_set(game)


class TestFloodFill:
    def test_zero_cell_floods_contiguous_region(self) -> None:
        """Revealing a zero-adjacency cell reveals the whole empty region and
        its numbered border, but never the mine itself."""
        game = make_game(rows=5, cols=5, mine_count=1)
        game.mine_positions = [[4, 4]]  # inject; suppresses random placement
        ms.reveal(game, 0, 0)
        revealed = revealed_set(game)
        # All 24 non-mine cells are reachable from (0,0) with a single mine
        # in the corner, so flood-fill reveals every one of them.
        assert len(revealed) == 24
        assert (4, 4) not in revealed
        # (3,3) borders the mine (adjacent==1); revealed but not expanded.
        assert (3, 3) in revealed

    def test_numbered_cell_does_not_flood(self) -> None:
        """Clicking a numbered cell reveals only that cell."""
        game = make_game(rows=5, cols=5, mine_count=1)
        game.mine_positions = [[0, 2]]  # (0,1) is adjacent -> value 1
        ms.reveal(game, 0, 1)
        assert revealed_set(game) == {(0, 1)}
        assert game.status == ms.STATUS_PLAYING


class TestWinLoss:
    def test_revealing_mine_loses_and_sets_end_time(self) -> None:
        game = make_game(rows=5, cols=5, mine_count=1)
        game.mine_positions = [[2, 2]]
        ms.reveal(game, 2, 2)
        assert game.status == ms.STATUS_LOST
        assert game.ended_at is not None

    def test_revealing_all_safe_cells_wins(self) -> None:
        game = make_game(rows=5, cols=5, mine_count=1)
        game.mine_positions = [[4, 4]]
        ms.reveal(game, 0, 0)  # floods all 24 non-mine cells
        assert game.status == ms.STATUS_WON
        assert game.ended_at is not None

    def test_win_requires_all_safe_cells(self) -> None:
        """Revealing only some safe cells is not a win.

        On a 1x3 board with the mine in the middle, clicking an end cell is a
        numbered (non-flooding) reveal, so one of the two safe cells stays
        hidden and the game remains in progress.
        """
        game = make_game(rows=1, cols=3, mine_count=1)
        game.mine_positions = [[0, 1]]
        ms.reveal(game, 0, 0)  # numbered cell, reveals only itself
        assert revealed_set(game) == {(0, 0)}
        assert game.status == ms.STATUS_PLAYING


class TestFlagging:
    def test_toggle_flag_adds_and_removes(self) -> None:
        game = make_game()
        ms.toggle_flag(game, 0, 0)
        assert [0, 0] in game.flags
        ms.toggle_flag(game, 0, 0)
        assert [0, 0] not in game.flags

    def test_cannot_flag_revealed_cell(self) -> None:
        game = make_game(rows=5, cols=5, mine_count=1)
        game.mine_positions = [[4, 4]]
        ms.reveal(game, 0, 0)
        ms.toggle_flag(game, 0, 0)  # (0,0) is revealed -> rejected
        assert [0, 0] not in game.flags

    def test_flagged_cell_is_not_revealed(self) -> None:
        game = make_game(rows=5, cols=5, mine_count=1)
        game.mine_positions = [[4, 4]]
        ms.toggle_flag(game, 0, 0)
        ms.reveal(game, 0, 0)  # flagged -> no-op
        assert (0, 0) not in revealed_set(game)

    def test_over_flagging_allowed(self) -> None:
        """More flags than mines is permitted and does not break the game."""
        game = make_game(rows=5, cols=5, mine_count=1)
        for cell in [(0, 0), (0, 1), (0, 2), (0, 3)]:
            ms.toggle_flag(game, *cell)
        assert len(game.flags) == 4
        assert game.status == ms.STATUS_PLAYING


class TestGameOverGuards:
    def test_no_moves_after_loss(self) -> None:
        game = make_game(rows=5, cols=5, mine_count=1)
        game.mine_positions = [[2, 2]]
        ms.reveal(game, 2, 2)  # loss
        before = revealed_set(game)
        ms.reveal(game, 0, 0)  # ignored
        ms.toggle_flag(game, 0, 0)  # ignored
        assert revealed_set(game) == before
        assert game.flags == []
