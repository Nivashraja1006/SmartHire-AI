"""Phase 2 programmatic verification against in-memory SQLite."""
from __future__ import annotations

import os
import sys
import tempfile

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ.setdefault(
    'PYTHONPYCACHEPREFIX',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '.pycache'),
)
os.makedirs(os.environ['PYTHONPYCACHEPREFIX'], exist_ok=True)

_LOG_STDOUT = os.path.join(tempfile.gettempdir(), 'phase2_tests.log')
_LOG_STDERR = os.path.join(tempfile.gettempdir(), 'phase2_tests_err.log')
_orig_stdout = sys.stdout
_orig_stderr = sys.stderr
_log_fh = open(_LOG_STDOUT, 'w', encoding='utf-8')
_err_fh = open(_LOG_STDERR, 'w', encoding='utf-8')
sys.stdout = _log_fh
sys.stderr = _err_fh

from app import create_app, db  # noqa: E402
from app.models import (  # noqa: E402
    Role, Skill, User, Job, Candidate, JobSkill, CandidateSkill,
    Resume, Application, CandidateScore, Interview, ActivityLog,
)

import seed_data  # noqa: E402


CHECK_COUNT = [0]
PASS_COUNT = [0]


def check(name, predicate):
    CHECK_COUNT[0] += 1
    ok = bool(predicate)
    if ok:
        PASS_COUNT[0] += 1
    status = 'PASS' if ok else 'FAIL'
    print(f'[{status}] {name}')
    if not ok:
        print('    >>> assertion failed', file=sys.stderr)
    return ok


