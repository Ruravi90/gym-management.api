"""Add updated_at column to users table

Revision ID: 7b085aea43c3
Revises: 3b08211379d7
Create Date: 2026-02-09 15:32:25.244411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b085aea43c3'
down_revision: Union[str, Sequence[str], None] = '3b08211379d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add updated_at column to users table
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Update existing records to have a default updated_at value
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE users SET updated_at = created_at WHERE updated_at IS NULL"))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove updated_at column from users table
    op.drop_column('users', 'updated_at')
