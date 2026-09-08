"""Create one development admin account from ADMIN_EMAIL and ADMIN_PASSWORD."""
from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

from app import create_app, db
from app.models import Role, User


load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


def main():
    email = os.environ.get('ADMIN_EMAIL', '').strip().lower()
    password = os.environ.get('ADMIN_PASSWORD', '')
    if not email or not password:
        print('Set ADMIN_EMAIL and ADMIN_PASSWORD in .env before running this command.', file=sys.stderr)
        return 1
    if len(password) < 8:
        print('ADMIN_PASSWORD must contain at least 8 characters.', file=sys.stderr)
        return 1

    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    with app.app_context():
        role = Role.query.filter_by(name=Role.ADMIN).first()
        if role is None:
            print('Admin role is missing. Run seed_data.py first.', file=sys.stderr)
            return 1
        if User.query.filter_by(email=email).first() is not None:
            print('An account with this email already exists.', file=sys.stderr)
            return 1

        admin = User(full_name='Platform Administrator', email=email, role=role)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f'Admin account created for {email}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())