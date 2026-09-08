import sys, os, tempfile, traceback

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_p2_out.log')

def w(s: str) -> None:
    with open(LOG, 'a', encoding='utf-8') as fh:
        fh.write(str(s) + '\n')

CHECK = [0]; OK = [0]
def chk(name, pred):
    CHECK[0] += 1
    v = bool(pred)
    if v: OK[0] += 1
    w(('PASS' if v else 'FAIL') + ' ' + name)
    return v

try:
    open(LOG, 'w').close()  # truncate
    w('start')

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'venv', 'Lib', 'site-packages'))
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ['PYTHONPYCACHEPREFIX'] = os.path.join(os.path.dirname(__file__), '.pycache')
    os.makedirs(os.environ['PYTHONPYCACHEPREFIX'], exist_ok=True)
    w('paths ok')

    from app import create_app, db
    from app.models import (
        Role, Skill, User, Job, Candidate, JobSkill, CandidateSkill,
        Resume, Application, CandidateScore, Interview, ActivityLog,
    )
    import seed_data
    w('imports ok')

    app = create_app('testing')
    with app.app_context():
        db.create_all()
        registered = set(db.metadata.tables.keys())
        expected = {
            'roles','skills','users','jobs','candidates','job_skills',
            'candidate_skills','resumes','applications','candidate_scores',
            'interviews','activity_logs',
        }
        chk('12 tables registered', expected.issubset(registered))
        w('tables created: ' + str(sorted(expected)))

        seed_data.seed_roles()
        seed_data.seed_skills()
        rc = db.session.query(Role).count()
        sc = db.session.query(Skill).count()
        chk('3 roles', rc == 3)
        chk('>=25 skills', sc >= 25)

        admin = db.session.query(Role).filter_by(name=Role.ADMIN).first()
        recruiter_role = db.session.query(Role).filter_by(name=Role.RECRUITER).first()
        chk('Admin role', admin is not None)
        chk('Recruiter role', recruiter_role is not None)

        py = db.session.query(Skill).filter_by(name='Python').first()
        fsk = db.session.query(Skill).filter_by(name='Flask').first()
        react = db.session.query(Skill).filter_by(name='React').first()
        msq = db.session.query(Skill).filter_by(name='MySQL').first()
        chk('Python cat=Programming', py and py.category == Skill.CAT_PROGRAMMING)
        chk('Flask cat=Backend', fsk and fsk.category == Skill.CAT_BACKEND)
        chk('React cat=Frontend', react and react.category == Skill.CAT_FRONTEND)
        chk('MySQL cat=Database', msq and msq.category == Skill.CAT_DATABASE)

        rec = User(full_name='Alice R', email='alice@example.com', role_id=recruiter_role.id)
        rec.set_password('Str0ng!')
        db.session.add(rec)
        db.session.commit()
        chk('password verify (correct)', rec.check_password('Str0ng!'))
        chk('password verify (wrong) -> False', not rec.check_password('nope'))
        hashed = rec.password_hash
        chk('password is hashed', hashed and hashed != 'Str0ng!' and (
            hashed.startswith('scrypt:') or hashed.startswith('pbkdf2')
        ))

        chk('is_authenticated', rec.is_authenticated)
        chk('is_active default True', rec.is_active)
        chk('get_id', rec.get_id() == str(rec.id))

        dup = User(full_name='Dup', email='alice@example.com', role_id=recruiter_role.id)
        dup.set_password('x')
        db.session.add(dup)
        raised = False
        try:
            db.session.commit()
        except Exception:
            raised = True
            db.session.rollback()
        chk('Unique User email', raised)

        job = Job(
            recruiter_id=rec.id,
            title='Senior Backend Engineer',
            company_name='Acme',
            location='Remote',
            employment_type=Job.TYPE_FULL_TIME,
            description='Build Flask SaaS.',
            min_experience=3.0, max_experience=7.0,
            required_education="Bachelor's",
            status=Job.STATUS_ACTIVE,
        )
        db.session.add(job); db.session.flush()
        js1 = JobSkill(job_id=job.id, skill_id=py.id, importance=JobSkill.IMPORTANCE_MANDATORY, weight=2.0)
        js2 = JobSkill(job_id=job.id, skill_id=fsk.id, importance=JobSkill.IMPORTANCE_PREFERRED)
        js3 = JobSkill(job_id=job.id, skill_id=msq.id, importance=JobSkill.IMPORTANCE_PREFERRED)
        db.session.add_all([js1, js2, js3])
        db.session.commit()
        chk('Job -> recruiter backpop', job in list(rec.jobs) and job.recruiter is rec)
        chk('3 job_skills', len(list(job.job_skills)) == 3)

        dup_js = JobSkill(job_id=job.id, skill_id=py.id, importance=JobSkill.IMPORTANCE_PREFERRED)
        db.session.add(dup_js); raised = False
        try: db.session.commit()
        except Exception: raised = True; db.session.rollback()
        chk('Unique JobSkill(job,skill)', raised)

        cand = Candidate(user_id=None, full_name='Bob A', email='bob@example.com',
                         phone='+919876543210', current_location='Bangalore',
                         total_experience=4.5, profile_summary='Flask dev')
        db.session.add(cand); db.session.flush()
        res = Resume(candidate_id=cand.id, original_filename='bob.pdf', stored_filename='r1.pdf',
                     file_path='uploads/resumes/r1.pdf', file_type='pdf')
        db.session.add(res)
        cs1 = CandidateSkill(candidate_id=cand.id, skill_id=py.id, proficiency_level=CandidateSkill.PROF_ADVANCED)
        cs2 = CandidateSkill(candidate_id=cand.id, skill_id=fsk.id)
        cs3 = CandidateSkill(candidate_id=cand.id, skill_id=msq.id, proficiency_level=CandidateSkill.PROF_BEGINNER, source=CandidateSkill.SRC_MANUAL)
        db.session.add_all([cs1, cs2, cs3])
        db.session.commit()
        chk('Candidate has 1 resume + 3 skills',
            len(list(cand.resumes)) == 1 and len(list(cand.candidate_skills)) == 3)

        dup_cs = CandidateSkill(candidate_id=cand.id, skill_id=py.id)
        db.session.add(dup_cs); raised=False
        try: db.session.commit()
        except Exception: raised=True; db.session.rollback()
        chk('Unique CandidateSkill(cand,skill)', raised)

        ap = Application(candidate_id=cand.id, job_id=job.id, status=Application.STATUS_APPLIED)
        db.session.add(ap); db.session.commit()
        dup_ap = Application(candidate_id=cand.id, job_id=job.id)
        db.session.add(dup_ap); raised=False
        try: db.session.commit()
        except Exception: raised=True; db.session.rollback()
        chk('Unique Application(cand,job)', raised)
        db.session.commit()
        chk('Candidate/Jobs applications backpop', ap in list(cand.applications) and ap in list(job.applications))

        sc = CandidateScore(application_id=ap.id, overall_score=82.5, skill_score=88.0,
                             experience_score=75.0, education_score=80.0,
                             recommendation=CandidateScore.REC_SHORTLIST)
        from datetime import date, time
        iv = Interview(application_id=ap.id, interview_date=date(2026,9,15),
                       interview_time=time(10,30), interview_type=Interview.TYPE_TECHNICAL,
                       status=Interview.STATUS_SCHEDULED, notes='DS live coding')
        db.session.add_all([sc, iv]); db.session.commit()
        chk('Application.score 1:1', ap.score is not None and ap.score.overall_score == 82.5)
        chk('Application.interviews ->1', len(list(ap.interviews)) == 1)

        bad = CandidateScore(application_id=99999)
        raised = False
        try:
            bad.overall_score = 500.0
            db.session.add(bad); db.session.flush()
        except Exception:
            raised = True; db.session.rollback()
        chk('CandidateScore clamp 0-100', raised)

        logs = [
            ActivityLog(user_id=rec.id, activity_type=ActivityLog.TYPE_JOB_CREATED, description='Create Job'),
            ActivityLog(user_id=rec.id, activity_type=ActivityLog.TYPE_RESUME_UPLOADED, description='Upload Resume'),
            ActivityLog(user_id=None, activity_type=ActivityLog.TYPE_CANDIDATE_RANKED, description='AI ranked'),
        ]
        db.session.add_all(logs); db.session.commit()
        chk('ActivityLogs for recruiter=2', len(list(rec.activity_logs)) == 2)

        rb = db.session.query(Role).count(); sb = db.session.query(Skill).count()
        seed_data.seed_roles(); seed_data.seed_skills()
        ra = db.session.query(Role).count(); sa = db.session.query(Skill).count()
        chk('Seed roles idempotent', rb == ra)
        chk('Seed skills idempotent', sb == sa)

        rec.is_active = False
        db.session.commit()
        chk('User.is_active False honored', rec.is_active is False)
        rec.is_active = True
        db.session.commit()

        client = app.test_client()
        r = client.get('/')
        html = r.get_data(as_text=True)
        chk('GET / == 200 (Phase 1 landing)', r.status_code == 200)
        for n in [
            'SmartHire AI','Real-Time AI-Powered Candidate Intelligence Platform',
            'Get Started','Explore Features',
            'AI Resume Analysis','Smart Candidate Ranking',
            'Skill Gap Detection','Real-Time Analytics',
            'Core Capabilities','How It Works','100% Free',
        ]:
            chk('landing contains: ' + n, n in html)
        r2 = client.get('/health')
        chk('/health == 200 ok', r2.status_code == 200 and r2.get_json() and r2.get_json().get('status') == 'ok')
        r3 = client.get('/static/css/style.css')
        chk('/static/css/style.css', r3.status_code == 200 and len(r3.data) > 2000)
        r4 = client.get('/static/js/main.js')
        chk('/static/js/main.js', r4.status_code == 200 and len(r4.data) > 200)

    w('END: TOTAL=%d PASS=%d FAIL=%d' % (CHECK[0], OK[0], CHECK[0] - OK[0]))
    RC = 0 if CHECK[0] == OK[0] else 2
except Exception as exc:
    with open(LOG, 'a', encoding='utf-8') as fh:
        fh.write('EXCEPTION: %s\n%s\n' % (exc, traceback.format_exc()))
    RC = 3

with open(LOG, 'a', encoding='utf-8') as fh:
    fh.write('EXITCODE=%d\n' % RC)
sys.exit(RC)
