# Testing

Run all tests with:

```powershell
venv\Scripts\python.exe -m unittest discover -s tests -v
```

The suite covers authentication, RBAC, matching, ranking, notifications, Socket.IO, Copilot, analytics, interviews, exports, quality analyzers, CSRF rejection, protected routes, and invalid upload behavior.

Use `flask --app run.py db upgrade` against a running MySQL instance to validate migrations. `--sql` generates migration SQL without requiring a database connection.
