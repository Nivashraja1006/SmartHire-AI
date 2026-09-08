"""Add Phase 10 interview scheduling fields

Revision ID: d21f10a0c7e1
Revises: b44605147bf0
"""
from alembic import op
import sqlalchemy as sa

revision = 'd21f10a0c7e1'
down_revision = 'b44605147bf0'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('interviews', schema=None) as batch_op:
        batch_op.add_column(sa.Column('duration_minutes', sa.Integer(), server_default='60', nullable=False))
        batch_op.add_column(sa.Column('meeting_link', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('location', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('created_by', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_interviews_created_by', 'users', ['created_by'], ['id'], ondelete='SET NULL')
        batch_op.create_index('ix_interviews_created_by', ['created_by'], unique=False)


def downgrade():
    with op.batch_alter_table('interviews', schema=None) as batch_op:
        batch_op.drop_index('ix_interviews_created_by')
        batch_op.drop_constraint('fk_interviews_created_by', type_='foreignkey')
        batch_op.drop_column('created_by')
        batch_op.drop_column('location')
        batch_op.drop_column('meeting_link')
        batch_op.drop_column('duration_minutes')
