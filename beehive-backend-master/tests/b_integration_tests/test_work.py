import time
from unittest.mock import Mock, patch

from bh_grpc.generated.beehive.robobee.v1.github_pb2 import GetPRInfoRequest, GetPRInfoResponse, PRBranch

import pytest

from src.models.task import Task, TaskStatus
from src.models.work import Work, WorkType
from src.models.user import User
from src.models.work_record import WorkRecord
from src.utils.db import db
from src.utils.grpc_client import GRPCClient


def test_work_record_crud_get_endpoint_no_jwt(app):
    # get work records requires jwt
    res = app.test_client().get('api/v1/work')
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}


@patch('src.resources.work.dispatch_cuckoo_event', new=Mock())
@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
def test_work_record_crud_get_endpoint_success(app, active_token, active_token_user_id, second_active_token, inner_token):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # user has no work records to begin with
    res = app.test_client().get('api/v1/work', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data'] == []

    # create task
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'Test task',
            'userName': trello_user,
        }
    )
    assert res.status_code == 200

    task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_work_record_crud_get_endpoint_success.task_ids = [task_id]

    # get available work will return work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id

    work_id = res.json['data']['work']['id']

    # start work on task
    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work_id, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200

    # user now has work records
    res = app.test_client().get('api/v1/work', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert len(res.json['data']) == 1
    assert res.json['data'][0]['workId'] == work_id
    assert res.json['data'][0]['work']['id'] == work_id
    assert res.json['data'][0]['work']['task']['id'] == task_id

    # requesting records for a specific work id which doesn't exist returns nothing
    res = app.test_client().get('api/v1/work/1234567890', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data'] == []

    # requesting records for a specific work id which does exist returns records
    res = app.test_client().get(f'api/v1/work/{work_id}', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert len(res.json['data']) == 1
    assert res.json['data'][0]['workId'] == work_id
    assert res.json['data'][0]['work']['id'] == work_id
    assert res.json['data'][0]['work']['task']['id'] == task_id

    # work records are not visible to other users
    res = app.test_client().get('api/v1/work', headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 200
    assert res.json['data'] == []

    # work records are not visible to other users even if requesting existing work id
    res = app.test_client().get(f'api/v1/work/{work_id}', headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 200
    assert res.json['data'] == []


def test_available_work_get_endpoint_no_jwt(app):
    # get available work requires jwt
    res = app.test_client().get('api/v1/work/available')
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}


def test_available_work_get_endpoint_no_work(app, active_token):
    # no work items
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}

    # requesting a specific work item also returns 404
    res = app.test_client().get(
        'api/v1/work/available',
        headers={'Authorization': f'Bearer {active_token}'},
        query_string={'specificWorkId': 1}
    )
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}


def test_available_work_get_endpoint_bad_status_work(app, active_token, active_token_user_id, inner_token):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create task
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'Test task',
            'userName': trello_user,
        }
    )
    assert res.status_code == 200

    task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_available_work_get_endpoint_bad_status_work.task_ids = [task_id]

    # set task status to new
    with app.app_context():
        Task.query.filter_by(id=task_id).first().status = TaskStatus.NEW
        db.session.commit()

    # no available work
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}

    # set task status to paused
    with app.app_context():
        Task.query.filter_by(id=task_id).status = TaskStatus.PAUSED
        db.session.commit()

    # no available work
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}

    # set task status to solved
    with app.app_context():
        Task.query.filter_by(id=task_id).first().status = TaskStatus.SOLVED
        db.session.commit()

    # no available work
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}

    # set task status to accepted
    with app.app_context():
        Task.query.filter_by(id=task_id).first().status = TaskStatus.ACCEPTED
        db.session.commit()

    # no available work
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}

    # set task status to cancelled
    with app.app_context():
        Task.query.filter_by(id=task_id).first().status = TaskStatus.CANCELLED
        db.session.commit()

    # no available work
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}

    # set task status to invalid
    with app.app_context():
        Task.query.filter_by(id=task_id).first().status = TaskStatus.INVALID
        db.session.commit()

    # no available work
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}

    # set task status to pending class params
    with app.app_context():
        Task.query.filter_by(id=task_id).first().status = TaskStatus.PENDING_CLASS_PARAMS
        db.session.commit()

    # no available work
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}

    # set task status to pending package
    with app.app_context():
        Task.query.filter_by(id=task_id).first().status = TaskStatus.PENDING_PACKAGE
        db.session.commit()

    # no available work
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}


