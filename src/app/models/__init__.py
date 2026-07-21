"""Database models package.

Exports all models for easy importing throughout the application. Importing the
model classes here also ensures SQLAlchemy's metadata is populated (so
``db.create_all()`` and Alembic autogenerate both see every table).
"""
from .base import db
from .game import Game
from .score import Score

__all__ = ['db', 'Game', 'Score']
