# SmartHire AI — Phase 2 Implementation Plan

## Repository Research

**Current state from Phase 1 (verified):**
- Flask app factory in [app/__init__.py](file:///c:/Users/Nivash%20Raja/OneDrive/Desktop/ranking/app/__init__.py#L13-L58) already exposes module-level `db = SQLAlchemy()`, `migrate = Migrate()`, `socketio = SocketIO()` and wires them in `create_app()`. Inside the app context it already does `from app import models` — so our new models simply need to be imported in `app/models/__init__.py` and they'll be registered.
- [config.py](file:///c:/Users/Nivash%20Raja/OneDrive/Desktop/ranking/config.py#L30-L40) `Config._make_db_url()` already supports both direct `DATABASE_URL` **and** individual `MYSQL_HOST/PORT/USER/PASSWORD/DB` variables. The only mismatch vs Phase 2 request: the env-var is currently `MYSQL_DB` but user asks for `MYSQL_DATABASE`. Plan: **accept both** for backward compatibility (prefer `MYSQL_DATABASE` if set, fall back to `MYSQL_DB`).
- [run.py](file:///c:/Users/Nivash%20Raja/OneDrive/Desktop/ranking/run.py#L1-L15) uses `socketio.run(...)`, which is compatible with all Flask features including Flask-CLI (`flask db ...`) because `create_app()` also works outside the SocketIO runner.
- `.env` is already in `.gitignore` (line 23). Good.
- `PyMySQL` and `cryptography` are already in requirements.txt, but **`Flask-Login` and `Werkzeug[security]` are missing** (User model needs password hashing via `werkzeug.security` and Flask-Login mixin `UserMixin` + session plumbing). Those will be added to requirements.txt.
- `app/models/__init__.py` is an empty stub — this is where we'll import all 12 model modules so SQLAlchemy metadata sees them.
- Landing page verified working 17/17 in Phase 1 — we must run the same smoke test after changes.

**DB availability note:** MySQL Community Edition may or may not be running on this Windows machine. Plan:
- Models, migrations, and seed script are created for MySQL target.
- We'll run the `flask db` commands on a **best-effort** basis. If MySQL isn't reachable the commands will fail — we'll catch that, document the exact setup commands the user must run manually, and still verify everything via SQLite (TestingConfig) programmatic tests to prove model integrity.

---

## Files and Modules

### Files to CREATE (16 new files)
1. `app/models/role.py` — Role model (Admin / Recruiter / Candidate)
2. `app/models/user.py` — User model with hashed passwords, Flask-Login UserMixin, relationship to Role + jobs (as recruiter) + activity_logs + candidate profile
3. `app/models/job.py` — Job model with recruiter FK, employment_type enum, status enum, skills via JobSkill, applications
4. `app/models/skill.py` — Skill model (unique name, category enum)
5. `app/models/job_skill.py` — JobSkill association (job_id, skill_id, importance=Mandatory/Preferred, optional weight), UniqueConstraint(job_id, skill_id)
6. `app/models/candidate.py` — Candidate model with nullable user_id FK, contact fields, experience, skills via CandidateSkill, resumes, applications
7. `app/models/resume.py` — Resume model, candidate FK, processing_status enum, file metadata + extracted_text blob
8. `app/models/candidate_skill.py` — CandidateSkill association (candidate_id, skill_id, proficiency_level, source), UniqueConstraint(candidate_id, skill_id)
9. `app/models/application.py` — Application model (candidate_id, job_id, status enum, applied_at, updated_at), UniqueConstraint(candidate_id, job_id) to prevent double-apply
10. `app/models/candidate_score.py` — CandidateScore per application (overall + 5 sub-scores, recommendation, calculated_at)
11. `app/models/interview.py` — Interview model per application (date/time/type/status/notes)
12. `app/models/activity_log.py` — ActivityLog (user_id FK, activity_type, description, created_at)
13. `seed_data.py` — Root-level idempotent CLI seed script. Seeds 3 roles + 25+ categorized skills if missing. Reads env, calls `create_app()`, pushes app context, commits.
14. `_test_phase2.py` — (Temp) programmatic verification script against in-memory SQLite using TestingConfig. Creates all tables, exercises every model, unique constraints, FKs, relationships. Deleted after completion.
15. `.trae/documents/phase2_implementation_plan.md` — This document.

### Files to MODIFY (4 files)
1. `app/models/__init__.py` — Import every model so they're registered with SQLAlchemy metadata. Also expose them at package level for convenience.
2. `config.py` — Accept both `MYSQL_DATABASE` (preferred) and legacy `MYSQL_DB` env vars. Add `FLASK_LOGIN_LOGIN_VIEW` / `SESSION_PROTECTION` placeholders.
3. `.env.example` — Add `MYSQL_DATABASE=` (new preferred name), keep `MYSQL_DB=` commented as legacy; add `FLASK_APP=run.py` explanation; add a small block showing how to run `flask db ...` via env vars. No real credentials.
4. `requirements.txt` — Add `Flask-Login==0.6.3`; Werkzeug already covers password hashing but add an explicit `Werkzeug[security]` line for clarity.

### Files NOT touched (Phase 1 preserved)
- `app/__init__.py` — keeps existing extension pattern (db/migrate/socketio). Only change: no change needed since `from app import models` already runs inside app context.
- `run.py`, `app/routes/main.py`, templates, static, uploads/.gitkeep, tests/.gitkeep — untouched.
- `.gitignore` — already covers `.env`, `venv/`, `__pycache__/`, uploads, logs.

---

## Implementation Steps (Dependency Order)

1. **Update config + requirements + env template** (so all subsequent steps see new env vars + deps)
   - Edit `config.py` to accept `MYSQL_DATABASE` || `MYSQL_DB`; add Flask-Login related config placeholders.
   - Edit `.env.example` → add `MYSQL_DATABASE=smarthire_ai` line; keep `MYSQL_DB=` commented-out legacy; document commands section comments at top.
   - Edit `requirements.txt` → add `Flask-Login==0.6.3`.

2. **Write 12 model files, import order = dependency order (no circular FKs)**
   Order within models package: `role → skill → user → job → candidate → job_skill → candidate_skill → resume → application → candidate_score → interview → activity_log`.
   - All models inherit `db.Model` from the module-level `db` in `app/__init__.py` (already matches Phase 1 pattern).
   - Use string-based lazy FK targets (e.g. `db.ForeignKey('users.id')`) to avoid circular import issues.
   - Naming conventions: tables use **plural snake_case** (e.g. `user_roles` → no, actually: `roles`, `users`, `jobs`, `skills`, `job_skills`, `candidates`, `resumes`, `candidate_skills`, `applications`, `candidate_scores`, `interviews`, `activity_logs`) — explicit `__tablename__` on every model.
   - `created_at` defaults: `db.DateTime(timezone=True), server_default=db.func.now()`.
   - `updated_at`: `db.DateTime(timezone=True), onupdate=db.func.now()` with default too.
   - Enums stored as plain `db.String(32)` with Python `validates` + class constants (not native SQL ENUM) so migrations stay portable across MySQL/SQLite for testing.
   - User model: `werkzeug.security.generate_password_hash / check_password_hash`, `UserMixin` from `flask_login`, methods `set_password`, `check_password`. Prepare for Flask-Login but don't wire up the `login_manager` yet (Phase 3).
   - `UniqueConstraint('candidate_id', 'job_id', name='uq_applications_candidate_job')` on Application.
   - `UniqueConstraint('job_id', 'skill_id')` on JobSkill.
   - `UniqueConstraint('candidate_id', 'skill_id')` on CandidateSkill.
   - `db.Index('ix_*')` on `users.email`, `roles.name`, `skills.name`, `applications.job_id`, `applications.candidate_id`, `applications.status`, `resumes.candidate_id`, `candidates.email`, `activity_logs.user_id`, `activity_logs.created_at`.
   - Relationships with `back_populates` (not backref) for explicitness and static clarity. Cascade `save-update, merge` only for non-delete relationships; cascade on Job → JobSkill and Candidate → Resume as appropriate.
   - Each model: useful `__repr__` with `id` + natural name field.

3. **Wire them in `app/models/__init__.py`** so `from app import models` pulls them all in (matches Phase 1 factory code).

4. **Create `seed_data.py`** at project root:
   - Idempotent: if roles/skills exist, skip them (don't double-insert).
   - Roles: `Admin`, `Recruiter`, `Candidate`.
   - 25+ categorized skills using the exact list from Phase 2 request (Python, Java, JavaScript, HTML, CSS, React, Flask, Django, Node.js, MySQL, PostgreSQL, MongoDB, Git, GitHub, Docker, AWS, Azure, Pandas, NumPy, Scikit-learn, Selenium, JUnit, REST API, Linux, Power BI).
   - Categories exactly per spec: Programming Language, Frontend, Backend, Database, Cloud, DevOps, AI/ML, Testing, Tools.
   - Usage: `python seed_data.py` — will also tell people this in the final instructions.

5. **Run programmatic tests (in-memory SQLite, TestingConfig):**
   - `_test_phase2.py` script uses `create_app('testing')`, `db.create_all()`, then:
     - imports all 12 models and confirms tablenames exist in metadata
     - seeds roles + skills via seed_data helper
     - creates User (Recruiter) → Job → JobSkill, Candidate → Resume → CandidateSkill, Application → CandidateScore + Interview, ActivityLog
     - checks back_populates relationships (user.jobs → [job], job.recruiter = user)
     - checks unique email constraint (attempting 2 users same email raises IntegrityError after rollback)
     - checks unique application constraint
     - checks User.set_password / check_password works (plaintext not stored)
     - checks landing page still works via test client GET / == 200 with all feature text
     - deletes file after it passes

6. **Best-effort `flask db` operations (only if MySQL reachable / configured):**
   - If the user already has `.env` with working MySQL creds:
     - Try `flask db init` (only if `migrations/` doesn't exist)
     - Try `flask db migrate -m "Initial database models"`
     - Try `flask db upgrade`
     - Try `python seed_data.py`
   - If any of these fail because MySQL isn't running / .env not filled in → **document** the exact commands for the user to run manually in Phase 2 final summary and STOP. Do NOT create a MySQL database or modify user's MySQL instance automatically.

7. **Final checks:**
   - Lint / type diagnostics via GetDiagnostics (must be 0).
   - Landing page smoke test (same as Phase 1, 17 checks).

---

## Dependencies and Considerations

- **Python 3.10+**: current venv runs 3.11.9 (verified).
- **Flask-SQLAlchemy 3.1.1** + **SQLAlchemy 2.0.35** — use `db.Integer`, `db.String`, `db.Text`, `db.DateTime(timezone=True)`, `db.ForeignKey`, `db.Index`, `UniqueConstraint` inside `__table_args__`. Use MRO `db.Model`. No legacy `declarative_base`.
- **Flask-Migrate 4.0.7** (Alembic under) — `flask db` CLI works via `FLASK_APP=run.py` (Flask auto-discovers `app = create_app()` in run.py when using `FLASK_APP`). We'll make sure `create_app()` is callable in Flask-CLI context even without SocketIO.
- **Flask-Login 0.6.3**: User model uses `UserMixin` (4 methods: `is_authenticated`, `is_active`, `is_anonymous`, `get_id`) — only `is_active` maps to User.is_active field. The actual `login_manager = LoginManager()` init is Phase 3 (auth pages), but model must be ready.
- **Password hashing**: `werkzeug.security.generate_password_hash(method='pbkdf2:sha256')` — no scrypt/bcrypt extra deps required, already in Werkzeug.
- **Timezone timestamps**: MySQL DATETIME ignores TZ info from driver; we still set `timezone=True` for SQLAlchemy 2.0 correctness and note in docs that the server runs on local/UTC TBD.
- **Circular imports avoided by using `from __future__ import annotations` (PEP 563)** in every model file + string FK targets + back_populates string names + importing sub-models inside `app/models/__init__.py` (bottom of file, after all module-level code).
- **Seed script must be idempotent**. If `Role` with name 'Admin' already exists → do nothing. Same for Skill by unique name. Safe to re-run.

---

## Validation

1. **Syntax + IDE diagnostics**: `GetDiagnostics` returns `[]` after all changes.
2. **Programmatic DB test pass** (in-memory SQLite — no MySQL required):
   - All 12 models register in metadata → 12 `__tablename__` present
   - Relationships back-populate bidirectionally
   - Unique constraints correctly raise IntegrityError on conflict
   - Password hashing round trips (verification succeeds on correct pw, fails on wrong)
   - FK integrity: cannot create JobSkill with invalid skill_id → error
   - Flask app still starts (create_app no exception)
3. **Landing page smoke test (Phase 1 preservation)**:
   - `GET /` HTTP 200
   - All 11 needles (SmartHire AI, subtitle, 2 CTAs, 4 feature titles, etc.) still in HTML
   - CSS + JS statics 200
4. **MySQL steps (user manual)**:
   - Document exact commands in final response + explain they're manual if local MySQL wasn't configured during our automation.

---

## Risks and Handling

| Risk | Handling |
|---|---|
| MySQL not installed / not running / wrong creds in .env | All programmatic Phase 2 verification runs against SQLite TestingConfig — we prove models correct regardless. Provide manual MySQL setup commands user runs at their own pace. |
| Flask-Login version conflict with current Flask 3.0.3 | Pin Flask-Login==0.6.3 (tested with Flask 3.x). |
| Circular imports in 12-model package | Enforce `from __future__ import annotations`, string FKs, import order in `__init__`. Test with `from app import models` inside app context. |
| `flask db init` fails because `migrations/` already exists later | Script only runs when dir missing; tell user to delete it to regenerate. |
| Alembic autogenerate can't detect String-check-constraints for enums (we use plain strings anyway) | We don't use native ENUMs — autogenerate works fine for columns/constraints/indexes. |
| `werkzeug.security.generate_password_hash` deprecated method warning | Use `scrypt` if available, fallback `pbkdf2:sha256` — both methods supported in Werkzeug 3.0.4; wrap in `User.set_password` so internals isolated. |
| Phase 1 landing page breaks | Run Phase 1 smoke test; any regression → revert affected template/static immediately. |
| User forgets to create MySQL DB before `flask db upgrade` | Provide explicit Step 1 `CREATE DATABASE smarthire_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;` command in setup guide. |
