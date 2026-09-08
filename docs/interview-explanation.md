# Interview Explanation

## 60 seconds
I built SmartHire AI, a local Flask recruitment platform. A recruiter creates a job, uploads a description, and the system extracts requirements. Resumes are validated, parsed, and matched using skills, experience, education, projects, certifications, and TF-IDF semantic relevance. The resulting scores are explainable and ranked. The platform also handles shortlisting, interviews, realtime notifications, analytics, and a rule-based Copilot.

## 2 minutes: AI
The system does not call a paid LLM. It uses seeded skill dictionaries, regex parsing, deterministic component matchers, and TF-IDF/cosine similarity. The scoring engine combines skill 40%, experience 20%, semantic 15%, projects 10%, education 10%, and certifications 5%. Each result stores matched, partial, missing, and explanation evidence. Hiring insights summarize database records but never change recruiter decisions.

## 5 minutes: architecture
The browser renders Flask templates and uses JavaScript for Chart.js and Socket.IO. Blueprints handle authentication, recruiter, candidate, admin, analytics, interviews, notifications, and Copilot routes. Decorators enforce roles, while ownership queries scope recruiter and candidate data. Services hold analytics and audit logic. AI modules parse and compare text. SQLAlchemy maps the relational model to MySQL, with in-memory SQLite used in tests. Flask-SocketIO emits authenticated recruiter-room events for score, shortlist, interview, activity, and notification updates. Alembic migrations version schema changes. Security includes password hashing, CSRF, secure cookies, upload limits/signature checks, safe errors, and human review of all AI outputs.
