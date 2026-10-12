"""create phone number column for users table

Revision ID: d874487ff39f
Revises: 36d4aad6f191
Create Date: 2026-10-12 21:37:53.270555

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd874487ff39f'
down_revision: Union[str, Sequence[str], None] = '36d4aad6f191'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("phone_number", sa.String, nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "phone_number")