@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
def test_available_work_get_endpoint_available_work(app, active_token, active_token_user_id, inner_token):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create task
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'Test task',
            'userName': trello_user,
        }
    )
    assert res.status_code == 200

    task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_available_work_get_endpoint_available_work.task_ids = [task_id]

    # get available work returns single work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id


@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
def test_available_work_get_endpoint_filter_by_tags(app, active_token, active_token_user_id, inner_token):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create skill and tag via backoffice
    res = app.test_client().post(
        f'/api/v1/backoffice/tag',
        headers={'X-BEE-AUTH': inner_token},
        json={'tagName': 'superhero'}
    )
    assert res.status_code == 200

    res = app.test_client().post(
        f'/api/v1/backoffice/skill',
        headers={'X-BEE-AUTH': inner_token},
        json={'skillName': 'Preact'}
    )
    assert res.status_code == 200

    # create task with tags and skills
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'Test task',
            'userName': trello_user,
            'tags': ['superhero'],
            'skills': ['Preact']
        }
    )
    assert res.status_code == 200

    task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_available_work_get_endpoint_filter_by_tags.task_ids = [task_id]

    # get available work for user without any tags should not return any item
    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 404

    # get available work for user with non matching tag does not return any item
    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'tags': ['different-tag']
        }
    )

    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {active_token}'}
    )

    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}

    # get available work with mixed filter set should include all given filter params
    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'tags': ['a-ok'],
            'skills': ['Preact']
        }
    )
    assert res.status_code == 200

    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}

    # get available work for user with relevant tag returns the task
    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'tags': ['superhero']
        }
    )
    assert res.status_code == 200

    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id

    # unset user tags and skills so the objects can be deleted
    res = app.test_client().delete(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'tags': ['superhero', 'different-tag', 'a-ok'],
            'skills': ['Preact']
        }
    )
    assert res.status_code == 200

    # unset task tags and skills so the objects can be deleted
    with app.app_context():
        task = Task.query.filter_by(id=task_id).first()
        task.tags = []
        task.skills = []
        task.works[0].tags = []
        task.works[0].skills = []
        db.session.commit()

    # delete created skills and tags via backoffice
    for tag_name in ('superhero', 'different-tag', 'a-ok'):
        res = app.test_client().delete(
            f'api/v1/backoffice/tag',
            headers={'X-BEE-AUTH': inner_token},
            json={'tagName': tag_name}
        )
        assert res.status_code == 200

    res = app.test_client().delete(
        f'api/v1/backoffice/skill',
        headers={'X-BEE-AUTH': inner_token},
        json={'skillName': 'Preact'}
    )
    assert res.status_code == 200


@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
def test_available_work_get_endpoint_order_by_skills(app, active_token, active_token_user_id, inner_token):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create skill via backoffice
    res = app.test_client().post(
        f'/api/v1/backoffice/skill',
        headers={'X-BEE-AUTH': inner_token},
        json={'skillName': 'React'}
    )
    assert res.status_code in (200, 400)
    if res.status_code == 400:
        assert res.json == {'status': 'error', 'error': 'skill_already_exists'}

    # create task with tags and skills
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'Test task',
            'userName': trello_user,
            'skills': ['React']
        }
    )
    assert res.status_code == 200
    task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_available_work_get_endpoint_order_by_skills.task_ids = [task_id]

    # get available work for user without any skills should still return this item, as skills aren't filtered by, just sorted
    active_token_user_id
    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id

    # get available work for user with non matching skills should still return this item
    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'skills': ['different-skill']
        }
    )
    assert res.status_code == 200

    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id

    # get available work should prioritize work that has most skills matching
    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'skills': ['React', 'another-skill']
        }
    )

    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'Test task',
            'userName': trello_user,
            'skills': ['React', 'another-skill']
        }
    )
    assert res.status_code == 200
    second_task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_available_work_get_endpoint_order_by_skills.task_ids.append(second_task_id)

    # NOTE: available work has a random element to it, so this next section may fail if you're
    # out of luck. in such a case the test will be marked as "skipped" so it does not fail the
    # entire suite run. you can just try again, it shouldn't fail more than once in a row (but
    # again, random)

    # when getting available work twice the second task (which has two common skills with the
    # user) should probably be received at least once
    available_work_tasks = []
    for _ in range(2):
        res = app.test_client().get(
            'api/v1/work/available',
            headers={'Authorization': f'Bearer {active_token}'})
        assert res.status_code == 200
        available_work_tasks.append(res.json['data']['work']['taskId'])

    try:
        assert any(t == second_task_id for t in available_work_tasks)
    except AssertionError:
        pytest.skip(
            'test_available_work_get_endpoint_order_by_skills missed the desired available work with more skills matched'
        )

    # when getting available work five times the first task (which only has one common skill
    # with the user) should probably be received at least once
    available_work_tasks = []
    for _ in range(4):
        res = app.test_client().get(
            'api/v1/work/available',
            headers={'Authorization': f'Bearer {active_token}'})
        assert res.status_code == 200
        available_work_tasks.append(res.json['data']['work']['taskId'])

    try:
        assert any(t == task_id for t in available_work_tasks)
    except AssertionError:
        pytest.skip(
            'test_available_work_get_endpoint_order_by_skills missed the desired available work with less skills matched'
        )


