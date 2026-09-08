from __future__ import annotations

import os
from functools import lru_cache

from app.ai.text_preprocessor import clean_text


def _tfidf_similarity(left, right):
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        matrix = TfidfVectorizer(ngram_range=(1, 2), stop_words='english').fit_transform([left, right])
        return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100)
    except Exception:
        left_words, right_words = set(left.casefold().split()), set(right.casefold().split())
        return 100 * len(left_words & right_words) / (len(left_words | right_words) or 1)


def semantic_similarity(job_text, candidate_text):
    job_text, candidate_text = clean_text(job_text), clean_text(candidate_text)
    if not job_text or not candidate_text:
        return 0.0
    if os.environ.get('USE_LOCAL_SENTENCE_TRANSFORMER', '').lower() in {'1', 'true', 'yes'}:
        try:
            from sentence_transformers import SentenceTransformer
            from sklearn.metrics.pairwise import cosine_similarity
            model = _sentence_model()
            vectors = model.encode([job_text, candidate_text])
            return round(float(cosine_similarity([vectors[0]], [vectors[1]])[0][0] * 100), 1)
        except Exception:
            pass
    return round(_tfidf_similarity(job_text, candidate_text), 1)


@lru_cache(maxsize=1)
def _sentence_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(os.environ.get('LOCAL_SENTENCE_MODEL', 'all-MiniLM-L6-v2'))