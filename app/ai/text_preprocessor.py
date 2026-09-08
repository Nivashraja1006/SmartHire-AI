from __future__ import annotations

import re


def clean_text(text: str) -> str:
    text = (text or '').replace('\x00', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def normalize_text(text: str) -> str:
    return clean_text(text).casefold()


def remove_noise(text: str) -> str:
    return clean_text(re.sub(r'[^\w\s+#.\-/]', ' ', text, flags=re.UNICODE))


def remove_duplicate_whitespace(text: str) -> str:
    return re.sub(r'\s+', ' ', text or '').strip()


def normalize_skill_terms(text: str, aliases=None) -> str:
    normalized = normalize_text(text)
    for alias, canonical in (aliases or {}).items():
        normalized = re.sub(r'(?<!\w)' + re.escape(alias.casefold()) + r'(?!\w)', canonical.casefold(), normalized)
    return normalized