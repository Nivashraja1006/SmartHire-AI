# Security

- Passwords use Werkzeug secure hashing.
- Production requires an explicit `SECRET_KEY` and database password/URL.
- Sessions are HttpOnly and SameSite Lax; Secure is enabled in production.
- Flask-WTF CSRF protection covers state-changing forms and same-origin AJAX through the shared token wrapper.
- Uploads allow only PDF, DOCX, or TXT, enforce a 10 MB limit, generate UUID filenames, and validate PDF/DOCX signatures before parsing.
- Recruiter ownership and role checks are server-side.
- Protected attributes are not used by matching, ranking, analytics, or insights.
- Error responses do not expose stack traces, paths, credentials, or uploaded content.

Set `CORS_ORIGINS` explicitly for deployed origins. Never commit `.env`, credentials, or upload contents.