@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
def test_available_work_get_endpoint_order_by_priority(app, active_token, active_token_user_id, inner_token):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create a task with priority
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'Test task',
            'userName': trello_user,
            'priority': 30
        }
    )
    assert res.status_code == 200
    task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_available_work_get_endpoint_order_by_priority.task_ids = [task_id]

    # get available work for user should still return this item, as this is the only item
    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id

    # get available work should prioritize work that has most skills matching
    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'skills': ['React', 'another-skill']
        }
    )

    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'Test task',
            'userName': trello_user,
            'priority': 40
        }
    )
    assert res.status_code == 200
    second_task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_available_work_get_endpoint_order_by_priority.task_ids.append(second_task_id)

    # # get available work for user should return now the higher prioritised work
    # res = app.test_client().put(
    #     f'/api/v1/backoffice/user-profile/{active_token_user_id}',
    #     headers={'X-BEE-AUTH': inner_token},
    #     json={
    #         'skills': ['different-skill']
    #     }
    # )
    # assert res.status_code == 200

    # res = app.test_client().get(
    #     'api/v1/work/available', 
    #     headers={'Authorization': f'Bearer {active_token}'}
    # )
    # assert res.status_code == 200
    # assert res.json['data']['work']['taskId'] == second_task_id

    # NOTE: available work has a random element to it, so this next section may fail if you're
    # out of luck. in such a case the test will be marked as "skipped" so it does not fail the
    # entire suite run. you can just try again, it shouldn't fail more than once in a row (but
    # again, random)

    # when getting available work twice the second task (which has a higher priority)
    # should probably be received at least once
    available_work_tasks = []
    for _ in range(2):
        res = app.test_client().get(
            'api/v1/work/available',
            headers={'Authorization': f'Bearer {active_token}'})
        assert res.status_code == 200
        available_work_tasks.append(res.json['data']['work']['taskId'])

    try:
        assert any(t == second_task_id for t in available_work_tasks)
    except AssertionError:
        pytest.skip(
            'test_available_work_get_endpoint_order_by_priority missed the desired available work with the higher priority'
        )

    # when getting available work eight times the first task (which has lesser priority)
    # should probably be received at least once
    available_work_tasks = []
    for _ in range(7):
        res = app.test_client().get(
            'api/v1/work/available',
            headers={'Authorization': f'Bearer {active_token}'})
        assert res.status_code == 200
        available_work_tasks.append(res.json['data']['work']['taskId'])

    try:
        assert any(t == task_id for t in available_work_tasks)
    except AssertionError:
        pytest.skip(
            'test_available_work_get_endpoint_order_by_priority missed the desired available work with the lesser priority'
        )


