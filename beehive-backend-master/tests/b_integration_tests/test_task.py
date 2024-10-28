from base64 import b32encode
import time

from src.models.task import TaskStatus, TaskType
from src.models.user import User
from src.models.work import WorkStatus
from src.models.work_record import SolutionRating


def test_cuckoo_task_post_endpoint_no_token(app, active_token):
    # post task requires an inner token
    res = app.test_client().post('api/v1/task/cuckoo')
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}

    # post task requires an inner token
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}


def test_cuckoo_task_post_endpoint_valid_task(app, active_token, active_token_user_id, inner_token):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # post valid task
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'Test task',
            'userName': trello_user
        }
    )
    assert res.status_code == 200

    task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_cuckoo_task_post_endpoint_valid_task.task_ids = [task_id]

    # post was successful and the task is saved with pending status
    res = app.test_client().get(
        f'api/v1/task/{task_id}',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['status'] == TaskStatus.PENDING


def test_cuckoo_task_put_endpoint_non_existing_task(app, active_token_user_id, inner_token):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # put non-existing task id
    res = app.test_client().put(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'taskId': 'nope',
            'userName': trello_user,
            'description': 'new description'
        }
    )
    assert res.status_code == 404


def test_cuckoo_task_put_endpoint_valid_params(app, active_token, active_token_user_id, inner_token):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # post valid task
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'initial description',
            'userName': trello_user
        }
    )
    assert res.status_code == 200

    task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_cuckoo_task_put_endpoint_valid_params.task_ids = [task_id]

    # post was successful and the task is saved
    res = app.test_client().get(
        f'api/v1/task/{task_id}',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['description'] == 'initial description'
    assert res.json['data']['status'] == TaskStatus.PENDING
    assert res.json['data']['priority'] == 2
    assert res.json['data']['tags'] == []
    assert res.json['data']['skills'] == []

    # update task description
    res = app.test_client().put(
        f'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'taskId': task_id,
            'userName': trello_user,
            'description': 'new description'
        }
    )
    assert res.status_code == 200

    # update task tags
    res = app.test_client().put(
        f'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'taskId': task_id,
            'userName': trello_user,
            'tags': ['test-tag']
        }
    )
    assert res.status_code == 200

    # update task skills
    res = app.test_client().put(
        f'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'taskId': task_id,
            'userName': trello_user,
            'skills': ['test-skill']
        }
    )
    assert res.status_code == 200

    # make sure that the task's work item was updated as well (before
    # updating the project zip since that action will trigger task
    # rebuild and create a new work item)
    res = app.test_client().get(
        f'api/v1/backoffice/task/{task_id}/work',
        headers={'X-BEE-AUTH': inner_token}
    )
    assert res.status_code == 200
    assert len(res.json['data']) == 1
    assert res.json['data'][0]['description'] == 'new description'
    assert res.json['data'][0]['tags'] == ['test-tag']
    assert res.json['data'][0]['skills'] == ['test-skill']

    # update task status (after project zip since the job re-sets the status to pending)
    res = app.test_client().put(
        f'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'taskId': task_id,
            'userName': trello_user,
            'status': TaskStatus.PAUSED.name
        }
    )
    assert res.status_code == 200

    # task fields should now be updated
    res = app.test_client().get(
        f'api/v1/task/{task_id}',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['description'] == 'new description'
    assert res.json['data']['status'] == TaskStatus.PAUSED
    assert res.json['data']['tags'] == ['test-tag']
    assert res.json['data']['skills'] == ['test-skill']

    # make sure that the task's work items are updated as well - both
    # should have the updated description and one should be available
    # and the other unavailable since the task was rebuilt when the
    # project zip was updated
    res = app.test_client().get(
        f'api/v1/backoffice/task/{task_id}/work',
        headers={'X-BEE-AUTH': inner_token}
    )
    assert res.status_code == 200
    assert len(res.json['data']) == 1
    assert res.json['data'][0]['description'] == 'new description'
    assert res.json['data'][0]['tags'] == ['test-tag']
    assert res.json['data'][0]['skills'] == ['test-skill']
    assert res.json['data'][0]['status'] == WorkStatus.AVAILABLE
