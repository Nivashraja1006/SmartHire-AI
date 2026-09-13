import unittest
from datetime import date, timedelta

from app import create_app, db
from app.models import Application, Candidate, CandidateScore, Interview, Job, JobSkill, Role, Skill, User


class Phase10TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        db.session.add_all([Role(name=Role.ADMIN), Role(name=Role.RECRUITER), Role(name=Role.CANDIDATE)])
        recruiter_role = Role.query.filter_by(name=Role.RECRUITER).one()
        self.recruiter = User(full_name='Analytics Recruiter', email='analytics@example.com', role=recruiter_role)
        self.recruiter.set_password('password-123')
        candidate = Candidate(full_name='Test Candidate', email='candidate@example.com')
        self.job = Job(recruiter=self.recruiter, title='Python Engineer', company_name='SmartHire', status=Job.STATUS_ACTIVE)
        db.session.add_all([self.recruiter, candidate, self.job])
        db.session.flush()
        self.application = Application(candidate=candidate, job=self.job, status=Application.STATUS_SHORTLISTED, is_shortlisted=True)
        db.session.add(self.application)
        db.session.flush()
        db.session.add(CandidateScore(application=self.application, overall_score=88, skill_score=90, experience_score=80))
        db.session.commit()
        self.client = self.app.test_client()
        self.client.post('/login', data={'email': self.recruiter.email, 'password': 'password-123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_overview_and_funnel_use_database_values(self):
        overview = self.client.get('/api/recruiter/analytics/overview')
        self.assertEqual(overview.status_code, 200)
        self.assertEqual(overview.get_json()['overview']['total_applications'], 1)
        funnel = self.client.get(f'/api/recruiter/analytics/funnel/{self.job.id}')
        self.assertEqual(funnel.get_json()['funnel']['strong_matches'], 1)
        self.assertEqual(funnel.get_json()['funnel']['shortlisted'], 1)

    def test_interview_conflict_and_csv_export(self):
        payload = {'application_id': self.application.id, 'interview_date': (date.today() + timedelta(days=1)).isoformat(), 'interview_time': '10:00', 'duration_minutes': '60', 'interview_type': 'Online'}
        response = self.client.post('/recruiter/interviews/create', data=payload)
        self.assertEqual(response.status_code, 302)
        response = self.client.post('/recruiter/interviews/create', data={**payload, 'interview_time': '10:30'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Scheduling conflict detected.', response.data)
        report = self.client.get('/api/recruiter/analytics/export/ranking')
        self.assertEqual(report.status_code, 200)
        self.assertIn(b'Candidate,Job,Score', report.data)

    def test_recruiter_applications_endpoint_returns_dropdown_data(self):
        response = self.client.get('/api/recruiter/applications')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn('applications', payload)
        self.assertEqual(len(payload['applications']), 1)
        app = payload['applications'][0]
        self.assertEqual(app['id'], self.application.id)
        self.assertEqual(app['name'], 'Test Candidate')
        self.assertEqual(app['title'], 'Python Engineer')
        self.assertEqual(app['label'], 'Test Candidate · Python Engineer')

    def test_custom_date_range_and_unauthorized_job_is_hidden(self):
        other = User(full_name='Other Recruiter', email='other@example.com', role=Role.query.filter_by(name=Role.RECRUITER).one())
        other.set_password('password-123')
        db.session.add(other)
        db.session.commit()
        other_job = Job(recruiter=other, title='Other Job', company_name='Other', status=Job.STATUS_ACTIVE)
        db.session.add(other_job)
        db.session.commit()
        self.assertEqual(self.client.get(f'/api/recruiter/analytics/job/{other_job.id}').status_code, 404)
        start = (date.today() - timedelta(days=2)).isoformat()
        end = date.today().isoformat()
        self.assertEqual(self.client.get(f'/api/recruiter/analytics/trends?start_date={start}&end_date={end}').status_code, 200)

    def test_match_page_handles_warmup_html_responses_without_raw_json_parse_error(self):
        response = self.client.get(f'/recruiter/jobs/{self.job.id}/candidates/{self.application.candidate_id}/match')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('fetchJsonWithRetry', html)
        self.assertIn('waking up', html.lower())


if __name__ == '__main__':
    unittest.main()