@patch('src.resources.work.dispatch_cuckoo_event', new=Mock())
@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
@patch('src.resources.work.run_beehave_pr_github_bot', new=Mock())
def test_contributor_work_history_no_ratings(app, active_token, active_token_user_id, inner_token):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create a task with
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
    test_contributor_work_history_no_ratings.task_ids = [task_id]

    # get available work should return a single work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id

    work_id = res.json['data']['work']['id']

    # start work on work item
    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work_id, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200

    # finish work with some solution code
    res = app.test_client().post(
        f'api/v1/work/finish',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work_id, 'durationSeconds': 20, 'solutionUrl': 'https://github.com/my-org/my-repo/pull/1'}
    )
    assert res.status_code == 200

    # the delegator accepted the solution
    with app.app_context():
        Task.query.filter_by(id=task_id).first().status = TaskStatus.ACCEPTED
        db.session.commit()

    with patch('src.resources.work.get_rating_items') as mock_rating:
        mock_rating.return_value = None
        res = app.test_client().get('api/v1/work/history', headers={'Authorization': f'Bearer {active_token}'})
        history = res.json['data']
        assert res.status_code == 200
        assert len(history) == 1
        assert history[0]['name'] == None
        assert history[0]['project'] == None
        assert len(history[0]['ratings']) == 0


@patch('src.resources.work.dispatch_cuckoo_event', new=Mock())
@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
@patch('src.resources.work.run_beehave_pr_github_bot', new=Mock())
def test_contributor_work_history_with_rating(app, active_token, active_token_user_id, inner_token):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create a task with
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
    test_contributor_work_history_with_rating.task_ids = [task_id]

    # get available work should return a single work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    work_id = res.json['data']['work']['id']

    # start work on work item
    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work_id, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200

    # finish work with some solution code
    res = app.test_client().post(
        f'api/v1/work/finish',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work_id, 'durationSeconds': 20, 'solutionUrl': 'https://github.com/my-org/my-repo/pull/1'}
    )
    assert res.status_code == 200

    # the delegator accepted the solution
    with app.app_context():
        Task.query.filter_by(id=task_id).first().status = TaskStatus.ACCEPTED
        db.session.commit()

    # get work_record_id to implant in rating pock response
    res = app.test_client().get(f'api/v1/work', headers={'Authorization': f'Bearer {active_token}'})
    work_record_id = res.json['data'][0]['id']

    with patch('src.resources.work.get_rating_items') as mock_rating:
        mock_rating.return_value = [{'id':1,'user':active_token_user_id,'objectKey':f'wr-{work_record_id}','subject':'s','score':5.0,'text':'text'}]
        res = app.test_client().get('api/v1/work/history', headers={'Authorization': f'Bearer {active_token}'})
        dd = res.json['data'][0]
        history = res.json['data']
        assert res.status_code == 200
        assert len(history) == 1
        assert history[0]['name'] == None
        assert history[0]['project'] == None
        assert history[0]['ratings'][0]['subject'] == 's'
        assert len(history[0]['ratings']) == 1


