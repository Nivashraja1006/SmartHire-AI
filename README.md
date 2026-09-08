# SmartHire AI

SmartHire AI is a Flask recruitment intelligence project built with open-source local processing.

## Phase 6

Phase 6 adds explainable candidate-to-job matching:

- Skill extraction and alias normalization
- Exact, alias, related, and missing skill matching
- Experience and education comparison
- Certification and project relevance signals
- TF-IDF plus cosine similarity semantic matching
- Optional local Sentence Transformers support
- Configurable weighted scoring
- Rule-based explanations
- Recruiter-only matching API and UI

No paid AI API is required.

## Matching pipeline

```text
Resume + Candidate Profile
        |
Text preprocessing
        |
Skill extraction and normalization
        |
Skill matching
        |
Experience matching
        |
Education matching
        |
Certification matching
        |
Project relevance
        |
TF-IDF semantic similarity
        |
Weighted scoring
        |
Explainable result
```

Default formula:

```text
Skill          40%
Experience     20%
Semantic       15%
Projects       10%
Education      10%
Certification   5%
```

TF-IDF and cosine similarity are the default semantic method. To use an already-installed local Sentence Transformers model, set `USE_LOCAL_SENTENCE_TRANSFORMER=true` and optionally `LOCAL_SENTENCE_MODEL`. Models are never downloaded automatically by the application. If the package or model is unavailable, TF-IDF remains active.

## Phase 6 routes

- `GET /recruiter/jobs/<job_id>/matches`
- `GET /recruiter/jobs/<job_id>/candidates/<candidate_id>/match`
- `POST /recruiter/api/recruiter/jobs/<job_id>/match/<candidate_id>`

All matching routes require a logged-in Recruiter who owns the job.

## Run

```powershell
venv\\Scripts\\python.exe -m flask --app run.py db upgrade
venv\\Scripts\\python.exe demo_phase6.py
venv\\Scripts\\python.exe run.py
```

Run tests:

```powershell
venv\\Scripts\\python.exe -m unittest tests.test_auth tests.test_phase6 -v
```

The sample seed creates five fictional candidates and three demo jobs. Matching does not rank a candidate pool; it only calculates a single candidate-to-job match as required for Phase 6.

## Phase 7

Phase 7 adds score-based AI candidate ranking for a recruiter-owned job. The ranking engine reuses Phase 6 `CandidateScore` records, recalculating only when a score is missing, stale, or explicitly requested.

```text
Candidate -> Phase 6 matching -> CandidateScore -> ranking engine
          -> mandatory coverage -> threshold -> tie-breaker -> dashboard
```

Ranking uses the Phase 6 weights: skill 40%, experience 20%, semantic 15%, projects 10%, education 10%, certification 5%. Ties use mandatory skill coverage, skill score, experience score, semantic score, project relevance, and earliest application time. Protected attributes are never used.

Routes:

- `GET /recruiter/jobs/<job_id>/ranking`
- `GET /api/recruiter/jobs/<job_id>/ranking`
- `POST /api/recruiter/jobs/<job_id>/ranking/recalculate`
- `GET /api/recruiter/jobs/<job_id>/ranking/candidate/<candidate_id>`
- `POST|DELETE /api/recruiter/jobs/<job_id>/shortlist/<candidate_id>`
- `POST /api/recruiter/jobs/<job_id>/compare`

Seed and calculate demo rankings:

```powershell
venv\\Scripts\\python.exe demo_phase7.py
```

Shortlisting is stored on the existing `Application.is_shortlisted` field and does not affect AI scores. Ranking does not implement interviews, analytics, notifications, or later-phase features.

## Phase 8

Phase 8 adds local real-time recruiter updates using the existing single Flask-SocketIO instance:

```text
Browser <-> Socket.IO <-> Flask-SocketIO <-> realtime.events <-> services/database
```

Rooms are authenticated server-side as `recruiter_<user_id>` and `job_<job_id>`. Client-supplied recruiter IDs are ignored; job rooms require ownership. Events include candidate creation, resume processing, score updates, ranking lifecycle, shortlist changes, job status changes, activity creation, and notification creation.

Notifications are persisted in `notifications` and expose:

- `GET /api/notifications`
- `POST /api/notifications/<id>/read`
- `POST /api/notifications/read-all`
- `GET /api/recruiter/dashboard`

The recruiter UI includes a notification bell, unread count, live activity feed, realtime dashboard metrics, connection fallback state, and accessible toast notifications. If Socket.IO is unavailable, the normal HTTP pages and lightweight dashboard refresh still work.

Run the Phase 8 migration and tests:

```powershell
venv\\Scripts\\python.exe -m flask --app run.py db upgrade
venv\\Scripts\\python.exe -m unittest tests.test_phase8 tests.test_phase7 tests.test_phase6 tests.test_auth -v
venv\\Scripts\\python.exe run.py
```

## Phase 9

SmartHire Copilot is a local, rule-based recruitment assistant. It uses intent detection plus targeted SQLAlchemy queries over the existing jobs, candidates, applications, scores, skills, and shortlist data. It does not use an LLM or paid API and never replaces the Phase 6 matching or Phase 7 ranking engines.

Architecture:

```text
Recruiter message
        |
Intent detection
        |
Recruiter-owned context
        |
Safe query engine
        |
Structured response generator
        |
Copilot chat UI
```

