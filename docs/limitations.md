# Limitations

- Local regex and rule-based NLP are less flexible than large proprietary language models.
- Resume formatting can reduce extraction quality.
- The seeded skill dictionary requires maintenance as technology vocabulary changes.
- TF-IDF may miss domain-specific synonyms and deeper context.
- Candidate scores are decision-support signals, not hiring truth.
- AI quality checks are structural heuristics, not professional resume or legal evaluations.
- The local rate limiter is process-local and does not coordinate across multiple workers.
- Live MySQL and browser/mobile verification must be performed in an environment where those services are available.
- Real-world hiring requires organizational policy, legal review, accessibility review, and human judgment.
