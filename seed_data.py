"""
SmartHire AI — Idempotent seed data script (Phase 2).

Seeds:
  - 3 roles: Admin, Recruiter, Candidate
  - 25+ common technical skills, correctly categorized

Safe to re-run any number of times: existing records are skipped.

Usage:
    python seed_data.py
    # Or against a specific FLASK_ENV:
    FLASK_ENV=development python seed_data.py
"""
from __future__ import annotations

import os
import sys

from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

from app import create_app, db  # noqa: E402
from app.models import Role, Skill  # noqa: E402


ROLES = [
    (Role.ADMIN,
     'Full platform access — users, jobs, candidates, system configuration.'),
    (Role.RECRUITER,
     'Create jobs, upload resumes, review candidates, schedule interviews.'),
    (Role.CANDIDATE,
     'Limited access — view applications and profile only.'),
]

# (skill_name, Skill.CATEGORY_*, optional description)
SKILLS = [
    ('Python', Skill.CAT_PROGRAMMING,
     'Python programming language — general purpose, data science, web.'),
    ('Java', Skill.CAT_PROGRAMMING,
     'Enterprise Java — Spring, JEE, JVM ecosystem.'),
    ('JavaScript', Skill.CAT_PROGRAMMING,
     'ECMAScript / JavaScript language including ES2015+.'),
    ('HTML', Skill.CAT_FRONTEND, 'HTML5 markup and semantics.'),
    ('CSS', Skill.CAT_FRONTEND,
     'CSS3, layouts, responsive design, animations.'),
    ('React', Skill.CAT_FRONTEND, 'React.js component-based UI library.'),
    ('Flask', Skill.CAT_BACKEND, 'Flask lightweight Python web framework.'),
    ('Django', Skill.CAT_BACKEND, 'Django batteries-included Python framework.'),
    ('Node.js', Skill.CAT_BACKEND, 'Node.js JavaScript runtime + Express.'),
    ('MySQL', Skill.CAT_DATABASE, 'MySQL Community Edition relational database.'),
    ('PostgreSQL', Skill.CAT_DATABASE, 'PostgreSQL advanced open-source RDBMS.'),
    ('MongoDB', Skill.CAT_DATABASE, 'MongoDB document-oriented NoSQL database.'),
    ('Git', Skill.CAT_TOOLS, 'Distributed version control system.'),
    ('GitHub', Skill.CAT_TOOLS, 'GitHub — collaboration, pull requests, CI hooks.'),
    ('Docker', Skill.CAT_DEVOPS, 'Docker container engine and Dockerfiles.'),
    ('AWS', Skill.CAT_CLOUD, 'Amazon Web Services (EC2, S3, Lambda, RDS, etc.).'),
    ('Azure', Skill.CAT_CLOUD, 'Microsoft Azure cloud platform.'),
    ('Pandas', Skill.CAT_AI_ML, 'Pandas data manipulation library for Python.'),
    ('NumPy', Skill.CAT_AI_ML, 'NumPy scientific computing for Python.'),
    ('Scikit-learn', Skill.CAT_AI_ML,
     'Scikit-learn classical ML — TF-IDF, cosine similarity, classifiers.'),
    ('Selenium', Skill.CAT_TESTING, 'Selenium web-browser automation / testing.'),
    ('JUnit', Skill.CAT_TESTING, 'JUnit Java unit testing framework.'),
    ('REST API', Skill.CAT_BACKEND,
     'RESTful HTTP APIs, JSON, OpenAPI / Swagger.'),
    ('Linux', Skill.CAT_TOOLS,
     'GNU/Linux command line, shell scripting, administration.'),
    ('Power BI', Skill.CAT_TOOLS,
     'Microsoft Power BI — business intelligence dashboards and reports.'),
]


def seed_roles() -> int:
    created = 0
    for name, desc in ROLES:
        if db.session.query(Role).filter_by(name=name).first() is None:
            db.session.add(Role(name=name, description=desc))
            created += 1
    if created:
        db.session.commit()
        print(f'[Roles] inserted {created} role(s).')
    else:
        print('[Roles] 0 inserted — already present.')
    return created


def seed_skills() -> int:
    existing = {
        s.name.lower() for s in db.session.query(Skill.name).all()
    }
    created = 0
    for name, category, desc in SKILLS:
        if name.lower() in existing:
            continue
        db.session.add(Skill(name=name, category=category, description=desc))
        existing.add(name.lower())
        created += 1
    if created:
        db.session.commit()
        print(f'[Skills] inserted {created} skill(s).')
    else:
        print('[Skills] 0 inserted — already present.')
    return created


def main() -> int:
    env = os.environ.get('FLASK_ENV', 'development')
    app = create_app(env)
    with app.app_context():
        total_roles = db.session.query(Role).count()
        total_skills = db.session.query(Skill).count()
        print(f'Environment: {env}')
        print(f'Database URI: {app.config.get("SQLALCHEMY_DATABASE_URI")[:64]}...')
        print(f'Before seed — roles={total_roles}, skills={total_skills}')

        try:
            roles_added = seed_roles()
            skills_added = seed_skills()
        except Exception as exc:  # pragma: no cover
            db.session.rollback()
            print(f'SEED FAILED: {exc}', file=sys.stderr)
            return 1

        total_roles = db.session.query(Role).count()
        total_skills = db.session.query(Skill).count()
        print(f'After seed  — roles={total_roles} (+{roles_added}),'
              f' skills={total_skills} (+{skills_added})')
        print('Seed complete.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
