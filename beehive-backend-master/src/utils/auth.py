from functools import wraps

from flask import current_app, request
from flask_jwt_extended import get_jwt, verify_jwt_in_request

from .errors import abort


JWT_ADDITIONAL_CLAIM_PREFIX = 'bh-'


def inner_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_auth_header_in_request(
            'X-BEE-AUTH',
            current_app.config.get('INTER_SERVICE_AUTH_KEYS', [])
        )
        return fn(*args, **kwargs)
    return wrapper


def metrics_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_auth_header_in_request(
            'Authorization',
            [f'Bearer {key}' for key in current_app.config.get('METRICS_AUTH_KEYS', [])]
        )
        return fn(*args, **kwargs)
    return wrapper


def verify_auth_header_in_request(header_name, valid_values):
    if header_name not in request.headers or \
        request.headers[header_name] not in valid_values:
        abort(401)


def activated_jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if not claims.get(f'{JWT_ADDITIONAL_CLAIM_PREFIX}activated'):
            abort(401)

        return fn(*args, **kwargs)
    return wrapper


def unactivated_jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get(f'{JWT_ADDITIONAL_CLAIM_PREFIX}activated'):
            abort(401)

        return fn(*args, **kwargs)
    return wrapper


def admin_jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if not claims.get(f'{JWT_ADDITIONAL_CLAIM_PREFIX}activated') or not claims.get(f'{JWT_ADDITIONAL_CLAIM_PREFIX}admin'):
            abort(401)

        return fn(*args, **kwargs)
    return wrapper


def test_after_response_add_cors_headers(response):
    """
    ONLY USED FOR TESTING AND SHOULD NOT BE USED OTHERWISE!

    add cors allow-all headers to responses
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response