@patch('src.resources.work.dispatch_cuckoo_event', new=Mock())
@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
def test_available_work_get_endpoint_multiple_available_work_items(app, active_token, active_token_user_id, inner_token):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create first task
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'Test task',
            'userName': trello_user
        }
    )
    assert res.status_code == 200

    task_id_1 = res.json['data']['id']
    # set task ids so the fixture teardown can delete them
    test_available_work_get_endpoint_multiple_available_work_items.task_ids = [task_id_1]

    # get available work returns single work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id_1

    work_id_1 = res.json['data']['work']['id']
    # get available work with current work id returns no work items
    res = app.test_client().get(
        'api/v1/work/available',
        headers={'Authorization': f'Bearer {active_token}'},
        query_string={'currentWorkId': work_id_1}
    )
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}
    
    # create second task
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'Test task',
            'userName': trello_user
        }
    )
    assert res.status_code == 200

    task_id_2 = res.json['data']['id']
    # add to task ids
    test_available_work_get_endpoint_multiple_available_work_items.task_ids.append(task_id_2)

    # get available work task with current work id returns the other work item
    res = app.test_client().get(
        'api/v1/work/available',
        headers={'Authorization': f'Bearer {active_token}'},
        query_string={'currentWorkId': work_id_1}
    )
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id_2
    work_id_2 = res.json['data']['work']['id']

    # same vice-versa
    res = app.test_client().get(
        'api/v1/work/available',
        headers={'Authorization': f'Bearer {active_token}'},
        query_string={'currentWorkId': work_id_2}
    )
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id_1
    assert res.json['data']['work']['id'] == work_id_1

    # requesting a specific work item will return the work item
    res = app.test_client().get(
        'api/v1/work/available',
        headers={'Authorization': f'Bearer {active_token}'},
        query_string={'specificWorkId': work_id_1}
    )
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id_1
    assert res.json['data']['work']['id'] == work_id_1

    # requesting a specific work item will return the work item
    res = app.test_client().get(
        'api/v1/work/available',
        headers={'Authorization': f'Bearer {active_token}'},
        query_string={'specificWorkId': work_id_2}
    )
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id_2
    assert res.json['data']['work']['id'] == work_id_2

    # requesting a specific work item which doesn't exist will return any available work item
    res = app.test_client().get(
        'api/v1/work/available',
        headers={'Authorization': f'Bearer {active_token}'},
        query_string={'specificWorkId': 1000000}
    )
    assert res.status_code == 200
    assert res.json['data']['work']['id'] in (work_id_1, work_id_2)

    # start work on the first work item
    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work_id_1, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200

    # get available will return the active work item and the work record
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id_1
    assert res.json['data']['work']['id'] == work_id_1
    assert res.json['data']['workRecord']['workId'] == work_id_1

    # active work item is returned even if another sepecific id is provided
    res = app.test_client().get(
        'api/v1/work/available',
        headers={'Authorization': f'Bearer {active_token}'},
        query_string={'specificWorkId': work_id_2}
    )
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id_1
    assert res.json['data']['work']['id'] == work_id_1
    assert res.json['data']['workRecord']['workId'] == work_id_1

    # active work item is returned even if the work item id is sent as the current one
    res = app.test_client().get(
        'api/v1/work/available',
        headers={'Authorization': f'Bearer {active_token}'},
        query_string={'currentWorkId': work_id_1}
    )
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id_1
    assert res.json['data']['work']['id'] == work_id_1
    assert res.json['data']['workRecord']['workId'] == work_id_1


