"""Destructively reset and rebuild fictional SmartHire presentation data.

Usage:
    python scripts/reset_demo.py --yes

This command is development/demo-only and refuses FLASK_ENV=production.
"""
from __future__ import annotations

import argparse
import os
from datetime import date, time, timedelta

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

from app import create_app, db  # noqa: E402
from app.ai.ranking_engine import rank_candidates_for_job  # noqa: E402
from app.ai.resume_parser import parse_resume  # noqa: E402
from app.models import (  # noqa: E402
    ActivityLog, Application, Candidate, CandidateScore, CandidateSkill,
    Interview, Job, JobSkill, Notification, Resume, Role, Skill, User,
)
from seed_data import seed_roles, seed_skills  # noqa: E402


RECRUITER_EMAIL = 'demo.recruiter@smarthire.local'
CANDIDATE_DATA = [
    ('Ava Menon', 'python flask mysql git docker', 5), ('Noah Williams', 'javascript react node.js git', 3),
    ('Mia Chen', 'python pandas numpy scikit-learn', 6), ('Liam Patel', 'java docker aws mysql git', 7),
    ('Zoe Garcia', 'python flask django git', 2), ('Ethan Brooks', 'python django postgresql docker', 5),
    ('Priya Shah', 'python sql git aws', 4), ('Oliver Smith', 'javascript react node.js mongodb', 3),
    ('Sara Khan', 'python pandas power bi mysql', 4), ('Daniel Kim', 'java spring postgresql docker', 6),
    ('Emma Rossi', 'python flask rest api mysql', 3), ('Lucas Brown', 'python django docker aws', 5),
    ('Nora Wilson', 'javascript react html css git', 2), ('Arjun Rao', 'python scikit-learn pandas numpy', 4),
    ('Grace Lee', 'java mysql aws linux', 6),
]
JOB_DATA = [
    ('Python Platform Engineer', 'python flask django mysql docker git', ['Python', 'Flask', 'Docker', 'MySQL']),
    ('Data Intelligence Analyst', 'python pandas numpy scikit-learn mysql', ['Python', 'Pandas', 'Scikit-learn', 'MySQL']),
    ('Frontend Product Engineer', 'javascript react html css git', ['JavaScript', 'React', 'HTML', 'CSS']),
    ('Cloud Backend Engineer', 'python docker aws postgresql rest api', ['Python', 'Docker', 'AWS', 'REST API']),
    ('Java Services Engineer', 'java mysql docker aws git', ['Java', 'MySQL', 'Docker', 'AWS']),
]


def _clear_demo():
    recruiter = User.query.filter_by(email=RECRUITER_EMAIL).first()
    demo_candidates = Candidate.query.filter(Candidate.email.like('%@demo.smarthire.local')).all()
    demo_jobs = Job.query.filter(Job.title.in_([item[0] for item in JOB_DATA])).all()
    job_ids = [job.id for job in demo_jobs]
    candidate_ids = [candidate.id for candidate in demo_candidates]
    applications = Application.query.filter(
        Application.job_id.in_(job_ids) if job_ids else False,
        Application.candidate_id.in_(candidate_ids) if candidate_ids else False,
    ).all()
    application_ids = [application.id for application in applications]
    if application_ids:
        Interview.query.filter(Interview.application_id.in_(application_ids)).delete(synchronize_session=False)
        CandidateScore.query.filter(CandidateScore.application_id.in_(application_ids)).delete(synchronize_session=False)
        Application.query.filter(Application.id.in_(application_ids)).delete(synchronize_session=False)
    for job in demo_jobs:
        db.session.delete(job)
    for candidate in demo_candidates:
        db.session.delete(candidate)
    if recruiter:
        ActivityLog.query.filter_by(user_id=recruiter.id).delete(synchronize_session=False)
        Notification.query.filter_by(user_id=recruiter.id).delete(synchronize_session=False)
        db.session.delete(recruiter)
    db.session.commit()


