"""create todos table

Revision ID: 36d4aad6f191
Revises: 8b9e767b2103
Create Date: 2026-10-12 21:19:48.817295

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36d4aad6f191'
down_revision: Union[str, Sequence[str], None] = '8b9e767b2103'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "todos",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=True),
        sa.Column("priority", sa.Integer, nullable=False),
        sa.Column("completed", sa.Boolean, nullable=False, server_default=sa.sql.expression.false()),
        sa.Column("owner_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        # sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        # sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("todos")
