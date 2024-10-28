from src.models.task_template import TaskTemplate


def test_template_no_jwt(app):
    # task templates require jwt
    res = app.test_client().get('api/v1/task_template')
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}


def test_template_no_task_type(app, active_token):
    # check task type
    res = app.test_client().get(
        'api/v1/task_template',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 400


def test_template_bad_task_type(app, active_token):
    # task type that doesn't exist cannot be asked for
    res = app.test_client().get(
        'api/v1/task_template?taskType=BAD_TASK_TYPE',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 400


def test_template_good_request(app, active_token):
    # good request
    res = app.test_client().get(
        'api/v1/task_template?taskType=UPDATE_FUNCTION',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
