"""Tests for difficulty presets.

Preset correctness is deterministic, so these assert dimensions and mine counts
directly — both at the controller (the single source of truth) and end-to-end
through ``POST /api/games``. The regression guard that a *missing* difficulty
still defaults to Beginner is important: the base game's API tests and the E2E
suite depend on a no-body create producing a 9x9/10 board.
"""
from __future__ import annotations

from typing import Any

import pytest
from flask.testing import FlaskClient

from app.controllers import minesweeper as ms


class TestPresetDimensions:
    @pytest.mark.parametrize(
        'difficulty,rows,cols,mine_count',
        [
            ('beginner', 9, 9, 10),
            ('intermediate', 16, 16, 40),
            ('expert', 16, 30, 99),
        ],
    )
    def test_controller_creates_correct_board(
        self, difficulty: str, rows: int, cols: int, mine_count: int
    ) -> None:
        game = ms.new_game_for_difficulty(difficulty)
        assert (game.rows, game.cols, game.mine_count) == (rows, cols, mine_count)
        assert game.difficulty == difficulty

    def test_unknown_difficulty_raises(self) -> None:
        with pytest.raises(ms.UnknownDifficulty):
            ms.new_game_for_difficulty('impossible')


class TestPresetApi:
    @pytest.mark.parametrize(
        'difficulty,rows,cols,mine_count',
        [
            ('beginner', 9, 9, 10),
            ('intermediate', 16, 16, 40),
            ('expert', 16, 30, 99),
        ],
    )
    def test_create_with_difficulty(
        self,
        client: FlaskClient[Any],
        difficulty: str,
        rows: int,
        cols: int,
        mine_count: int,
    ) -> None:
        response = client.post('/api/games', json={'difficulty': difficulty})
        assert response.status_code == 201
        data = response.get_json()
        assert data['difficulty'] == difficulty
        assert data['rows'] == rows
        assert data['cols'] == cols
        assert data['mineCount'] == mine_count
        assert len(data['board']) == rows
        assert all(len(row) == cols for row in data['board'])

    def test_unknown_difficulty_rejected(self, client: FlaskClient[Any]) -> None:
        response = client.post('/api/games', json={'difficulty': 'nightmare'})
        assert response.status_code == 400
        assert 'error' in response.get_json()

    def test_missing_body_defaults_to_beginner(self, client: FlaskClient[Any]) -> None:
        """Regression guard for the base system: no body -> Beginner 9x9/10."""
        response = client.post('/api/games')
        assert response.status_code == 201
        data = response.get_json()
        assert data['difficulty'] == 'beginner'
        assert (data['rows'], data['cols'], data['mineCount']) == (9, 9, 10)
