import io
import re
import unittest

from app import create_app, db
from app.models import Candidate, Resume, Role, User


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        db.session.add_all([
            Role(name=Role.ADMIN),
            Role(name=Role.RECRUITER),
            Role(name=Role.CANDIDATE),
        ])
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_registration_hashes_password_and_rejects_admin(self):
        response = self.client.post('/register', data={
            'full_name': 'Taylor Recruiter',
            'email': 'Taylor@Example.com',
            'password': 'secure-pass-123',
            'confirm_password': 'secure-pass-123',
            'role': 'Recruiter',
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(email='taylor@example.com').one()
        self.assertEqual(user.role.name, Role.RECRUITER)
        self.assertNotEqual(user.password_hash, 'secure-pass-123')
        self.assertTrue(user.check_password('secure-pass-123'))

        response = self.client.post('/register', data={
            'full_name': 'Admin Impostor',
            'email': 'admin@example.com',
            'password': 'secure-pass-123',
            'confirm_password': 'secure-pass-123',
            'role': 'Admin',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(User.query.filter_by(email='admin@example.com').first())

    def test_login_role_guard_and_logout(self):
        role = Role.query.filter_by(name=Role.CANDIDATE).one()
        user = User(full_name='Candidate User', email='candidate@example.com', role=role)
        user.set_password('secure-pass-123')
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/login', data={
            'email': 'candidate@example.com',
            'password': 'secure-pass-123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/candidate/dashboard'))
        self.assertEqual(self.client.get('/candidate/dashboard').status_code, 200)
        self.assertEqual(self.client.get('/admin/dashboard').status_code, 403)

        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/login'))
        self.assertEqual(self.client.get('/candidate/dashboard').status_code, 302)

    def test_candidate_resume_upload_accepts_rendered_csrf_token(self):
        role = Role.query.filter_by(name=Role.CANDIDATE).one()
        user = User(full_name='Candidate User', email='upload@example.com', role=role)
        user.set_password('secure-pass-123')
        db.session.add(user)
        db.session.flush()
        db.session.add(Candidate(user_id=user.id, full_name=user.full_name, email=user.email))
        db.session.commit()

        self.client.post('/login', data={
            'email': 'upload@example.com',
            'password': 'secure-pass-123',
        })
        page = self.client.get('/candidate/resumes')
        csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', page.get_data(as_text=True)).group(1)

        response = self.client.post('/candidate/resumes/upload', data={
            'csrf_token': csrf_token,
            'resume': (io.BytesIO(b'Candidate resume text'), 'resume.txt'),
        }, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Resume.query.count(), 1)


if __name__ == '__main__':
    unittest.main()
