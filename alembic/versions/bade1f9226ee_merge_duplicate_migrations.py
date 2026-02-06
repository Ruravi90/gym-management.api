"""Merge duplicate migrations

Revision ID: bade1f9226ee
Revises: a49ef42046dc, b5c2d8e4f1a2
Create Date: 2026-02-04 14:37:46.067658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bade1f9226ee'
down_revision: Union[str, Sequence[str], None] = ('a49ef42046dc', 'b5c2d8e4f1a2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
