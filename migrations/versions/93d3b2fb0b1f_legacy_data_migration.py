"""legacy data migration

Revision ID: 93d3b2fb0b1f
Revises: e36f860593e9
Create Date: 2026-03-02 22:35:40.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93d3b2fb0b1f'
down_revision: Union[str, None] = '52e6b0e16038'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    target_uuid = '019cb265-1862-76d0-8ebb-10273b096f66'
    legacy_ids = ['default_user', 'test-user']
    tables = ['transactions', 'holdings', 'daily_snapshots', 'chat_threads', 'reports', 'assets']
    
    # We already verified the user exists in gsd-executor run
    for table in tables:
        for old_id in legacy_ids:
            op.execute(f"UPDATE {table} SET user_id = '{target_uuid}' WHERE user_id = '{old_id}'")


def downgrade() -> None:
    # No downgrade path for data cleanup
    pass
