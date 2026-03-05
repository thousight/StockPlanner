"""drop_legacy_checkpoint_tables

Revision ID: f7f06209e6af
Revises: 80ae3fa232bd
Create Date: 2026-03-03 21:43:40.138105

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f7f06209e6af'
down_revision: Union[str, Sequence[str], None] = '80ae3fa232bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop tables managed by langgraph-checkpoint-postgres
    # We use execute with CASCADE to be sure, or just order them correctly
    op.execute("DROP TABLE IF EXISTS checkpoint_writes CASCADE")
    op.execute("DROP TABLE IF EXISTS checkpoint_blobs CASCADE")
    op.execute("DROP TABLE IF EXISTS checkpoints CASCADE")
    op.execute("DROP TABLE IF EXISTS checkpoint_migrations CASCADE")


def downgrade() -> None:
    """Downgrade schema."""
    # Since these were managed by an external library, we don't recreate them here.
    pass
