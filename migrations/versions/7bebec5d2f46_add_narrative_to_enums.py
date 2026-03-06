"""add_narrative_to_enums

Revision ID: 7bebec5d2f46
Revises: 08f779ec9aee
Create Date: 2026-03-05 19:25:09.229096

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7bebec5d2f46'
down_revision: Union[str, Sequence[str], None] = '08f779ec9aee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add NARRATIVE to ResearchSourceType and ReportCategory enums
    # PostgreSQL doesn't allow ALTER TYPE ... ADD VALUE inside a transaction block easily in some versions/contexts
    # but Alembic usually handles this with op.execute
    op.execute("ALTER TYPE researchsourcetype ADD VALUE 'NARRATIVE'")
    op.execute("ALTER TYPE reportcategory ADD VALUE 'NARRATIVE'")

def downgrade() -> None:
    """Downgrade schema."""
    # PostgreSQL doesn't support removing an enum value easily. 
    # Usually requires recreating the type, which is complex for a simple addition.
    # We will leave downgrade as pass or handle with more complex logic if strictly required.
    pass
