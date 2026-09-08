# API Overview

All protected endpoints require a logged-in role. Recruiter endpoints scope records to jobs owned by the current recruiter. State-changing browser requests use CSRF tokens.

| Method | URL | Purpose |
|---|---|---|
| GET | `/api/recruiter/analytics/overview` | Recruiter KPIs |
| GET | `/api/recruiter/analytics/job/<job_id>` | Job performance |
| GET | `/api/recruiter/analytics/funnel/<job_id>` | Recruitment funnel |
| GET | `/api/recruiter/analytics/skills/<job_id>` | Skill gaps |
| GET | `/api/recruiter/insights/<job_id>` | Hiring insights |
| GET | `/api/recruiter/jobs/<job_id>/quality` | Job quality |
| GET | `/api/recruiter/analytics/export/<report>` | CSV report |
| POST | `/recruiter/interviews/create` | Schedule interview |
| POST | `/api/recruiter/interviews/<id>/<action>` | Update interview status |
| GET | `/api/admin/analytics/overview` | Admin system metrics |
| GET | `/admin/system-health` | Runtime health checks |

Errors use JSON for API paths with `success: false` and a safe error message. Unauthorized resources return 403/404 without leaking ownership details.
