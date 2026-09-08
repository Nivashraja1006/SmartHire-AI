from __future__ import annotations

from collections import defaultdict, deque
from functools import wraps
from threading import Lock
from time import monotonic

from flask import current_app, flash, jsonify, redirect, request
from flask_login import current_user


_buckets = defaultdict(deque)
_lock = Lock()


def local_rate_limit(limit, window_seconds=60):
    """Small process-local limiter for sensitive endpoints; no external service required."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if current_app.testing or request.method in {'GET', 'HEAD', 'OPTIONS'}:
                return view(*args, **kwargs)
            identity = str(current_user.get_id()) if current_user.is_authenticated else request.remote_addr or 'anonymous'
            key = (view.__module__, view.__name__, identity)
            now = monotonic()
            with _lock:
                bucket = _buckets[key]
                while bucket and now - bucket[0] >= window_seconds:
                    bucket.popleft()
                if len(bucket) >= limit:
                    if not request.is_json and not request.path.startswith('/api/'):
                        flash('Too many requests. Please try again shortly.', 'error')
                        return redirect(request.referrer or request.path)
                    response = jsonify({'success': False, 'error': 'Too many requests. Please try again shortly.'})
                    response.status_code = 429
                    response.headers['Retry-After'] = str(window_seconds)
                    return response
                bucket.append(now)
            return view(*args, **kwargs)
        return wrapped
    return decorator
