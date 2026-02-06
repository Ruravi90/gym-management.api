"""Separate user and client models with proper relationships - corrected

Revision ID: b5c2d8e4f1a2
Revises: 9b95a5f6c046
Create Date: 2026-02-04 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5c2d8e4f1a2'
down_revision: Union[str, Sequence[str], None] = '9b95a5f6c046'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add role column to users table if it doesn't exist
    try:
        op.add_column('users', sa.Column('role', sa.String(length=20), nullable=True))
    except:
        pass  # Column may already exist

    # Remove membership_type and profile_image columns from users table if they exist
    try:
        op.drop_column('users', 'membership_type')
    except:
        pass  # Column may not exist
    try:
        op.drop_column('users', 'profile_image')
    except:
        pass  # Column may not exist

    # Now we need to update the foreign key constraints
    # First, update the foreign key for attendance
    try:
        op.drop_constraint('attendance_ibfk_1', 'attendance', type_='foreignkey')
        op.create_foreign_key(None, 'attendance', 'clients', ['client_id'], ['id'])
        op.drop_column('attendance', 'user_id')
    except:
        pass  # May have already been processed

    # Update the foreign key for memberships
    try:
        op.drop_constraint('memberships_ibfk_1', 'memberships', type_='foreignkey')
        op.create_foreign_key(None, 'memberships', 'clients', ['client_id'], ['id'])
        op.drop_column('memberships', 'user_id')
    except:
        pass  # May have already been processed

    # Update the foreign key for facial_encodings
    try:
        op.drop_constraint('facial_encodings_ibfk_1', 'facial_encodings', type_='foreignkey')
        op.drop_constraint('user_id', 'facial_encodings', type_='unique')  # This is the unique constraint
        op.create_unique_constraint(None, 'facial_encodings', ['client_id'])
        op.create_foreign_key(None, 'facial_encodings', 'clients', ['client_id'], ['id'])
        op.drop_column('facial_encodings', 'user_id')
    except:
        pass  # May have already been processed


def downgrade() -> None:
    """Downgrade schema."""
    # Reverse the changes
    op.add_column('facial_encodings', sa.Column('user_id', sa.Integer(), nullable=True))
    op.drop_constraint(None, 'facial_encodings', type_='foreignkey')
    op.drop_constraint(None, 'facial_encodings', type_='unique')
    op.create_foreign_key('facial_encodings_ibfk_1', 'facial_encodings', 'users', ['user_id'], ['id'])
    op.create_index('user_id', 'facial_encodings', ['user_id'], unique=True)
    
    op.add_column('memberships', sa.Column('user_id', sa.Integer(), nullable=True))
    op.drop_constraint(None, 'memberships', type_='foreignkey')
    op.create_foreign_key('memberships_ibfk_1', 'memberships', 'users', ['user_id'], ['id'])
    op.drop_column('memberships', 'client_id')
    
    op.add_column('attendance', sa.Column('user_id', sa.Integer(), nullable=True))
    op.drop_constraint(None, 'attendance', type_='foreignkey')
    op.create_foreign_key('attendance_ibfk_1', 'attendance', 'users', ['user_id'], ['id'])
    op.drop_column('attendance', 'client_id')
    
    op.drop_column('users', 'role')
    op.add_column('users', sa.Column('profile_image', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('membership_type', sa.String(length=20), nullable=True))
    
    op.drop_index(op.f('ix_clients_name'), table_name='clients')
    op.drop_index(op.f('ix_clients_id'), table_name='clients')
    op.drop_index(op.f('ix_clients_email'), table_name='clients')
    op.drop_table('clients')