def _build_demo():
    seed_roles()
    seed_skills()
    recruiter_role = Role.query.filter_by(name=Role.RECRUITER).one()
    recruiter = User(full_name='SmartHire Demo Recruiter', email=RECRUITER_EMAIL, role=recruiter_role)
    recruiter.set_password(os.environ.get('DEMO_RECRUITER_PASSWORD', 'demo-recruiter-password'))
    db.session.add(recruiter)
    db.session.flush()
    skill_map = {skill.name.casefold(): skill for skill in Skill.query.all()}
    candidates = []
    for index, (name, skill_text, years) in enumerate(CANDIDATE_DATA, 1):
        email = f'candidate{index}@demo.smarthire.local'
        candidate = Candidate(full_name=name, email=email, total_experience=years, profile_summary='Fictional SmartHire presentation candidate.')
        db.session.add(candidate)
        db.session.flush()
        parsed = parse_resume(f'{name} {email} +1 555 010 {index:04d}. {skill_text}. {years} years experience. B.Tech Computer Science. Projects: scalable platform.', Skill.query.all())
        db.session.add(Resume(candidate=candidate, original_filename=f'demo_{index}.txt', stored_filename=f'demo_{index}.txt', file_path=f'uploads/resumes/demo_{index}.txt', file_type='txt', extracted_text=skill_text, parsed_data=parsed, processing_status=Resume.STATUS_COMPLETED))
        for skill_name in skill_text.split():
            skill = skill_map.get(skill_name.casefold())
            if skill:
                db.session.add(CandidateSkill(candidate=candidate, skill=skill, source=CandidateSkill.SRC_RESUME))
        candidates.append(candidate)
    jobs = []
    for title, description, required_names in JOB_DATA:
        job = Job(recruiter_id=recruiter.id, title=title, company_name='SmartHire Demo Labs', description=description, min_experience=1, max_experience=8, required_education='B.Tech', status=Job.STATUS_ACTIVE)
        db.session.add(job)
        db.session.flush()
        for skill_name in required_names:
            skill = skill_map.get(skill_name.casefold())
            if skill:
                db.session.add(JobSkill(job=job, skill=skill, importance=JobSkill.IMPORTANCE_MANDATORY))
        jobs.append(job)
    db.session.commit()
    return recruiter, candidates, jobs


def main():
    parser = argparse.ArgumentParser(description='Reset fictional SmartHire demo data.')
    parser.add_argument('--yes', action='store_true', help='Confirm destructive demo reset.')
    args = parser.parse_args()
    environment = os.environ.get('FLASK_ENV', 'development').lower()
    if environment == 'production':
        raise SystemExit('Refusing to reset demo data in production.')
    if not args.yes:
        raise SystemExit('This permanently replaces demo records. Re-run with --yes to confirm.')
    app = create_app(environment)
    with app.app_context():
        _clear_demo()
        recruiter, candidates, jobs = _build_demo()
        for job in jobs:
            rows = rank_candidates_for_job(job.id, force=True)
            for row in rows[:2]:
                application = row['application']
                if application:
                    application.is_shortlisted = True
                    application.status = Application.STATUS_SHORTLISTED
            for offset, row in enumerate(rows[:2]):
                application = row['application']
                if application:
                    db.session.add(Interview(application=application, created_by=recruiter.id, interview_date=date.today() + timedelta(days=offset + 1), interview_time=time(10 + offset, 0), duration_minutes=45, interview_type=Interview.TYPE_ONLINE, meeting_link='https://localhost/demo-interview', status=Interview.STATUS_SCHEDULED, notes='Fictional demo interview.'))
        db.session.add(ActivityLog(user_id=recruiter.id, activity_type='Demo Data Reset', description='Fictional presentation dataset rebuilt.'))
        db.session.commit()
        print(f'Demo reset complete: {len(jobs)} jobs, {len(candidates)} candidates, {Application.query.count()} applications, {Interview.query.count()} interviews.')
        print(f'Recruiter login: {RECRUITER_EMAIL} / {os.environ.get("DEMO_RECRUITER_PASSWORD", "demo-recruiter-password")}')


if __name__ == '__main__':
    main()
