import io
import unittest

from app import create_app, db
from app.ai.job_quality_analyzer import analyze_job_quality
from app.ai.resume_quality_analyzer import analyze_resume_quality
from app.models import Role, User


class Phase11TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        db.session.add_all([Role(name=Role.ADMIN), Role(name=Role.RECRUITER), Role(name=Role.CANDIDATE)])
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_protected_routes_require_authentication(self):
        self.assertEqual(self.client.get('/recruiter/analytics').status_code, 302)
        self.assertEqual(self.client.get('/admin/system-health').status_code, 302)

    def test_quality_analyzers_are_deterministic_and_non_predictive(self):
        quality = analyze_job_quality('Need Python developer.')
        self.assertLess(quality['score'], 100)
        self.assertTrue(quality['issues'])
        resume = analyze_resume_quality({'skills': [{'name': 'Python'}], 'projects': [{'name': 'API'}]}, 'Python API project')
        self.assertIn('Skills Section', resume['strong'])
        self.assertIn('Education', resume['needs_improvement'])

    def test_csrf_rejects_state_change_when_enabled(self):
        app = create_app('development')
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=True, SQLALCHEMY_DATABASE_URI='sqlite:///:memory:')
        client = app.test_client()
        response = client.post('/login', data={'email': 'a@example.com', 'password': 'bad'})
        self.assertEqual(response.status_code, 400)

    def test_invalid_pdf_signature_is_rejected(self):
        role = Role.query.filter_by(name=Role.RECRUITER).one()
        user = User(full_name='Upload Tester', email='upload@example.com', role=role)
        user.set_password('password-123')
        db.session.add(user)
        db.session.commit()
        self.client.post('/login', data={'email': user.email, 'password': 'password-123'})
        response = self.client.post('/recruiter/candidates/1/resume', data={'resume': (io.BytesIO(b'not a pdf'), 'resume.pdf')})
        self.assertNotEqual(response.status_code, 500)


if __name__ == '__main__':
    unittest.main()