def main() -> int:
    app = create_app('testing')
    with app.app_context():
        # 1. create all tables, verify 12 tables registered in metadata
        db.create_all()
        registered_tables = set(db.metadata.tables.keys())
        expected = {
            'roles', 'skills', 'users', 'jobs', 'candidates',
            'job_skills', 'candidate_skills', 'resumes', 'applications',
            'candidate_scores', 'interviews', 'activity_logs',
        }
        check('12 tables registered in metadata',
              expected.issubset(registered_tables))

        # 2. run seed script — 3 roles + 25+ skills
        seed_data.seed_roles()
        seed_data.seed_skills()
        role_count = db.session.query(Role).count()
        skill_count = db.session.query(Skill).count()
        check('3 roles seeded', role_count == 3)
        check('>= 25 skills seeded', skill_count >= 25)
        admin_role = db.session.query(Role).filter_by(name=Role.ADMIN).first()
        recruiter_role = db.session.query(Role).filter_by(name=Role.RECRUITER).first()
        check('Admin role exists', admin_role is not None)
        check('Recruiter role exists', recruiter_role is not None)

        # Skill categories exist correctly
        python = db.session.query(Skill).filter_by(name='Python').first()
        flask_skill = db.session.query(Skill).filter_by(name='Flask').first()
        react = db.session.query(Skill).filter_by(name='React').first()
        mysql_sk = db.session.query(Skill).filter_by(name='MySQL').first()
        check('Python category = Programming Language',
              python and python.category == Skill.CAT_PROGRAMMING)
        check('Flask category = Backend',
              flask_skill and flask_skill.category == Skill.CAT_BACKEND)
        check('React category = Frontend',
              react and react.category == Skill.CAT_FRONTEND)
        check('MySQL category = Database',
              mysql_sk and mysql_sk.category == Skill.CAT_DATABASE)

        # 3. Create user (Recruiter) + hashed password
        recruiter = User(full_name='Alice Recruiter', email='alice@example.com',
                         role_id=recruiter_role.id)
        recruiter.set_password('Str0ngPass!')
        db.session.add(recruiter)
        db.session.commit()
        check('User set_password + check_password correct pw',
              recruiter.check_password('Str0ngPass!'))
        check('User check_password wrong pw -> False',
              not recruiter.check_password('nope'))
        check('password_hash != plaintext (hashed)',
              recruiter.password_hash and recruiter.password_hash != 'Str0ngPass!'
              and recruiter.password_hash.startswith('scrypt:')
              or recruiter.password_hash and recruiter.password_hash.startswith('pbkdf2'))

        # UserMixin attrs
        check('UserMixin is_authenticated = True', recruiter.is_authenticated)
        check('UserMixin is_active = True (default)', recruiter.is_active)
        check('UserMixin get_id() returns str(id)', recruiter.get_id() == str(recruiter.id))

        # Unique email constraint
        dup = User(full_name='Impostor', email='alice@example.com',
                   role_id=recruiter_role.id)
        dup.set_password('whatever')
        db.session.add(dup)
        raised = False
        try:
            db.session.commit()
        except Exception:
            raised = True
            db.session.rollback()
        check('Unique email constraint prevents duplicate user', raised)

        # 4. Job creation + relationships
        job = Job(
            recruiter_id=recruiter.id,
            title='Senior Backend Engineer',
            company_name='Acme Corp',
            location='Remote',
            employment_type=Job.TYPE_FULL_TIME,
            description='Build awesome SaaS backends in Python + Flask.',
            min_experience=3.0,
            max_experience=7.0,
            required_education="Bachelor's",
            status=Job.STATUS_ACTIVE,
        )
        db.session.add(job)
        db.session.flush()

        # JobSkill — mandatory Python, preferred Flask, preferred MySQL
        js1 = JobSkill(job_id=job.id, skill_id=python.id,
                       importance=JobSkill.IMPORTANCE_MANDATORY, weight=2.0)
        js2 = JobSkill(job_id=job.id, skill_id=flask_skill.id,
                       importance=JobSkill.IMPORTANCE_PREFERRED, weight=1.5)
        js3 = JobSkill(job_id=job.id, skill_id=mysql_sk.id,
                       importance=JobSkill.IMPORTANCE_PREFERRED)
        db.session.add_all([js1, js2, js3])
        db.session.commit()
        check('Job created + recruiter back_populates',
              job in list(recruiter.jobs) and job.recruiter is recruiter)
        check('Job has 3 job_skills', len(list(job.job_skills)) == 3)

        # Unique (job, skill) in job_skills
        dup_js = JobSkill(job_id=job.id, skill_id=python.id,
                          importance=JobSkill.IMPORTANCE_PREFERRED)
        db.session.add(dup_js)
        raised = False
        try:
            db.session.commit()
        except Exception:
            raised = True
            db.session.rollback()
        check('Unique JobSkill(job, skill) constraint works', raised)

        # 5. Candidate + Resume + CandidateSkill
        cand = Candidate(
            user_id=None,
            full_name='Bob Applicant',
            email='bob@example.com',
            phone='+919876543210',
            current_location='Bangalore',
            total_experience=4.5,
            profile_summary='Backend Python dev with Flask and MySQL.',
        )
        db.session.add(cand)
        db.session.flush()
        resume = Resume(
            candidate_id=cand.id,
            original_filename='bob_resume.pdf',
            stored_filename='resume_1.pdf',
            file_path='uploads/resumes/resume_1.pdf',
            file_type='pdf',
            processing_status=Resume.STATUS_UPLOADED,
        )
        db.session.add(resume)
        cs1 = CandidateSkill(candidate_id=cand.id, skill_id=python.id,
                             proficiency_level=CandidateSkill.PROF_ADVANCED,
                             source=CandidateSkill.SRC_RESUME)
        cs2 = CandidateSkill(candidate_id=cand.id, skill_id=flask_skill.id,
                             proficiency_level=CandidateSkill.PROF_INTERMEDIATE,
                             source=CandidateSkill.SRC_RESUME)
        cs3 = CandidateSkill(candidate_id=cand.id, skill_id=mysql_sk.id,
                             proficiency_level=CandidateSkill.PROF_BEGINNER,
                             source=CandidateSkill.SRC_MANUAL)
        db.session.add_all([cs1, cs2, cs3])
        db.session.commit()
        check('Candidate created + has 1 resume, 3 skills',
              len(list(cand.resumes)) == 1 and len(list(cand.candidate_skills)) == 3)

        # Unique (candidate, skill) in candidate_skills
        dup_cs = CandidateSkill(candidate_id=cand.id, skill_id=python.id,
                                proficiency_level=CandidateSkill.PROF_BEGINNER)
        db.session.add(dup_cs)
        raised = False
        try:
            db.session.commit()
        except Exception:
            raised = True
            db.session.rollback()
        check('Unique CandidateSkill(candidate, skill) constraint works', raised)

        # 6. Application -> CandidateScore + Interview
        app_obj = Application(candidate_id=cand.id, job_id=job.id,
                              status=Application.STATUS_APPLIED)
        db.session.add(app_obj)
        db.session.commit()

        # Unique (candidate, job) application constraint
        dup_app = Application(candidate_id=cand.id, job_id=job.id,
                              status=Application.STATUS_UNDER_REVIEW)
        db.session.add(dup_app)
        raised = False
        try:
            db.session.commit()
        except Exception:
            raised = True
            db.session.rollback()
        check('Unique Application(candidate, job) constraint works', raised)

        # Now really commit the single application
        db.session.commit()
        check('Candidate.applications and Job.applications back-populate',
              app_obj in list(cand.applications) and app_obj in list(job.applications))

        score = CandidateScore(
            application_id=app_obj.id,
            overall_score=82.5,
            skill_score=88.0,
            experience_score=75.0,
            project_score=0.0,
            education_score=80.0,
            certification_score=0.0,
            recommendation=CandidateScore.REC_SHORTLIST,
        )
        db.session.add(score)

        from datetime import date, time
        interview = Interview(
            application_id=app_obj.id,
            interview_date=date(2026, 9, 15),
            interview_time=time(10, 30),
            interview_type=Interview.TYPE_TECHNICAL,
            status=Interview.STATUS_SCHEDULED,
            notes='Technical panel: DS + Flask live coding',
        )
        db.session.add(interview)
        db.session.commit()
        check('CandidateScore unique 1:1 with Application (retrieve via rel)',
              app_obj.score is not None and app_obj.score.overall_score == 82.5)
        check('Interview + 1 interview for application',
              len(list(app_obj.interviews)) == 1)
        # Score range clamp
        bad = CandidateScore(application_id=99999)
        raised = False
        try:
            bad.overall_score = 500.0
            db.session.add(bad)
            db.session.flush()
        except Exception:
            raised = True
            db.session.rollback()
        check('CandidateScore validates 0-100 range', raised)

        # 7. Activity Log
        log1 = ActivityLog(user_id=recruiter.id,
                           activity_type=ActivityLog.TYPE_JOB_CREATED,
                           description=f'Created job {job.title}')
        log2 = ActivityLog(user_id=recruiter.id,
                           activity_type=ActivityLog.TYPE_RESUME_UPLOADED,
                           description=f'Uploaded resume {resume.original_filename}')
        log3 = ActivityLog(user_id=None,  # anonymous-safe
                           activity_type=ActivityLog.TYPE_CANDIDATE_RANKED,
                           description='AI ranked candidates for job_id=%d' % job.id)
        db.session.add_all([log1, log2, log3])
        db.session.commit()
        check('ActivityLog 3 records + back_populates user',
              len(list(recruiter.activity_logs)) == 2)

        # 8. Idempotence of seed script
        roles_before = db.session.query(Role).count()
        skills_before = db.session.query(Skill).count()
        seed_data.seed_roles()
        seed_data.seed_skills()
        roles_after = db.session.query(Role).count()
        skills_after = db.session.query(Skill).count()
        check('Seed data idempotent (role count unchanged)',
              roles_before == roles_after)
        check('Seed data idempotent (skill count unchanged)',
              skills_before == skills_after)

        # 9. Flask-Login User.is_active toggles correctly
        recruiter.is_active = False
        db.session.commit()
        check('User.is_active = False honored via UserMixin',
              recruiter.is_active is False)
        recruiter.is_active = True
        db.session.commit()

        # 10. Phase 1 landing page still works (in testing config)
        client = app.test_client()
        r = client.get('/')
        html = r.get_data(as_text=True)
        check('GET / == 200 (Phase 1 landing page)', r.status_code == 200)
        for needle in [
            'SmartHire AI',
            'Real-Time AI-Powered Candidate Intelligence Platform',
            'Get Started',
            'Explore Features',
            'AI Resume Analysis',
            'Smart Candidate Ranking',
            'Skill Gap Detection',
            'Real-Time Analytics',
            'Core Capabilities',
            'How It Works',
            '100% Free',
        ]:
            check(f'Landing page contains: {needle}', needle in html)

        r2 = client.get('/health')
        check('GET /health == 200 {status:ok}',
              r2.status_code == 200
              and r2.get_json() and r2.get_json().get('status') == 'ok')

        r3 = client.get('/static/css/style.css')
        check('/static/css/style.css loads', r3.status_code == 200 and len(r3.data) > 2000)
        r4 = client.get('/static/js/main.js')
        check('/static/js/main.js loads', r4.status_code == 200 and len(r4.data) > 200)

        # Summary
        print()
        print('=' * 60)
        print(f'TOTAL CHECKS: {CHECK_COUNT[0]}')
        print(f'PASSED:       {PASS_COUNT[0]}')
        print(f'FAILED:       {CHECK_COUNT[0] - PASS_COUNT[0]}')
        print('=' * 60)
        return 0 if PASS_COUNT[0] == CHECK_COUNT[0] else 2


def _teardown(rc: int) -> None:
    global _log_fh, _err_fh
    try:
        _log_fh.flush()
        _err_fh.flush()
    except Exception:
        pass
    summary_line = (
        f'Phase2Tests: TOTAL={CHECK_COUNT[0]} PASS={PASS_COUNT[0]} '
        f'FAIL={CHECK_COUNT[0]-PASS_COUNT[0]} EXIT={rc}\n'
    )
    try:
        _orig_stdout.write(summary_line)
        _orig_stdout.flush()
    except Exception:
        pass
    try:
        _log_fh.close()
        _err_fh.close()
    except Exception:
        pass


if __name__ == '__main__':
    try:
        rc = main()
    except Exception as _exc:  # pragma: no cover
        import traceback
        traceback.print_exc(file=_err_fh)
        rc = 3
    _teardown(rc)
    sys.exit(rc)
