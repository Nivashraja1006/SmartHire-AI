# AI System

SmartHire uses local, explainable rules and classical matching. Candidate scores use the existing weighted components: skills, experience, semantic relevance, projects, education, and certifications.

Phase 11 adds:

- `hiring_insights.py`: database-derived supply, gap, and recommendation insights.
- `job_quality_analyzer.py`: deterministic job-description quality checks.
- `resume_quality_analyzer.py`: structural resume checks without protected attributes.
- `ai_audit_service.py`: operation, status, algorithm, version, duration, and error metadata.

The engine version is configured with `AI_ENGINE_VERSION`. No external AI provider is required. Insights never mutate jobs, scores, applications, or interviews.
