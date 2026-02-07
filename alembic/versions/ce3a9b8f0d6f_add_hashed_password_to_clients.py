"""add hashed_password to clients

Revision ID: ce3a9b8f0d6f
Revises: 
Create Date: 2026-02-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'ce3a9b8f0d6f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    cols = [c['name'] for c in inspector.get_columns('clients')]
    if 'hashed_password' not in cols:
        op.add_column('clients', sa.Column('hashed_password', sa.String(length=100), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    cols = [c['name'] for c in inspector.get_columns('clients')]
    if 'hashed_password' in cols:
        op.drop_column('clients', 'hashed_password')
