"""Initial migration

Revision ID: 001_initial_tables
Revises: 
Create Date: 2026-02-04 12:40:30.170279

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import ENUM


# revision identifiers, used by Alembic.
revision: str = '001_initial_tables'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('membership_type', sa.String(length=20), nullable=True),
        sa.Column('hashed_password', sa.String(length=100), nullable=True),
        sa.Column('status', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_name'), 'users', ['name'], unique=False)

    # Create memberships table
    op.create_table('memberships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_memberships_id'), 'memberships', ['id'], unique=False)

    # Create gym_classes table
    op.create_table('gym_classes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('instructor', sa.String(length=100), nullable=True),
        sa.Column('schedule', sa.DateTime(), nullable=True),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gym_classes_id'), 'gym_classes', ['id'], unique=False)

    # Create attendance table
    op.create_table('attendance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('class_id', sa.Integer(), nullable=True),
        sa.Column('check_in_time', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['class_id'], ['gym_classes.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_attendance_id'), 'attendance', ['id'], unique=False)

    # Create facial_encodings table
    op.create_table('facial_encodings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('encoding', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_facial_encodings_id'), 'facial_encodings', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop facial_encodings table
    op.drop_index(op.f('ix_facial_encodings_id'), table_name='facial_encodings')
    op.drop_table('facial_encodings')

    # Drop attendance table
    op.drop_index(op.f('ix_attendance_id'), table_name='attendance')
    op.drop_table('attendance')

    # Drop gym_classes table
    op.drop_index(op.f('ix_gym_classes_id'), table_name='gym_classes')
    op.drop_table('gym_classes')

    # Drop memberships table
    op.drop_index(op.f('ix_memberships_id'), table_name='memberships')
    op.drop_table('memberships')

    # Drop users table
    op.drop_index(op.f('ix_users_name'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
