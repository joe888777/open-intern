"""initial schema: memories and thread_meta

Revision ID: 6b6009bdebb2
Revises:
Create Date: 2026-03-21 20:54:59.881303

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '6b6009bdebb2'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # memories table (may already exist — use if_not_exists)
    op.create_table('memories',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('scope', sa.String(), nullable=False),
        sa.Column('scope_id', sa.String(), nullable=False, server_default=''),
        sa.Column('source', sa.String(), nullable=False, server_default=''),
        sa.Column('importance', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('metadata_json', sa.Text(), nullable=False, server_default='{}'),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True,
    )
    op.create_index('ix_memories_scope', 'memories', ['scope'], if_not_exists=True)
    op.create_index('ix_memories_scope_id', 'memories', ['scope_id'], if_not_exists=True)
    op.create_index(
        'ix_memories_scope_scope_id', 'memories', ['scope', 'scope_id'], if_not_exists=True,
    )

    # thread_meta table
    op.create_table('thread_meta',
        sa.Column('thread_id', sa.String(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False, server_default=''),
        sa.Column('created_at', sa.String(), nullable=False, server_default=''),
        sa.PrimaryKeyConstraint('thread_id'),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table('thread_meta')
    # Don't drop memories on downgrade — data loss risk
