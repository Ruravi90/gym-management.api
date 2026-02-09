"""Initial migration with all tables (safe)

Revision ID: 3b08211379d7
Revises: 
Create Date: 2026-02-09 15:19:11.375762

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b08211379d7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Get the database engine and inspector
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Get list of existing tables
    existing_tables = inspector.get_table_names()
    
    # Create users table if it doesn't exist
    if 'users' not in existing_tables:
        op.create_table('users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('email', sa.String(length=100), nullable=False),
            sa.Column('phone', sa.String(length=20), nullable=True),
            sa.Column('role', sa.String(length=20), nullable=True),
            sa.Column('hashed_password', sa.String(length=100), nullable=False),
            sa.Column('status', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
        op.create_index(op.f('ix_users_name'), 'users', ['name'], unique=False)

    # Create clients table if it doesn't exist
    if 'clients' not in existing_tables:
        op.create_table('clients',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('email', sa.String(length=100), nullable=False),
            sa.Column('phone', sa.String(length=20), nullable=True),
            sa.Column('hashed_password', sa.String(length=100), nullable=True),
            sa.Column('membership_type', sa.String(length=20), nullable=True),
            sa.Column('profile_image', sa.String(length=255), nullable=True),
            sa.Column('status', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_clients_email'), 'clients', ['email'], unique=True)
        op.create_index(op.f('ix_clients_id'), 'clients', ['id'], unique=False)
        op.create_index(op.f('ix_clients_name'), 'clients', ['name'], unique=False)

    # Create attendance table if it doesn't exist
    if 'attendance' not in existing_tables:
        op.create_table('attendance',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('client_id', sa.Integer(), nullable=True),
            sa.Column('check_in', sa.DateTime(), nullable=True),
            sa.Column('check_out', sa.DateTime(), nullable=True),
            sa.Column('date', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_attendance_id'), 'attendance', ['id'], unique=False)

    # Create memberships table if it doesn't exist
    if 'memberships' not in existing_tables:
        op.create_table('memberships',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('client_id', sa.Integer(), nullable=True),
            sa.Column('type', sa.String(length=50), nullable=True),
            sa.Column('start_date', sa.DateTime(), nullable=True),
            sa.Column('end_date', sa.DateTime(), nullable=True),
            sa.Column('price', sa.Float(), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=True),
            sa.Column('payment_status', sa.String(length=20), nullable=True),
            sa.Column('payment_method', sa.String(length=50), nullable=True),
            sa.Column('notes', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_memberships_id'), 'memberships', ['id'], unique=False)

    # Create facial_encodings table if it doesn't exist
    if 'facial_encodings' not in existing_tables:
        op.create_table('facial_encodings',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('client_id', sa.Integer(), nullable=True),
            sa.Column('encoding_data', sa.LargeBinary(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('client_id')
        )
        op.create_index(op.f('ix_facial_encodings_id'), 'facial_encodings', ['id'], unique=False)

    # Create classes table if it doesn't exist
    if 'classes' not in existing_tables:
        op.create_table('classes',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('instructor', sa.String(length=100), nullable=True),
            sa.Column('schedule', sa.DateTime(), nullable=True),
            sa.Column('capacity', sa.Integer(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_classes_id'), 'classes', ['id'], unique=False)
        op.create_index(op.f('ix_classes_name'), 'classes', ['name'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order to respect foreign key constraints
    # Note: This assumes all tables exist and can be dropped
    # In a real scenario, you might want to check if tables exist before dropping
    
    # Check if table exists before dropping
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    if 'classes' in existing_tables:
        op.drop_index(op.f('ix_classes_name'), table_name='classes')
        op.drop_index(op.f('ix_classes_id'), table_name='classes')
        op.drop_table('classes')

    if 'facial_encodings' in existing_tables:
        op.drop_index(op.f('ix_facial_encodings_id'), table_name='facial_encodings')
        op.drop_constraint('facial_encodings_ibfk_1', 'facial_encodings', type_='foreignkey')
        op.drop_table('facial_encodings')

    if 'memberships' in existing_tables:
        op.drop_index(op.f('ix_memberships_id'), table_name='memberships')
        op.drop_constraint('memberships_ibfk_1', 'memberships', type_='foreignkey')
        op.drop_table('memberships')

    if 'attendance' in existing_tables:
        op.drop_index(op.f('ix_attendance_id'), table_name='attendance')
        op.drop_constraint('attendance_ibfk_1', 'attendance', type_='foreignkey')
        op.drop_table('attendance')

    if 'clients' in existing_tables:
        op.drop_index(op.f('ix_clients_name'), table_name='clients')
        op.drop_index(op.f('ix_clients_id'), table_name='clients')
        op.drop_index(op.f('ix_clients_email'), table_name='clients')
        op.drop_table('clients')

    if 'users' in existing_tables:
        op.drop_index(op.f('ix_users_name'), table_name='users')
        op.drop_index(op.f('ix_users_id'), table_name='users')
        op.drop_index(op.f('ix_users_email'), table_name='users')
        op.drop_table('users')
