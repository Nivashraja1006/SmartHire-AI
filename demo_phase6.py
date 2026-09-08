"""Seed five fictional Phase 6 candidates, resumes, and sample jobs."""
from __future__ import annotations

import os

from app import create_app, db
from app.ai.resume_parser import parse_resume
from app.models import Candidate, CandidateSkill, Job, JobSkill, Resume, Role, Skill, User
from seed_data import seed_roles, seed_skills


CANDIDATES = [
    ('Ava Menon', 'ava.demo@example.com', 4, 'Python Flask MySQL Git. B.Tech Computer Science. Projects: Hiring API; certified AWS.'),
    ('Noah Williams', 'noah.demo@example.com', 2, 'JavaScript React Node.js MongoDB Git. B.Sc Computer Science. Projects: Commerce frontend.'),
    ('Mia Chen', 'mia.demo@example.com', 5, 'Python Pandas NumPy Scikit-learn SQL. M.Sc Data Science. Projects: Sales forecasting.'),
    ('Liam Patel', 'liam.demo@example.com', 6, 'Java Spring Boot PostgreSQL Docker AWS. B.Tech Information Technology. Projects: Payment platform.'),
    ('Zoe Garcia', 'zoe.demo@example.com', 1, 'Python OpenCV Flask. BCA. Projects: Crop disease detection.'),
]
JOBS = [
    ('Python Developer Demo', 'Python Django REST API MySQL Git. B.Tech', ['Python', 'Django', 'MySQL', 'Git']),
    ('Data Analyst Demo', 'Python Pandas NumPy Scikit-learn. M.Sc', ['Python', 'Pandas', 'NumPy', 'Scikit-learn']),
    ('Backend Platform Demo', 'Java Spring Boot PostgreSQL Docker AWS. B.Tech', ['Java', 'Spring Boot', 'PostgreSQL', 'Docker']),
]


def main():
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    with app.app_context():
        seed_roles()
        seed_skills()
        recruiter_role = Role.query.filter_by(name=Role.RECRUITER).first()
        recruiter = User.query.filter_by(email='phase6.demo.recruiter@example.com').first()
        if not recruiter:
            recruiter = User(full_name='Phase 6 Demo Recruiter', email='phase6.demo.recruiter@example.com', role=recruiter_role)
            recruiter.set_password(os.environ.get('DEMO_RECRUITER_PASSWORD', 'phase6-demo-password'))
            db.session.add(recruiter)
            db.session.flush()
        skill_map = {skill.name.casefold(): skill for skill in Skill.query.all()}
        for name, email, years, text in CANDIDATES:
            candidate = Candidate.query.filter_by(email=email).first()
            if candidate:
                continue
            candidate = Candidate(full_name=name, email=email, total_experience=years, profile_summary='Fictional Phase 6 demonstration candidate.')
            db.session.add(candidate)
            db.session.flush()
            parsed = parse_resume(text, Skill.query.all())
            resume = Resume(candidate=candidate, original_filename=f'{name.lower().replace(" ", "_")}.txt', stored_filename=f'demo_{candidate.id}.txt', file_path='uploads/resumes/demo.txt', file_type='txt', extracted_text=text, parsed_data=parsed, processing_status=Resume.STATUS_COMPLETED)
            db.session.add(resume)
            for item in parsed['skills']:
                skill = skill_map.get(item['name'].casefold())
                if skill:
                    db.session.add(CandidateSkill(candidate=candidate, skill=skill, source=CandidateSkill.SRC_RESUME))
        db.session.flush()
        for title, description, names in JOBS:
            if Job.query.filter_by(title=title, recruiter_id=recruiter.id).first():
                continue
            job = Job(recruiter_id=recruiter.id, title=title, company_name='SmartHire Demo Labs', description=description, min_experience=1, max_experience=7, status=Job.STATUS_ACTIVE)
            db.session.add(job)
            db.session.flush()
            for name in names:
                skill = skill_map.get(name.casefold())
                if skill:
                    db.session.add(JobSkill(job=job, skill=skill, importance=JobSkill.IMPORTANCE_MANDATORY))
        db.session.commit()
        print('Phase 6 demo data seeded: 5 candidates and 3 jobs.')


if __name__ == '__main__':
    main()
