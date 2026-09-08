# Database

Core entities are users, roles, jobs, candidates, resumes, skills, applications, candidate scores, interviews, notifications, activity logs, and AI audits.

Migrations are managed by Flask-Migrate/Alembic. The Phase 11 migration adds `ai_audits` and follows the Phase 10 interview migration. Production uses MySQL through `DATABASE_URL` or the `MYSQL_*` variables; tests use in-memory SQLite.

Indexes cover ownership, status, timestamps, application joins, score lookup, notification reads, and AI audit status/operation.