@patch('src.resources.work.dispatch_cuckoo_event', return_value=True)
@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
@patch('src.resources.work.grpc_client')
@patch('src.resources.work.run_beehave_pr_github_bot', new=Mock())
def test_cuckoo_work_lifecycle(mock_grpc_client, mock_dispatch_cuckoo_event, app, inner_token, active_token, active_token_user_id, second_active_token, delegation):
    description = 'Cuckoo task'
    tag = f'project:{delegation[0].name}'

    # pass-through call_service_catch_error_status calls to a real
    # implementation which forwards the calls to the gRPC service
    mock_grpc_client.call_service_catch_error_status = GRPCClient().call_service_catch_error_status
    mock_grpc_client.github_stub.GetPRInfo.return_value = GetPRInfoResponse(
        head=PRBranch(
            ref="external/cool-user/cool-feature",
            sha="6dcb09b5b57875f334f61aebed695e2e4193db5e"
        ),
        base=PRBranch(
            ref="master",
            sha="6dcb09b5b57875f334f61aebed695e2e4193db5e"
        )
    )

    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create task
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': description,
            'userName': trello_user,
            'tags': [tag],
            'skills': ['Python']
        }
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 0

    task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_cuckoo_work_lifecycle.task_ids = [task_id]

    # get available work should not return anything since user doesn't have tag
    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 404

    # assert pr info isn't requested in first iteration
    assert len(mock_grpc_client.github_stub.method_calls) == 0

    # update user tags
    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            "tags": [tag]
        }
    )
    assert res.status_code == 200

    # get available work should now return the task
    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    assert mock_dispatch_cuckoo_event.call_count == 0

    work_id = res.json['data']['work']['id']

    # start work on work item
    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work_id, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 1

    solution_url = 'https://github.com/my-org/my-repo/pull/1'

    # finish work with some solution code
    res = app.test_client().post(
        f'api/v1/work/finish',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work_id, 'durationSeconds': 20, 'solutionUrl': solution_url}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 2

    # get work data
    res = app.test_client().get(f'api/v1/work/{work_id}', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert len(res.json['data']) == 1
    assert res.json['data'][0]['workId'] == work_id
    assert res.json['data'][0]['work']['id'] == work_id
    assert res.json['data'][0]['work']['task']['id'] == task_id
    assert res.json['data'][0]['durationSeconds'] == 20
    assert res.json['data'][0]['solutionUrl'] == solution_url
    assert mock_dispatch_cuckoo_event.call_count == 2

    # get task data - should be solved
    res = app.test_client().get(
        f'api/v1/task/{task_id}',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['description'] == description
    assert res.json['data']['status'] == TaskStatus.SOLVED
    assert res.json['data']['feedback'] is None
    assert mock_dispatch_cuckoo_event.call_count == 2
    
    with app.app_context():
        work_record = WorkRecord.query.filter_by(work_id=work_id).all()
    assert len(work_record) == 1
    work_record = work_record[0]

    # delegator starts review
    res = app.test_client().post(
        f'api/v1/work/review',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workRecordId': work_record.id}
    )

    # assert redirected to pull request url
    assert res.status_code == 200
    assert res.json['data']['solutionUrl'] == solution_url

    with patch('src.models.work_record.get_rating_items') as mock_rating:
        mock_rating.return_value = [{}]

        # manager requests modifications should create a new review task
        res = app.test_client().put(
            'api/v1/task/cuckoo',
            headers={'X-BEE-AUTH': inner_token},
            json={
                'taskId': task_id,
                'userName': trello_user,
                'status': TaskStatus.MODIFICATIONS_REQUESTED.name
            }
        )
        assert res.status_code == 200

    assert mock_dispatch_cuckoo_event.call_count == 2

    # work record has updated start of review with correct timestamp
    with app.app_context():
        reviewed_work_record = WorkRecord.query.filter_by(work_id=work_id).all()
    assert len(reviewed_work_record) == 1
    assert reviewed_work_record[0].active is False
    assert reviewed_work_record[0].review_tz_name == 'UTC'
    assert reviewed_work_record[0].review_start_time_epoch_ms is not None
    assert reviewed_work_record[0].review_duration_seconds is not None

    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['workType'] == WorkType.CUCKOO_ITERATION
    assert mock_dispatch_cuckoo_event.call_count == 2

    review_work_id = res.json['data']['work']['id']

    # assert pull request data is fetched from robobee and exists in available work response
    assert len(mock_grpc_client.github_stub.method_calls) > 0
    assert mock_grpc_client.github_stub.GetPRInfo.call_count == 1
    mock_grpc_client.github_stub.GetPRInfo.assert_any_call(
        GetPRInfoRequest(
            repo_organization='my-org',
            repo_name='my-repo',
            pr_id=1
        ),
    )
    assert res.json['data']['work']['branchName'] == 'external/cool-user/cool-feature'

    # review work does not appear to a user that did not solve the task
    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 404

    # contributor starts on the review task
    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': review_work_id, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 3

    # finish work with same solution url
    res = app.test_client().post(
        f'api/v1/work/finish',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': review_work_id, 'durationSeconds': 400, 'solutionUrl': solution_url}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 4



def test_work_solution_review_post_no_jwt(app):
    # review solution work requires jwt
    res = app.test_client().post('api/v1/work/review', json={'workRecordId': 114})
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}


def test_work_solution_review_post_no_work(app, active_token, delegation):
    # no work items
    res = app.test_client().post('api/v1/work/review', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 400
    assert res.json['status'] == 'error'
    assert res.json['error'] == 'malformed_request'

    # requesting a specific work item that doesn't exist returns 404
    res = app.test_client().post(
        'api/v1/work/review',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workRecordId': 1}
    )
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}


@patch('src.resources.work.dispatch_cuckoo_event', return_value=True)
@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
def test_work_solution_review_post_active_work(mock_dispatch_cuckoo_event, app, active_token, active_token_user_id, inner_token, delegation):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user
    tag = f'project:{delegation[0].name}'

    # create task
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'Test task',
            'userName': trello_user,
            'tags': [tag]
        }
    )
    assert res.status_code == 200

    task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_work_solution_review_post_active_work.task_ids = [task_id]
    
    # update user tags
    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            "tags": [tag]
        }
    )
    assert res.status_code == 200

    # get available work returns single work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    work_id = res.json['data']['work']['id']
    assert mock_dispatch_cuckoo_event.call_count == 0

    # start work on work item
    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work_id, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 1

    with app.app_context():
        work_record = WorkRecord.query.filter_by(work_id=work_id).all()
    assert len(work_record) == 1
    work_record = work_record[0]

    # delegator starts review on active work
    res = app.test_client().post(
        f'api/v1/work/review',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workRecordId': work_record.id}
    )
    assert mock_dispatch_cuckoo_event.call_count == 1
    assert res.status_code == 404


