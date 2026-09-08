from datetime import datetime

from app import db


class AIAudit(db.Model):
    __tablename__ = 'ai_audits'
    __table_args__ = (
        db.Index('ix_ai_audits_operation_created', 'operation', 'created_at'),
        db.Index('ix_ai_audits_status', 'status'),
    )

    id = db.Column(db.Integer, primary_key=True)
    operation = db.Column(db.String(64), nullable=False)
    input_type = db.Column(db.String(64), nullable=False)
    entity_id = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(24), nullable=False, default='completed')
    algorithm = db.Column(db.String(120), nullable=True)
    engine_version = db.Column(db.String(32), nullable=False)
    duration_ms = db.Column(db.Integer, nullable=True)
    error_type = db.Column(db.String(160), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, server_default=db.func.now())
