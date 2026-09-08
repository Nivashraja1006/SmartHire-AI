"""Seed Phase 6 demo data and calculate persisted Phase 7 rankings."""
from __future__ import annotations

import os

from app import create_app
from app.ai.ranking_engine import rank_candidates_for_job
from app.models import Job
from demo_phase6 import main as seed_phase6


def main():
    seed_phase6()
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    with app.app_context():
        for job in Job.query.filter(Job.title.like('% Demo')).all():
            results = rank_candidates_for_job(job.id, force=True)
            print(f'{job.title}: {len(results)} candidates ranked')
            for item in results[:5]:
                score = item['score'].overall_score if item['score'] else 0
                print(f"  #{item['rank']} {item['candidate'].full_name}: {score:.1f}")


if __name__ == '__main__':
    main()