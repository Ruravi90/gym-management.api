"""add price_paid column to memberships table

Revision ID: 9a4b1c2d5e6f
Revises: 8f3c0d1e4b5a
Create Date: 2026-02-09 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '9a4b1c2d5e6f'
down_revision = '8f3c0d1e4b5a'
branch_labels = None
depends_on = None


def upgrade():
    # Add price_paid column to memberships table
    op.add_column('memberships', sa.Column('price_paid', sa.Float(), nullable=True))


def downgrade():
    # Remove price_paid column from memberships table
    op.drop_column('memberships', 'price_paid')