"""Tests for the Minesweeper game view.

The backend renders only the HTML shell; all game logic lives behind ``/api``.
These tests verify the shell contract: the homepage returns 200, advertises the
Minesweeper title, and includes the ``data-island="minesweeper"`` hook that
``main.ts`` uses to mount the React board.

The ``TestErrorHandlers`` class is retained from the scaffold so error-handler
coverage (HTML vs JSON content negotiation) survives independently of the game.
"""
from __future__ import annotations

import json
from typing import Any

from flask.testing import FlaskClient


class TestGamePage:
    """Tests for the main HTML page that hosts the game."""

    def test_index_returns_html(self, client: FlaskClient[Any]) -> None:
        """GET / should return a 200 HTML page for Minesweeper."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Minesweeper' in response.data

    def test_index_contains_island_mount(self, client: FlaskClient[Any]) -> None:
        """Index page should contain the minesweeper island mount point."""
        response = client.get('/')
        assert b'data-island="minesweeper"' in response.data

    def test_index_title(self, client: FlaskClient[Any]) -> None:
        """The page <title> should advertise Minesweeper."""
        response = client.get('/')
        assert b'<title>Minesweeper</title>' in response.data


class TestErrorHandlers:
    """Tests for error handling (content negotiation between HTML and JSON)."""

    def test_404_html(self, client: FlaskClient[Any]) -> None:
        """404 should return HTML for browser requests."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        assert b'Page Not Found' in response.data or b'404' in response.data

    def test_404_json(self, client: FlaskClient[Any]) -> None:
        """404 should return JSON for API requests."""
        response = client.get(
            '/nonexistent',
            headers={'Accept': 'application/json'}
        )
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
