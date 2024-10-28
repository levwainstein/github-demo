from flask import abort as original_flask_abort, jsonify
from werkzeug.exceptions import HTTPException


def init_app(app):
    app.register_error_handler(400, handle_malformed_request)
    app.register_error_handler(401, handle_unauthorized)
    app.register_error_handler(404, handle_not_found)
    app.register_error_handler(405, handle_method_not_allowed)
    app.register_error_handler(422, handle_unprocessable_entity)
    app.register_error_handler(500, handle_server_error)


def abort(http_status_code, **kwargs):
    """
    From: https://github.com/flask-restful/flask-restful/blob/master/flask_restful/__init__.py
    Raise a HTTPException for the given http_status_code. Attach any keyword
    arguments to the exception for later processing.
    """
    try:
        original_flask_abort(http_status_code)
    except HTTPException as e:
        if len(kwargs):
            e.data = kwargs
        raise


def handle_malformed_request(err=None):
    response = {'status': 'error', 'error': 'malformed_request'}
    
    if err and hasattr(err, 'data'):
        # not using dict.update here to make sure we only deal with specific fields
        if 'code' in err.data:
            response['error'] = err.data['code']
        if 'description' in err.data:
            response['description'] = err.data['description']

    return jsonify(response), 400


def handle_unauthorized(err=None):
    return jsonify({'status': 'error', 'error': 'unauthorized'}), 401


def handle_not_found(err=None):
    return jsonify({'status': 'error', 'error': 'not_found'}), 404


def handle_method_not_allowed(err=None):
    return jsonify({'status': 'error', 'error': 'not_allowed'}), 405


def handle_server_error(err=None):
    return jsonify({'status': 'error', 'error': 'server_error'}), 500

def handle_unprocessable_entity(err=None):
    response = {'status': 'error', 'error': 'unprocessable_entity'}
    
    if err and hasattr(err, 'data'):
        # not using dict.update here to make sure we only deal with specific fields
        if 'code' in err.data:
            response['error'] = err.data['code']
        if 'description' in err.data:
            response['description'] = err.data['description']

    return jsonify(response), 422