Supported intents include top candidates, candidate summaries, comparisons, skill gaps, match explanations, job summaries, candidate search, shortlist recommendations, statistics, help, and fairness-protected requests.

Routes:

- `GET /recruiter/copilot`
- `POST /api/recruiter/copilot/chat`
- `GET /api/recruiter/copilot/conversations`
- `GET /api/recruiter/copilot/conversations/<conversation_id>`

Copilot responses contain both concise text and structured data for candidate cards, score badges, and skill-gap views. Conversation history is stored in `copilot_conversations` and `copilot_messages`, scoped to the authenticated recruiter. Socket.IO events `copilot_request_started`, `copilot_response_ready`, and `copilot_error` support live UI state.

The Copilot refuses requests based on protected or irrelevant attributes and states that it can only use job-relevant qualifications. Missing data produces an explicit insufficient-information response rather than a guess.

## Phase 10

Phase 10 adds database-backed recruitment analytics, interview scheduling, and admin intelligence without paid services or external calendar integrations.

Analytics architecture:

```text
Recruitment tables -> app.services.analytics_service -> scoped JSON APIs -> Chart.js dashboards / CSV reports
```

Recruiters can use:

- `GET /recruiter/analytics` for KPI cards, funnel, score distribution, trends, job performance, and skill gaps
- `GET /recruiter/interviews` and `GET /recruiter/interviews/create` for scheduling and status management
- `/api/recruiter/analytics/overview`, `/job/<job_id>`, `/skills/<job_id>`, `/funnel/<job_id>`, `/interviews`, and `/trends`
- `/api/recruiter/analytics/export/summary`, `jobs`, `ranking`, `skills`, or `interviews` for CSV reports

Funnel and conversion values are calculated from `Application`, `CandidateScore`, and `Interview`: shortlist rate, interview rate, and selection rate are guarded against division by zero. Skill-gap percentages use required `JobSkill` records and candidate-owned `CandidateSkill` records. Date ranges support 7, 30, 90 days, or validated custom `start_date` and `end_date` values.

Interviews reuse the existing model and now store duration, meeting link, location, and creator. Scheduling validates recruiter ownership, future date/time, duration, and recruiter/candidate overlap. Create, reschedule, cancel, complete, and no-show actions create notifications, activity records, and Socket.IO events. Past interviews remain scheduled until a recruiter records the outcome.

Admins use `/admin/dashboard` or `/admin/analytics` and the `/api/admin/analytics/*` endpoints for system-wide users, jobs, applications, resumes, interviews, and recent activity. Recruiter data remains filtered by owned jobs; candidate access remains governed by existing candidate routes.

Phase 10 extends Copilot intents with interview statistics, analytics summaries, job performance, and aggregate skill-gap questions. All calculations are local SQLAlchemy queries and no paid AI, messaging, calendar, or analytics provider is required.

Run the complete test suite:

```powershell
venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Phase 11: Production Hardening

Phase 11 adds local explainable hiring insights, job and resume quality analyzers, score traces, AI operation auditing, CSRF protection, safer production configuration, upload signature validation, structured API errors, and a live admin system-health page.

AI insights are decision support only. They use stored job-relevant skills, experience, education, projects, certifications, applications, and candidate scores. They never infer or score protected attributes and never change requirements, rankings, shortlists, or interviews automatically.

Production setup requires an explicit `SECRET_KEY`, `DATABASE_URL` or `MYSQL_PASSWORD`, and a specific `CORS_ORIGINS` value. Configure `AI_ENGINE_VERSION` for reproducible audit records. Uploaded PDF, DOCX, and TXT files are UUID-named, size-limited, signature-checked where applicable, and never executed.

Phase 11 documentation is in `docs/`: architecture, AI system, database, API, security, testing, and user guide references.

## Phase 12: Presentation and Demo Readiness

Phase 12 adds a confirmation-gated fictional demo reset and final-year-project documentation. Reset demo data with:

```powershell
venv\Scripts\python.exe scripts\reset_demo.py --yes
```

The reset command refuses `FLASK_ENV=production`, preserves the schema, rebuilds five jobs and fifteen candidates, calculates real matching/ranking data, creates shortlists, interviews, and activity records, and prints the demo recruiter credentials. The password can be overridden with `DEMO_RECRUITER_PASSWORD`; never use real personal data.

Presentation and project documents are in `docs/`, including `project-architecture.md`, `project-abstract.md`, `modules.md`, `ai-algorithms.md`, `fairness.md`, `test-report.md`, `viva-questions.md`, `demo-script.md`, `presentation-content.md`, `resume-description.md`, `interview-explanation.md`, `limitations.md`, `future-scope.md`, and `screenshots.md`.

### Project structure

```text
ranking/
├── app/             # Flask blueprints, models, services, AI, templates, static assets
├── migrations/      # Alembic schema history
├── scripts/         # Safe development/demo utilities
├── tests/           # Automated unit and integration tests
├── docs/            # Architecture, viva, presentation, and user documentation
├── config.py
├── requirements.txt
├── run.py
└── .env.example
```

### Verified status

The latest automated run passes 20 tests across authentication, RBAC, matching, ranking, realtime notifications, Copilot, analytics, interviews, exports, CSRF, upload validation, and AI quality. Live MySQL migration execution and browser/mobile screenshots remain environment-dependent checks.
