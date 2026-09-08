# Viva Questions and Answers

1. **Why this project?** Recruitment screening is repetitive and benefits from explainable, job-relevant automation.
2. **What problem does it solve?** It organizes requirements, resumes, matching, ranking, interviews, and analytics in one workflow.
3. **Why Flask?** It is lightweight, modular through blueprints, and fits a maintainable final-year project.
4. **Why MySQL?** It provides relational integrity for users, jobs, applications, scores, and interviews.
5. **How does parsing work?** Validated PDF, DOCX, or TXT text is processed with local regex and section rules.
6. **How are skills extracted?** Text is matched against the seeded skill dictionary and normalized aliases.
7. **How does matching work?** Independent skill, experience, education, certification, project, and semantic matchers produce components.
8. **Why TF-IDF?** It is local, fast, interpretable, and suitable for document similarity without paid APIs.
9. **What is cosine similarity?** It measures the angle similarity between TF-IDF vectors.
10. **How is the final score calculated?** Components are multiplied by configured weights totaling 100%.
11. **Why skill has the highest weight?** Required skills are the most direct evidence of role fit in this project.
12. **How does ranking work?** Persisted scores are ordered with mandatory coverage and deterministic tie-breakers.
13. **How is hallucination prevented?** Copilot uses rule-based intents and database queries instead of generative claims.
14. **Is the system autonomous?** No. It is decision support; recruiters make final decisions.
15. **How is explainability implemented?** Matched, partial, missing, and component evidence are persisted and displayed.
16. **How are missing skills handled?** They are retained as explicit weaknesses and used in skill-gap analytics.
17. **How is privacy protected?** RBAC, ownership queries, secure sessions, CSRF, and limited audit metadata are used.
18. **How does RBAC work?** Decorators compare the authenticated user's role before protected views run.
19. **How do realtime notifications work?** Domain routes emit events to authenticated recruiter Socket.IO rooms.
20. **Why Flask-SocketIO?** It integrates local realtime events with the existing Flask application.
21. **How is interview conflict detected?** New intervals are compared with overlapping recruiter and candidate intervals.
22. **How are analytics calculated?** SQLAlchemy aggregates applications, scores, jobs, skills, and interviews.
23. **How does Copilot work without paid APIs?** Intent detection maps questions to scoped local query functions.
24. **How are parser failures handled?** Resume records store Failed status and an error message without crashing the server.
25. **What are limitations?** Local parsing depends on formatting, skill dictionaries need maintenance, and scores require human review.
26. **What is SQLAlchemy?** An ORM and SQL toolkit used to map Python models to relational tables.
27. **What is an API?** A controlled HTTP interface used by the browser and integrations to exchange JSON.
28. **What is CSRF?** A cross-site request attack mitigated here with Flask-WTF tokens.
29. **What is IDOR?** Unauthorized object access; ownership filters prevent it on recruiter resources.
30. **Why UUID upload names?** They prevent filename collisions and reduce path manipulation risk.
31. **What is a Socket.IO room?** A server-side group used to target events to one recruiter or job.
32. **Why persist CandidateScore?** It supports reproducibility, analytics, ranking reuse, and auditability.
33. **What is a funnel?** A count of candidates progressing from application through selection.
34. **What does the admin view provide?** System-wide metrics, activity, AI audits, and runtime health.
35. **What is fairness in this system?** Restricting decision signals to job-relevant information and preserving human oversight.
36. **How are sessions protected?** HttpOnly/SameSite cookies, strong session protection, and secure production cookies.
37. **How are uploads checked?** Extension, size, generated path, and PDF/DOCX signatures are checked.
38. **What is the score trace?** A breakdown of each component's actual weighted contribution.
39. **Why use migrations?** They version schema changes and allow reproducible database setup.
40. **What is the future scope?** Multilingual parsing, richer local models, enterprise integrations, and validated learning datasets.
