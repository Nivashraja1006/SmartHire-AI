"""Add Phase 11 AI audit records

Revision ID: e42b11c8f6a0
Revises: d21f10a0c7e1
"""
from alembic import op
import sqlalchemy as sa

revision = 'e42b11c8f6a0'
down_revision = 'd21f10a0c7e1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('ai_audits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('operation', sa.String(length=64), nullable=False),
        sa.Column('input_type', sa.String(length=64), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=24), nullable=False),
        sa.Column('algorithm', sa.String(length=120), nullable=True),
        sa.Column('engine_version', sa.String(length=32), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('error_type', sa.String(length=160), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('ai_audits') as batch_op:
        batch_op.create_index('ix_ai_audits_operation_created', ['operation', 'created_at'], unique=False)
        batch_op.create_index('ix_ai_audits_status', ['status'], unique=False)


def downgrade():
    with op.batch_alter_table('ai_audits') as batch_op:
        batch_op.drop_index('ix_ai_audits_status')
        batch_op.drop_index('ix_ai_audits_operation_created')
    op.drop_table('ai_audits')
