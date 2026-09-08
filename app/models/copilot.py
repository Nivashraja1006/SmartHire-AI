from __future__ import annotations

from datetime import datetime

from app import db


class CopilotConversation(db.Model):
    __tablename__ = 'copilot_conversations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='SET NULL'), nullable=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=db.func.now())

    messages = db.relationship('CopilotMessage', back_populates='conversation', cascade='all, delete-orphan', lazy='dynamic')


class CopilotMessage(db.Model):
    __tablename__ = 'copilot_messages'
    __table_args__ = (db.Index('ix_copilot_messages_conversation_created', 'conversation_id', 'created_at'),)

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('copilot_conversations.id', ondelete='CASCADE'), nullable=False)
    sender = db.Column(db.String(16), nullable=False)
    message = db.Column(db.Text, nullable=False)
    intent = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, server_default=db.func.now())

    conversation = db.relationship('CopilotConversation', back_populates='messages')