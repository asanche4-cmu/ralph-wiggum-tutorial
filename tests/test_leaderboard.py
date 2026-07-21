"""Security-style tests for the leaderboard.

The leaderboard is a trust boundary: a client must not be able to record a time
for a game the server didn't mark ``won``, submit twice, or dictate its own
elapsed time. These tests inject games with **seeded server timestamps** and
assert the exact recorded ``seconds`` so the authoritative-timing guarantee is
proven, not assumed. Timestamps are set directly on the row (mirroring the
loss-injection recipe in ``test_api_game.py``) because the test config does no
time mocking.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from flask.testing import FlaskClient

from app.models import db
from app.models.game import Game
from app.models.score import Score

# A fixed base instant; seeded games derive first_move_at/ended_at from it so
# the elapsed time under test is exact and independent of the wall clock.
_BASE = datetime(2026, 1, 1, 12, 0, 0)


def _seed_game(
    status: str = 'won',
    difficulty: str = 'beginner',
    seconds: int = 42,
    timed: bool = True,
) -> Game:
    """Insert a game row in a chosen state with seeded timing, return it."""
    game = Game(
        rows=9,
        cols=9,
        mine_count=10,
        difficulty=difficulty,
        mine_positions=[[0, 0]],
        revealed=[],
        flags=[],
        status=status,
        started_at=_BASE,
        first_move_at=_BASE if timed else None,
        ended_at=_BASE + timedelta(seconds=seconds) if timed else None,
    )
    db.session.add(game)
    db.session.commit()
    return game


class TestRecordScore:
    def test_records_authoritative_time(self, client: FlaskClient[Any]) -> None:
        game = _seed_game(seconds=42)
        response = client.post(
            '/api/leaderboard', json={'gameId': game.id, 'name': 'Ada'}
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['difficulty'] == 'beginner'
        assert data['entries'] == [
            {'name': 'Ada', 'seconds': 42, 'createdAt': data['entries'][0]['createdAt']}
        ]

    def test_client_supplied_duration_is_ignored(self, client: FlaskClient[Any]) -> None:
        """A forged ``seconds``/``duration`` in the body must not affect the time."""
        game = _seed_game(seconds=42)
        response = client.post(
            '/api/leaderboard',
            json={'gameId': game.id, 'name': 'Cheater', 'seconds': 1, 'duration': 0},
        )
        assert response.status_code == 201
        assert response.get_json()['entries'][0]['seconds'] == 42

    def test_name_is_trimmed(self, client: FlaskClient[Any]) -> None:
        game = _seed_game()
        response = client.post(
            '/api/leaderboard', json={'gameId': game.id, 'name': '  Bob  '}
        )
        assert response.status_code == 201
        assert response.get_json()['entries'][0]['name'] == 'Bob'


class TestSubmissionVerification:
    def test_cannot_submit_for_playing_game(self, client: FlaskClient[Any]) -> None:
        game = _seed_game(status='playing', timed=False)
        response = client.post(
            '/api/leaderboard', json={'gameId': game.id, 'name': 'Ada'}
        )
        assert response.status_code == 422

    def test_cannot_submit_for_lost_game(self, client: FlaskClient[Any]) -> None:
        game = _seed_game(status='lost')
        response = client.post(
            '/api/leaderboard', json={'gameId': game.id, 'name': 'Ada'}
        )
        assert response.status_code == 422

    def test_cannot_double_submit(self, client: FlaskClient[Any]) -> None:
        game = _seed_game()
        first = client.post('/api/leaderboard', json={'gameId': game.id, 'name': 'Ada'})
        assert first.status_code == 201
        second = client.post('/api/leaderboard', json={'gameId': game.id, 'name': 'Ada'})
        assert second.status_code == 409
        # Still exactly one score persisted for the game.
        assert db.session.query(Score).filter_by(game_id=game.id).count() == 1

    def test_unknown_game_returns_404(self, client: FlaskClient[Any]) -> None:
        response = client.post('/api/leaderboard', json={'gameId': 999999, 'name': 'Ada'})
        assert response.status_code == 404

    def test_empty_name_rejected(self, client: FlaskClient[Any]) -> None:
        game = _seed_game()
        for name in ('', '   '):
            response = client.post(
                '/api/leaderboard', json={'gameId': game.id, 'name': name}
            )
            assert response.status_code == 400

    def test_overlong_name_rejected(self, client: FlaskClient[Any]) -> None:
        game = _seed_game()
        response = client.post(
            '/api/leaderboard', json={'gameId': game.id, 'name': 'x' * 21}
        )
        assert response.status_code == 400


class TestLeaderboardListing:
    def test_sorted_ascending_and_filtered_by_difficulty(
        self, client: FlaskClient[Any]
    ) -> None:
        slow = _seed_game(difficulty='beginner', seconds=30)
        fast = _seed_game(difficulty='beginner', seconds=10)
        expert = _seed_game(difficulty='expert', seconds=5)
        for game, name in ((slow, 'Slow'), (fast, 'Fast'), (expert, 'Pro')):
            client.post('/api/leaderboard', json={'gameId': game.id, 'name': name})

        beginner = client.get('/api/leaderboard?difficulty=beginner').get_json()
        assert [e['seconds'] for e in beginner['entries']] == [10, 30]
        # An expert time never appears under beginner.
        assert all(e['name'] != 'Pro' for e in beginner['entries'])

        expert_board = client.get('/api/leaderboard?difficulty=expert').get_json()
        assert [e['name'] for e in expert_board['entries']] == ['Pro']

    def test_unknown_difficulty_rejected(self, client: FlaskClient[Any]) -> None:
        assert client.get('/api/leaderboard?difficulty=bogus').status_code == 400

    def test_default_difficulty_is_beginner(self, client: FlaskClient[Any]) -> None:
        game = _seed_game(difficulty='beginner', seconds=7)
        client.post('/api/leaderboard', json={'gameId': game.id, 'name': 'Ada'})
        board = client.get('/api/leaderboard').get_json()
        assert board['difficulty'] == 'beginner'
        assert board['entries'][0]['seconds'] == 7


class TestPersistence:
    def test_score_survives_reload(self, client: FlaskClient[Any]) -> None:
        """AC #8: a recorded score is DB-backed, not in-memory.

        After committing, expire the session so the follow-up read must hit the
        database rather than a cached identity-map object.
        """
        game = _seed_game(seconds=15)
        client.post('/api/leaderboard', json={'gameId': game.id, 'name': 'Ada'})
        db.session.expire_all()

        board = client.get('/api/leaderboard?difficulty=beginner').get_json()
        assert board['entries'][0] == {
            'name': 'Ada',
            'seconds': 15,
            'createdAt': board['entries'][0]['createdAt'],
        }
