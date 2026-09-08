# AI Algorithms

## Skill Matching
Required skills are compared with candidate profile and parsed resume skills. Matches, related/partial matches, and missing skills are retained as evidence.

## Semantic Similarity
The default semantic method is scikit-learn TF-IDF with word and bigram features followed by cosine similarity. An optional locally installed Sentence Transformer can be enabled through environment variables; it is never downloaded automatically.

## Component Matching
Experience compares candidate years with job bounds. Education, certifications, and projects use job-relevant text evidence. No protected attribute is used.

## Overall Score
The current implementation uses:

- Skill: 40%
- Experience: 20%
- Semantic: 15%
- Projects: 10%
- Education: 10%
- Certification: 5%

The score trace uses these same values from the scoring engine and reports each weighted contribution.

## Recommendation Tiers
90-100 Excellent Match; 75-89 Strong Match; 60-74 Good Match; 40-59 Moderate Match; 0-39 Low Match.

## Ranking
Ranking reuses persisted scores, considers mandatory skill coverage, then component scores and application timing for deterministic tie-breaking. Recruiters remain responsible for the final hiring decision.
