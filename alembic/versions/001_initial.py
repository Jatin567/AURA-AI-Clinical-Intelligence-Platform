"""initial migration

Revision ID: 001
Revises: 
Create Date: 2026-02-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create triage_sessions table
    op.create_table(
        'triage_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('intake_stage', sa.String(length=50), nullable=False),
        sa.Column('triage_level', sa.String(length=50), nullable=True),
        sa.Column('triage_label', sa.String(length=100), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('had_emergency', sa.Boolean(), nullable=False),
        sa.Column('had_crisis_flag', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_triage_sessions_created_at', 'triage_sessions', ['created_at'], unique=False)

    # Create triage_audit_logs table
    op.create_table(
        'triage_audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('event_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('classification_version', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['triage_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_triage_audit_logs_event_type', 'triage_audit_logs', ['event_type'], unique=False)
    op.create_index('ix_triage_audit_logs_session_id', 'triage_audit_logs', ['session_id'], unique=False)

def downgrade():
    op.drop_index('ix_triage_audit_logs_session_id', table_name='triage_audit_logs')
    op.drop_index('ix_triage_audit_logs_event_type', table_name='triage_audit_logs')
    op.drop_table('triage_audit_logs')
    op.drop_index('ix_triage_sessions_created_at', table_name='triage_sessions')
    op.drop_table('triage_sessions')
