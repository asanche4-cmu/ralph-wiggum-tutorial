"""add difficulty column to games and create scores table

Step 2 (Extension) schema. Two changes in one migration so the chain stays
linear and ``script/setup`` applies both atomically:

1. ``games.difficulty`` — the preset a game was created at. Added with a
   ``server_default`` of ``'beginner'`` so existing rows (created under the
   single-difficulty base system) backfill correctly and the column can be
   NOT NULL.
2. ``scores`` — the persistent leaderboard. ``game_id`` is a FK to ``games``
   *and* unique, which is what enforces "one score per game" at the database
   level (the concrete mechanism behind the no-duplicate-submissions rule).

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'games',
        sa.Column(
            'difficulty',
            sa.String(length=16),
            nullable=False,
            server_default='beginner',
        ),
    )

    op.create_table(
        'scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=20), nullable=False),
        sa.Column('difficulty', sa.String(length=16), nullable=False),
        sa.Column('seconds', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['games.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('game_id'),
    )


def downgrade() -> None:
    op.drop_table('scores')
    op.drop_column('games', 'difficulty')
