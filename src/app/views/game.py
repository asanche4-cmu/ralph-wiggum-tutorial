"""Game view (route).

Serves the Minesweeper homepage. The page is a thin HTML shell containing a
``[data-island="minesweeper"]`` mount point that the frontend hydrates with the
React island. All game logic lives on the server behind the ``/api`` blueprint;
this view renders no game state itself.
"""
from flask import Blueprint, render_template

game_bp = Blueprint('game', __name__)


@game_bp.route('/')
def index():  # type: ignore[no-untyped-def]
    """Render the Minesweeper game page.

    Serves HTML containing a ``[data-island="minesweeper"]`` mount point that
    ``main.ts`` hydrates with the React board on the client. The board fetches
    its state from the server-authoritative ``/api`` endpoints.
    """
    return render_template('game.html')
