import unittest

from app import create_app, db
from app.ai.education_matcher import match_education
from app.ai.experience_matcher import match_experience
from app.ai.scoring_engine import calculate_scores
from app.ai.semantic_matcher import semantic_similarity
from app.ai.skill_extractor import canonicalize, extract_skills
from app.ai.skill_matcher import match_skills
from app.models import Candidate, Job, JobSkill, Resume, Role, Skill, User
from app.services.matching_service import match_candidate_to_job


class Phase6TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        db.session.add_all([Role(name=Role.ADMIN), Role(name=Role.RECRUITER), Role(name=Role.CANDIDATE)])
        db.session.add_all([Skill(name='Python', category=Skill.CAT_PROGRAMMING), Skill(name='Django', category=Skill.CAT_BACKEND), Skill(name='Flask', category=Skill.CAT_BACKEND), Skill(name='MySQL', category=Skill.CAT_DATABASE)])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_extraction_alias_and_skill_matching(self):
        self.assertEqual(canonicalize('JS'), 'JavaScript')
        names = {item['name'] for item in extract_skills('Python, ReactJS and ML')}
        self.assertIn('Python', names)
        result = match_skills([{'name': 'Python', 'importance': 'Mandatory'}, {'name': 'Django', 'importance': 'Mandatory'}], ['Python', 'Flask'])
        self.assertEqual(result['matched_skills'][0]['type'], 'Exact Match')
        self.assertEqual(result['partial_skills'][0]['type'], 'Related Match')
        self.assertEqual(result['missing_skills'][0]['skill'], 'Django')

    def test_component_matchers_and_scoring(self):
        self.assertEqual(match_experience(3, 2, 4)['experience_score'], 100.0)
        self.assertEqual(match_education([{'degree': 'B.Tech Computer Science'}], 'B.Tech')['education_score'], 100.0)
        self.assertGreater(semantic_similarity('Python Flask API', 'Python Flask backend API'), 0)
        result = calculate_scores({'skill_score': 100, 'experience_score': 100, 'semantic_score': 100, 'project_relevance_score': 100, 'education_score': 100, 'certification_score': 100})
        self.assertEqual(result['overall_score'], 100.0)
        self.assertEqual(result['recommendation'], 'Excellent Match')

    def test_matching_service_persists_score(self):
        recruiter_role = Role.query.filter_by(name=Role.RECRUITER).one()
        user = User(full_name='Recruiter', email='phase6@example.com', role=recruiter_role)
        user.set_password('password-123')
        db.session.add(user)
        db.session.flush()
        job = Job(recruiter_id=user.id, title='Python Developer', company_name='Demo', description='Python Django API MySQL', min_experience=2, max_experience=4, required_education='B.Tech')
        candidate = Candidate(full_name='Candidate', email='candidate@phase6.com', total_experience=3)
        db.session.add_all([job, candidate])
        db.session.flush()
        python = Skill.query.filter_by(name='Python').one()
        django = Skill.query.filter_by(name='Django').one()
        db.session.add_all([JobSkill(job=job, skill=python, importance='Mandatory'), JobSkill(job=job, skill=django, importance='Mandatory'), Resume(candidate=candidate, original_filename='resume.txt', stored_filename='resume.txt', file_path='uploads/resumes/resume.txt', file_type='txt', extracted_text='Candidate Python Flask 3 years experience B.Tech', parsed_data={'education': [{'degree': 'B.Tech'}], 'projects': []}, processing_status=Resume.STATUS_COMPLETED)])
        db.session.commit()
        result = match_candidate_to_job(candidate.id, job.id)
        self.assertGreaterEqual(result['overall_score'], 0)
        self.assertTrue(result['missing_skills'])
        self.assertIsNotNone(candidate.applications.first().score)


if __name__ == '__main__':
    unittest.main()
