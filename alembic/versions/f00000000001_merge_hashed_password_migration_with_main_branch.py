"""Merge hashed_password migration with main branch

Revision ID: f00000000001
Revises: bade1f9226ee, ce3a9b8f0d6f
Create Date: 2026-02-09 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f00000000001'
down_revision: Union[str, Sequence[str], None] = ('bade1f9226ee', 'ce3a9b8f0d6f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # This is a merge migration, so no schema changes are needed
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # This is a merge migration, so no schema changes are needed
    pass