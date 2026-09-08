"""Enhanced resume parser with NLP and seeded skill matching."""
from __future__ import annotations

import re
import logging
from typing import Optional, List, Dict, Any

import spacy
from spacy.matcher import PhraseMatcher

logger = logging.getLogger(__name__)

# Try to load spaCy model, fall back gracefully
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    logger.warning('spaCy model not found. Download with: python -m spacy download en_core_web_sm')
    nlp = None


def _extract_section(text: str, section_names: List[str]) -> str:
    """Extract a section from resume text by section headers."""
    pattern = r'(?is)(?:^|\b(?:' + '|'.join(section_names) + r')\s*:?\s*)(.*?)(?=\b(?:education|experience|work experience|projects?|certifications?|skills?)\s*:|$)'
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ''


def _extract_contact_info(text: str) -> Dict[str, str]:
    """Extract email and phone from text."""
    email = re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text)
    phone = re.search(r'(?:\+?\d[\d\s().-]{7,}\d)', text)
    return {
        'email': email.group(0) if email else '',
        'phone': phone.group(0).strip() if phone else '',
    }


def _extract_name(text: str) -> str:
    """Extract candidate name using spaCy NER or fallback to first few words."""
    if nlp is None:
        # Fallback: take first 3 words
        words = text.split()[:3]
        return ' '.join(words) if words else ''
    
    doc = nlp(text[:500])  # Process only first 500 chars for speed
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            return ent.text
    
    # Fallback to first words
    words = text.split()[:3]
    return ' '.join(words) if words else ''


def _extract_experience_years(text: str) -> Optional[float]:
    """Extract total years of experience."""
    patterns = [
        r'(\d+)\+?\s+years?\s+(?:of\s+)?experience',
        r'(?:experience|exp).*?(\d+)\+?\s+years?',
        r'(\d+)\+?\s+(?:yrs?|years?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, IndexError):
                continue
    return None


def _extract_experience(text: str) -> List[Dict[str, str]]:
    """Extract work experience entries."""
    experience = []
    
    # Pattern 1: "Title at Company (duration)"
    pattern1 = r'(?i)([A-Za-z][\w .&-]{1,50})\s+at\s+([A-Za-z][\w .&-]{1,50})(?:\s*\(([^)]*)\))?'
    for match in re.finditer(pattern1, text):
        experience.append({
            'title': match.group(1).strip(),
            'company': match.group(2).strip(),
            'duration': (match.group(3) or '').strip(),
        })
    
    # Pattern 2: "Company - Title (duration)"
    pattern2 = r'(?i)([A-Za-z][\w .&-]{1,50})\s*-\s*([A-Za-z][\w .&-]{1,50})(?:\s*\(([^)]*)\))?'
    for match in re.finditer(pattern2, text):
        if len(experience) < 10:
            experience.append({
                'title': match.group(2).strip(),
                'company': match.group(1).strip(),
                'duration': (match.group(3) or '').strip(),
            })
    
    return experience[:10]


def _extract_education(text: str) -> List[Dict[str, str]]:
    """Extract education entries."""
    education = []
    
    degrees = [
        r"bachelor'?s?",
        r'b\.?s\.?',
        r"master'?s?",
        r'm\.?s\.?',
        r'ph\.?d\.?',
        r'b\.?tech\.?',
        r'm\.?tech\.?',
        r'mba',
        r'associate',
        r'diploma',
    ]
    
    pattern = r'(?i)\b((?:' + '|'.join(degrees) + r')[^,.;|]{0,100})'
    
    for match in re.finditer(pattern, text):
        if len(education) < 8:
            education.append({'degree': match.group(1).strip()})
    
    return education


def _extract_certifications(text: str) -> List[Dict[str, str]]:
    """Extract certifications."""
    certifications = re.findall(
        r'(?i)(?:certified|certification|certificate|cert)\s*[:\-]?\s*([A-Za-z0-9 .+#\-,()]{3,100})',
        text
    )
    return [{'name': cert.strip()} for cert in certifications[:10]]


def _extract_projects(text: str) -> List[Dict[str, str]]:
    """Extract projects from resume."""
    projects = []
    project_text = _extract_section(text, ['projects?', 'selected projects?', 'portfolio'])
    
    if project_text:
        # Split by common delimiters and create project entries
        items = re.split(r'\s*[;|\n]\s*', project_text)
        for item in items:
            cleaned = item.strip()
            if cleaned and len(cleaned) > 3:
                # Try to extract description if available
                parts = re.split(r'\s*[-:]\s*', cleaned, maxsplit=1)
                projects.append({
                    'name': parts[0],
                    'description': parts[1] if len(parts) > 1 else '',
                })
    
    return projects[:10]


def _match_skills_with_database(text: str, skills=None) -> List[Dict[str, Any]]:
    """Match skills found in text with database skills."""
    detected_skills = []
    
    if not skills:
        return detected_skills
    
    text_lower = text.lower()
    
    for skill in skills:
        skill_name_lower = skill.name.lower()
        
        # Exact match (word boundary)
        if re.search(r'(?<!\w)' + re.escape(skill_name_lower) + r'(?!\w)', text_lower):
            detected_skills.append({
                'name': skill.name,
                'category': getattr(skill, 'category', ''),
                'proficiency_level': 'Intermediate',
            })
            continue
        
        # Check for common aliases/variations
        if len(skill_name_lower) > 2:
            # Fuzzy match for partial strings
            if skill_name_lower in text_lower:
                if not any(s['name'].lower() == skill_name_lower for s in detected_skills):
                    detected_skills.append({
                        'name': skill.name,
                        'category': getattr(skill, 'category', ''),
                        'proficiency_level': 'Beginner',
                    })
    
    return detected_skills


def parse_resume(text: str, skills=None) -> Dict[str, Any]:
    """
    Parse resume text and extract structured information.
    
    Args:
        text: Raw resume text
        skills: List of Skill objects from database for matching
        
    Returns:
        Dictionary with extracted resume information
    """
    if not text:
        return {
            'full_name': '',
            'email': '',
            'phone': '',
            'skills': [],
            'education': [],
            'experience': [],
            'certifications': [],
            'projects': [],
            'total_experience': None,
        }
    
    # Normalize text
    cleaned = re.sub(r'\s+', ' ', text).strip()
    cleaned_lower = cleaned.lower()
    
    # Extract all components
    contact_info = _extract_contact_info(cleaned)
    name = _extract_name(cleaned)
    years = _extract_experience_years(cleaned)
    experience = _extract_experience(cleaned)
    education = _extract_education(cleaned)
    certifications = _extract_certifications(cleaned)
    projects = _extract_projects(cleaned)
    detected_skills = _match_skills_with_database(cleaned, skills)
    
    return {
        'full_name': name,
        'email': contact_info['email'],
        'phone': contact_info['phone'],
        'skills': detected_skills,
        'education': education,
        'experience': experience,
        'certifications': certifications,
        'projects': projects,
        'total_experience': years,
    }