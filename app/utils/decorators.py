from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def role_required(role_name):
    """Require an authenticated user with the exact named role."""
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if not current_user.role or current_user.role.name != role_name:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator