"""enhance membership system add types and features

Revision ID: 8f3c0d1e4b5a
Revises: 7b085aea43c3
Create Date: 2026-02-09 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers
revision = '8f3c0d1e4b5a'
down_revision = '7b085aea43c3'
branch_labels = None
depends_on = None


def upgrade():
    # Create membership_types table
    op.create_table('membership_types',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('duration_days', sa.Integer(), nullable=True),
        sa.Column('accesses_allowed', sa.Integer(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Add indexes for membership_types
    op.create_index('idx_membership_types_active', 'membership_types', ['is_active'])
    
    # Add membership_type_id column to memberships table
    op.add_column('memberships', sa.Column('membership_type_id', sa.Integer(), nullable=True))
    
    # Add accesses_used column to memberships table
    op.add_column('memberships', sa.Column('accesses_used', sa.Integer(), default=0, nullable=False))
    
    # Create foreign key constraint
    op.create_foreign_key('fk_memberships_membership_type', 'memberships', 'membership_types', 
                          ['membership_type_id'], ['id'])
    
    # Add index for performance
    op.create_index('idx_memberships_type_status', 'memberships', ['membership_type_id', 'status'])
    op.create_index('idx_memberships_accesses', 'memberships', ['accesses_used', 'membership_type_id'])
    
    # Insert default membership types
    connection = op.get_bind()
    
    # Insert day pass
    connection.execute(
        sa.text("""
        INSERT INTO membership_types (name, duration_days, accesses_allowed, price, description, is_active, created_at, updated_at) 
        VALUES ('Day Pass', 1, 1, 25.00, 'One-day unlimited access', 1, NOW(), NOW())
        """)
    )
    
    # Insert weekly pass
    connection.execute(
        sa.text("""
        INSERT INTO membership_types (name, duration_days, accesses_allowed, price, description, is_active, created_at, updated_at) 
        VALUES ('Weekly Pass', 7, NULL, 40.00, 'Seven-day unlimited access', 1, NOW(), NOW())
        """)
    )
    
    # Insert 5-punch pass
    connection.execute(
        sa.text("""
        INSERT INTO membership_types (name, duration_days, accesses_allowed, price, description, is_active, created_at, updated_at) 
        VALUES ('5-Punch Pass', 30, 5, 100.00, 'Five visits within 30 days', 1, NOW(), NOW())
        """)
    )
    
    # Insert 10-punch pass
    connection.execute(
        sa.text("""
        INSERT INTO membership_types (name, duration_days, accesses_allowed, price, description, is_active, created_at, updated_at) 
        VALUES ('10-Punch Pass', 60, 10, 180.00, 'Ten visits within 60 days', 1, NOW(), NOW())
        """)
    )
    
    # Insert monthly basic
    connection.execute(
        sa.text("""
        INSERT INTO membership_types (name, duration_days, accesses_allowed, price, description, is_active, created_at, updated_at) 
        VALUES ('Monthly Basic', 30, NULL, 55.00, 'Standard monthly membership', 1, NOW(), NOW())
        """)
    )
    
    # Insert monthly premium
    connection.execute(
        sa.text("""
        INSERT INTO membership_types (name, duration_days, accesses_allowed, price, description, is_active, created_at, updated_at) 
        VALUES ('Monthly Premium', 30, NULL, 85.00, 'Premium monthly membership with additional perks', 1, NOW(), NOW())
        """)
    )
    
    # Insert annual membership
    connection.execute(
        sa.text("""
        INSERT INTO membership_types (name, duration_days, accesses_allowed, price, description, is_active, created_at, updated_at) 
        VALUES ('Annual Membership', 365, NULL, 750.00, 'Yearly membership with discount', 1, NOW(), NOW())
        """)
    )
    
    # Insert student monthly
    connection.execute(
        sa.text("""
        INSERT INTO membership_types (name, duration_days, accesses_allowed, price, description, is_active, created_at, updated_at) 
        VALUES ('Student Monthly', 30, NULL, 35.00, 'Discounted monthly membership for students', 1, NOW(), NOW())
        """)
    )
    
    # Insert family monthly
    connection.execute(
        sa.text("""
        INSERT INTO membership_types (name, duration_days, accesses_allowed, price, description, is_active, created_at, updated_at) 
        VALUES ('Family Monthly', 30, NULL, 140.00, 'Monthly membership for up to 4 family members', 1, NOW(), NOW())
        """)
    )


def downgrade():
    # Drop foreign key constraint first
    op.drop_constraint('fk_memberships_membership_type', 'memberships', type_='foreignkey')
    
    # Drop indexes
    op.drop_index('idx_memberships_accesses', table_name='memberships')
    op.drop_index('idx_memberships_type_status', table_name='memberships')
    
    # Drop columns from memberships table
    op.drop_column('memberships', 'accesses_used')
    op.drop_column('memberships', 'membership_type_id')
    
    # Drop indexes from membership_types
    op.drop_index('idx_membership_types_active', table_name='membership_types')
    
    # Drop membership_types table
    op.drop_table('membership_types')