"""Controllers package.

Business logic layer that sits between views (routes) and models.
Controllers handle data manipulation and business rules, kept separate from the
HTTP layer so the server-authoritative game rules can be unit-tested without a
request context.
"""
from . import minesweeper

__all__ = ['minesweeper']
