# Module Reference

| Module | Purpose | Input | Processing | Output |
|---|---|---|---|---|
| Authentication | Sign in and registration | Credentials | Password hash verification and session creation | Authenticated session |
| Job Management | Maintain hiring briefs | Job fields/JD | Validation, skill association, local JD analysis | Job and JobSkill records |
| JD Analyzer | Extract requirements | Job text | Regex and seeded skill matching | Skills, experience, education, responsibilities |
| Candidate Management | Maintain profiles | Candidate fields/resumes | Ownership checks and persistence | Candidate and Resume records |
| Resume Parser | Extract resume fields | PDF/DOCX/TXT text | Local regex sections and skill matching | Parsed JSON |
| Skill Extraction | Normalize skills | Text/profile | Seeded dictionary and aliases | CandidateSkill/JobSkill data |
| Matching Engine | Compare candidate to job | Profile, resume, requirements | Component matchers plus semantic similarity | CandidateScore |
| Ranking Engine | Order candidates | Scores and applications | Threshold, coverage, score and tie-breakers | Ranked list |
| Explainable AI | Explain results | Match result | Evidence and weaknesses | Human-readable explanation and trace |
| Analytics | Measure funnel | Applications, scores, interviews | SQL aggregation | KPIs, charts, reports |
| Interview Management | Schedule conversations | Application/date/time | Ownership and overlap validation | Interview, notification, activity |
| Real-Time Notifications | Live updates | Domain events | Socket.IO recruiter rooms | Browser events/toasts |
| AI Recruiter Copilot | Read-only assistant | Recruiter question | Intent detection and scoped query | Text plus structured data |
| Admin Management | System oversight | Platform records | Role-protected aggregate views | Admin metrics and health |
