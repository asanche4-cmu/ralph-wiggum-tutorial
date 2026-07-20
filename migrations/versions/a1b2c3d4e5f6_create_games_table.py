"""create games table

Introduces the server-authoritative Minesweeper game state. A game is a single
row: the hidden board (``mine_positions``), the ``revealed`` and ``flags`` sets,
the ``status`` and the timing columns all live together as JSON / scalar
columns so no join is needed to reconstruct or redact board state.

JSON columns are used for the coordinate lists because they are portable across
this project's two backends (PostgreSQL in dev/prod, SQLite in tests).

Chains after the drop-hello migration so ``script/setup`` stays reproducible.

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2026-07-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rows', sa.Integer(), nullable=False),
        sa.Column('cols', sa.Integer(), nullable=False),
        sa.Column('mine_count', sa.Integer(), nullable=False),
        sa.Column('mine_positions', sa.JSON(), nullable=True),
        sa.Column('revealed', sa.JSON(), nullable=False),
        sa.Column('flags', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('first_move_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('games')
