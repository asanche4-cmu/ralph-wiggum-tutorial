"""API tests for the Minesweeper endpoints.

The centerpiece here is the **redaction / security test**: a response for a
game that is still ``playing`` must never contain mine or adjacency information
for cells the player has not revealed. Because every response flows through the
single redacting serializer, asserting this on the wire proves the guarantee.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from flask.testing import FlaskClient

from app.models import db
from app.models.game import Game


def _create(client: FlaskClient[Any]) -> dict[str, Any]:
    response = client.post('/api/games')
    assert response.status_code == 201
    return response.get_json()


class TestCreateGame:
    def test_create_returns_all_hidden_board(self, client: FlaskClient[Any]) -> None:
        data = _create(client)
        assert data['rows'] == 9
        assert data['cols'] == 9
        assert data['mineCount'] == 10
        assert data['status'] == 'playing'
        assert data['flagsUsed'] == 0
        assert len(data['board']) == 9
        for row in data['board']:
            assert len(row) == 9
            for cell in row:
                assert cell['state'] == 'hidden'
                # Redaction: hidden cells carry no board information at all.
                assert 'mine' not in cell
                assert 'adjacent' not in cell


class TestRedactionSecurity:
    def test_playing_response_never_leaks_mines(self, client: FlaskClient[Any]) -> None:
        """After a reveal, a playing game must expose no mine/adjacency data
        for any unrevealed cell, and no mine flag for any cell."""
        game_id = _create(client)['gameId']
        response = client.post(
            f'/api/games/{game_id}/reveal', json={'row': 4, 'col': 4}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] in ('playing', 'won')

        revealed_any = False
        for row in data['board']:
            for cell in row:
                # No cell ever exposes a mine while the game is not lost.
                assert 'mine' not in cell
                if cell['state'] == 'revealed':
                    revealed_any = True
                    assert 'adjacent' in cell
                else:
                    # Unrevealed cells leak nothing.
                    assert 'adjacent' not in cell
        assert revealed_any  # first click always reveals at least one cell


class TestLossRevealsMines:
    def test_loss_exposes_full_mine_layout(self, client: FlaskClient[Any]) -> None:
        """Injecting a known mine field and stepping on one loses the game and
        returns every mine so the UI can render the exploded board."""
        game_id = _create(client)['gameId']
        game = db.session.get(Game, game_id)
        assert game is not None
        game.mine_positions = [[0, 1], [1, 0], [1, 1]]
        game.first_move_at = datetime.utcnow()
        db.session.commit()

        response = client.post(
            f'/api/games/{game_id}/reveal', json={'row': 0, 'col': 1}
        )
        data = response.get_json()
        assert data['status'] == 'lost'
        for mr, mc in [(0, 1), (1, 0), (1, 1)]:
            assert data['board'][mr][mc].get('mine') is True


class TestFlagging:
    def test_flag_toggles_and_updates_counter(self, client: FlaskClient[Any]) -> None:
        game_id = _create(client)['gameId']
        data = client.post(
            f'/api/games/{game_id}/flag', json={'row': 0, 'col': 0}
        ).get_json()
        assert data['flagsUsed'] == 1
        assert data['board'][0][0]['state'] == 'flagged'

        data = client.post(
            f'/api/games/{game_id}/flag', json={'row': 0, 'col': 0}
        ).get_json()
        assert data['flagsUsed'] == 0
        assert data['board'][0][0]['state'] == 'hidden'


class TestGetGame:
    def test_get_returns_current_state(self, client: FlaskClient[Any]) -> None:
        game_id = _create(client)['gameId']
        response = client.get(f'/api/games/{game_id}')
        assert response.status_code == 200
        assert response.get_json()['gameId'] == game_id


class TestErrorHandling:
    def test_unknown_game_returns_404_json(self, client: FlaskClient[Any]) -> None:
        response = client.get('/api/games/999999')
        assert response.status_code == 404
        assert 'error' in response.get_json()

        response = client.post(
            '/api/games/999999/reveal', json={'row': 0, 'col': 0}
        )
        assert response.status_code == 404
        assert 'error' in response.get_json()

    def test_bad_body_returns_400(self, client: FlaskClient[Any]) -> None:
        game_id = _create(client)['gameId']
        # Wrong type
        r = client.post(f'/api/games/{game_id}/reveal', json={'row': 'x', 'col': 0})
        assert r.status_code == 400
        # Missing fields
        r = client.post(f'/api/games/{game_id}/reveal', json={})
        assert r.status_code == 400
        # Non-JSON body
        r = client.post(
            f'/api/games/{game_id}/reveal',
            data='not json',
            content_type='text/plain',
        )
        assert r.status_code == 400

    def test_out_of_range_returns_400(self, client: FlaskClient[Any]) -> None:
        game_id = _create(client)['gameId']
        r = client.post(
            f'/api/games/{game_id}/reveal', json={'row': 99, 'col': 0}
        )
        assert r.status_code == 400
