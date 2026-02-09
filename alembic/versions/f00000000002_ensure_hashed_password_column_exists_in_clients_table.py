"""Ensure hashed_password column exists in clients table

Revision ID: f00000000002
Revises: f00000000001
Create Date: 2026-02-09 16:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = 'f00000000002'
down_revision: Union[str, Sequence[str], None] = 'f00000000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    cols = [c['name'] for c in inspector.get_columns('clients')]
    if 'hashed_password' not in cols:
        op.add_column('clients', sa.Column('hashed_password', sa.String(length=100), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    cols = [c['name'] for c in inspector.get_columns('clients')]
    if 'hashed_password' in cols:
        op.drop_column('clients', 'hashed_password')