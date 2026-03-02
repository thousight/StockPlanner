"""replace_is_deleted_with_status_enum

Revision ID: bc7aa1c87155
Revises: 297d6b7a9d01
Create Date: 2026-03-01 23:11:54.673203

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc7aa1c87155'
down_revision: Union[str, Sequence[str], None] = '297d6b7a9d01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the enum type
    record_status = sa.Enum('ACTIVE', 'INACTIVE', name='recordstatus')
    record_status.create(op.get_bind(), checkfirst=True)

    # Add the column with a default value
    op.add_column('chat_threads', sa.Column('status', record_status, nullable=False, server_default='ACTIVE'))
    op.add_column('transactions', sa.Column('status', record_status, nullable=False, server_default='ACTIVE'))

    # Update the data
    op.execute("UPDATE chat_threads SET status = 'INACTIVE' WHERE is_deleted = True")
    op.execute("UPDATE transactions SET status = 'INACTIVE' WHERE is_deleted = True")

    # Drop the old column
    op.drop_column('chat_threads', 'is_deleted')
    op.drop_column('transactions', 'is_deleted')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('transactions', sa.Column('is_deleted', sa.BOOLEAN(), autoincrement=False, nullable=True, server_default='false'))
    op.add_column('chat_threads', sa.Column('is_deleted', sa.BOOLEAN(), autoincrement=False, nullable=True, server_default='false'))

    # Revert the data
    op.execute("UPDATE chat_threads SET is_deleted = True WHERE status = 'INACTIVE'")
    op.execute("UPDATE transactions SET is_deleted = True WHERE status = 'INACTIVE'")

    op.drop_column('transactions', 'status')
    op.drop_column('chat_threads', 'status')
    
    # We might want to drop the enum type here, but it can be tricky if it's used elsewhere
    # sa.Enum(name='recordstatus').drop(op.get_bind(), checkfirst=True)
