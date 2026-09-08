import unittest

from app import create_app, db
from app.copilot.intent_detector import detect_intent
from app.models import Application, Candidate, CandidateScore, Job, Role, User


class Phase9TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        db.session.add_all([Role(name=Role.ADMIN), Role(name=Role.RECRUITER), Role(name=Role.CANDIDATE)])
        role = Role.query.filter_by(name=Role.RECRUITER).one()
        self.user = User(full_name='Copilot Recruiter', email='copilot@example.com', role=role)
        self.user.set_password('password-123')
        db.session.add(self.user)
        db.session.flush()
        self.job = Job(recruiter_id=self.user.id, title='Python Developer', company_name='Demo', description='Python Django role')
        first = Candidate(full_name='Ava Menon', email='ava@example.com', total_experience=4)
        second = Candidate(full_name='Noah Williams', email='noah@example.com', total_experience=2)
        db.session.add_all([self.job, first, second])
        db.session.flush()
        db.session.add_all([
            CandidateScore(application=Application(job=self.job, candidate=first), overall_score=92.4, skill_score=95, experience_score=90, project_score=94, education_score=100, certification_score=60, semantic_score=88, recommendation='Excellent Match', matched_skills=[{'skill': 'Python'}], missing_skills=[{'skill': 'AWS'}], explanation={'strengths': ['Python matched'], 'weaknesses': ['AWS missing']}),
            CandidateScore(application=Application(job=self.job, candidate=second), overall_score=76.8, skill_score=80, experience_score=70, project_score=75, education_score=80, certification_score=50, semantic_score=70, recommendation='Strong Match', matched_skills=[{'skill': 'Python'}], missing_skills=[], explanation={'strengths': ['Python matched'], 'weaknesses': []}),
        ])
        db.session.commit()
        self.client = self.app.test_client()
        self.client.post('/login', data={'email': self.user.email, 'password': 'password-123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_intents(self):
        self.assertEqual(detect_intent('Who are the top candidates?'), 'TOP_CANDIDATES')
        self.assertEqual(detect_intent('What skills is Ava Menon missing?'), 'SKILL_GAP')
        self.assertEqual(detect_intent('Compare Ava Menon and Noah Williams'), 'CANDIDATE_COMPARISON')
        self.assertEqual(detect_intent('Who is best because they are young?'), 'FAIRNESS')

    def test_grounded_chat_and_history(self):
        response = self.client.post('/api/recruiter/copilot/chat', json={'message': 'Who are the top candidates?', 'job_id': self.job.id})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['intent'], 'TOP_CANDIDATES')
        self.assertIn('Ava Menon', data['response'])
        history = self.client.get(f"/api/recruiter/copilot/conversations/{data['conversation_id']}")
        self.assertEqual(history.status_code, 200)
        self.assertEqual(len(history.get_json()['messages']), 2)

    def test_fairness_and_unauthorized_job(self):
        response = self.client.post('/api/recruiter/copilot/chat', json={'message': 'Who is best because they are young?', 'job_id': self.job.id})
        self.assertIn('only evaluate candidates using job-relevant criteria', response.get_json()['response'])
        other = User(full_name='Other', email='other@example.com', role=Role.query.filter_by(name=Role.RECRUITER).one())
        other.set_password('password-123')
        db.session.add(other)
        db.session.commit()
        self.client.get('/logout')
        self.client.post('/login', data={'email': other.email, 'password': 'password-123'})
        response = self.client.post('/api/recruiter/copilot/chat', json={'message': 'Summarize this job', 'job_id': self.job.id})
        self.assertEqual(response.status_code, 200)
        self.assertIn('could not access', response.get_json()['response'])


if __name__ == '__main__':
    unittest.main()
