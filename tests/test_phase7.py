import unittest

from app import create_app, db
from app.ai.ranking_engine import rank_candidates_for_job
from app.models import Application, Candidate, CandidateScore, Job, JobSkill, Role, Skill, User


class Phase7TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        db.session.add_all([Role(name=Role.ADMIN), Role(name=Role.RECRUITER), Role(name=Role.CANDIDATE)])
        db.session.add_all([Skill(name='Python', category=Skill.CAT_PROGRAMMING), Skill(name='Django', category=Skill.CAT_BACKEND)])
        db.session.commit()
        role = Role.query.filter_by(name=Role.RECRUITER).one()
        self.user = User(full_name='Ranking Recruiter', email='ranking@example.com', role=role)
        self.user.set_password('password-123')
        db.session.add(self.user)
        db.session.flush()
        self.job = Job(recruiter_id=self.user.id, title='Python Developer', company_name='Demo', description='Python Django')
        db.session.add(self.job)
        db.session.flush()
        python_skill = Skill.query.filter_by(name='Python').one()
        django_skill = Skill.query.filter_by(name='Django').one()
        db.session.add_all([
            JobSkill(job=self.job, skill=python_skill, importance='Mandatory'),
            JobSkill(job=self.job, skill=django_skill, importance='Mandatory'),
        ])
        self.candidates = []
        for index, score_value in enumerate((92.4, 87.1, 38.0), 1):
            candidate = Candidate(full_name=f'Candidate {index}', email=f'candidate{index}@example.com', total_experience=index)
            db.session.add(candidate)
            db.session.flush()
            application = Application(job=self.job, candidate=candidate, status=Application.STATUS_UNDER_REVIEW)
            score = CandidateScore(application=application, overall_score=score_value, skill_score=score_value, experience_score=80, semantic_score=70, project_score=60, education_score=50, certification_score=40, recommendation='Excellent Match' if score_value > 90 else 'Strong Match' if score_value > 75 else 'Low Match', matched_skills=[{'skill': 'Python'}] if index != 3 else [], missing_skills=[{'skill': 'Django'}] if index != 1 else [], partial_skills=[])
            db.session.add_all([application, score])
            self.candidates.append(candidate)
        db.session.commit()
        self.client = self.app.test_client()
        self.client.post('/login', data={'email': 'ranking@example.com', 'password': 'password-123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_score_ordering_and_mandatory_coverage(self):
        results = rank_candidates_for_job(self.job.id)
        self.assertEqual([item['candidate'].full_name for item in results], ['Candidate 1', 'Candidate 2', 'Candidate 3'])
        self.assertEqual(results[0]['mandatory_coverage']['percent'], 50.0)
        self.assertEqual(results[2]['below_threshold'], True)

    def test_ranking_api_and_search(self):
        response = self.client.get(f'/api/recruiter/jobs/{self.job.id}/ranking')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['candidates'][0]['candidate_name'], 'Candidate 1')
        response = self.client.get(f'/recruiter/jobs/{self.job.id}/ranking?q=Candidate 2')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Candidate 2', response.data)

    def test_shortlist_and_compare_limit(self):
        candidate_id = self.candidates[0].id
        response = self.client.post(f'/api/recruiter/jobs/{self.job.id}/shortlist/{candidate_id}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['shortlisted'])
        response = self.client.delete(f'/api/recruiter/jobs/{self.job.id}/shortlist/{candidate_id}')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.get_json()['shortlisted'])
        response = self.client.post(f'/api/recruiter/jobs/{self.job.id}/compare', json={'candidate_ids': [item.id for item in self.candidates] + [999]})
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
