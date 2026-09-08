from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter

from flask import current_app

from app import db
from app.models import AIAudit


@contextmanager
def record_ai_operation(operation, input_type, entity_id=None, algorithm='rule-based local'):
    started = perf_counter()
    audit = AIAudit(operation=operation, input_type=input_type, entity_id=entity_id, algorithm=algorithm, engine_version=current_app.config.get('AI_ENGINE_VERSION', '1.0.0'), status='started')
    db.session.add(audit)
    try:
        yield audit
        audit.status = 'completed'
    except Exception as exc:
        audit.status = 'failed'
        audit.error_type = type(exc).__name__
        raise
    finally:
        audit.duration_ms = round((perf_counter() - started) * 1000)
        db.session.commit()


def audit_ai_operation(operation, input_type, entity_id=None, status='completed', algorithm='rule-based local', duration_ms=None, error_type=None):
    audit = AIAudit(operation=operation, input_type=input_type, entity_id=entity_id, status=status, algorithm=algorithm, engine_version=current_app.config.get('AI_ENGINE_VERSION', '1.0.0'), duration_ms=duration_ms, error_type=error_type)
    db.session.add(audit)
    db.session.flush()
    return audit