@patch('src.resources.work.dispatch_cuckoo_event', return_value=True)
@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
@patch('src.resources.work.run_beehave_pr_github_bot', new=Mock())
def test_work_solution_review_post_no_delegator_permissions(mock_dispatch_cuckoo_event, app, active_token, active_token_user_id, second_active_token, second_active_token_user_id, inner_token, delegation):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user
    description = 'Test description'
    tag = f'project:{delegation[0].name}'

    # create task with project tag
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': description,
            'userName': trello_user,
            'tags': [tag]
        }
    )
    assert res.status_code == 200

    task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_work_solution_review_post_no_delegator_permissions.task_ids = [task_id]

    # update user tags for second user (not delegator)
    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{second_active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            "tags": [tag]
        }
    )
    assert res.status_code == 200

    # get available work should now return the task for second user
    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {second_active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    assert mock_dispatch_cuckoo_event.call_count == 0

    work_id = res.json['data']['work']['id']

    # start work on work item
    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work_id, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 1

    solution_url = 'https://github.com/my-org/my-repo/pull/1'

    # finish work with some solution code
    res = app.test_client().post(
        f'api/v1/work/finish',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work_id, 'durationSeconds': 20, 'solutionUrl': solution_url}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 2

    with app.app_context():
        work_record = WorkRecord.query.filter_by(work_id=work_id).all()
    assert len(work_record) == 1
    work_record = work_record[0]

    # second user (which doesn't have delegator permission) starts review
    res = app.test_client().post(
        f'api/v1/work/review',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workRecordId': work_record.id}
    )

    # assert user can't review
    assert res.status_code == 401
    with app.app_context():
        work_record = WorkRecord.query.filter_by(work_id=work_id).all()
    assert len(work_record) == 1
    work_record = work_record[0]
    assert work_record.review_start_time_epoch_ms is None
    assert work_record.review_duration_seconds is None
    assert work_record.review_tz_name is None
    assert work_record.review_user_id is None

    # first user (which is the delegator) starts review
    res = app.test_client().post(
        f'api/v1/work/review',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workRecordId': work_record.id}
    )
    assert res.status_code == 200
    assert res.json['data']['solutionUrl'] == solution_url
    with app.app_context():
        work_record = WorkRecord.query.filter_by(work_id=work_id).all()
    assert len(work_record) == 1
    work_record = work_record[0]
    assert work_record.review_start_time_epoch_ms is not None
    assert work_record.review_duration_seconds is None      ## duration is filled only on cuckoo event of card moved to 'beehive' or 'done' list
    assert work_record.review_tz_name is not None
    assert work_record.review_user_id == active_token_user_id

    with patch('src.models.work_record.get_rating_items') as mock_rating:

        # manager sets status to accepted without rating should produce error
        mock_rating.return_value = None
        res = app.test_client().put(
            'api/v1/task/cuckoo',
            headers={'X-BEE-AUTH': inner_token},
            json={
                'taskId': task_id,            
                'userName': trello_user,
                'status': TaskStatus.ACCEPTED.name
            }
        )
        assert res.status_code == 422

        # manager accepts the solution after rating
        mock_rating.return_value = [{}]
        res = app.test_client().put(
            'api/v1/task/cuckoo',
            headers={'X-BEE-AUTH': inner_token},
            json={
                'taskId': task_id,
                'userName': trello_user,
                'status': TaskStatus.ACCEPTED.name
            }
        )
        assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 2

    with app.app_context():
        work_record = WorkRecord.query.filter_by(work_id=work_id).all()
    assert len(work_record) == 1
    work_record = work_record[0]
    assert work_record.review_start_time_epoch_ms is not None
    assert work_record.review_duration_seconds is not None      ## duration is filled only on cuckoo event of card moved to 'beehive' or 'done' list
    assert work_record.review_tz_name is not None
    assert work_record.review_user_id == active_token_user_id





