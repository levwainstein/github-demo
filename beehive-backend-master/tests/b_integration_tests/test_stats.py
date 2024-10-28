import time
from unittest.mock import Mock, patch

from src.models.honeycomb import Honeycomb
from src.models.task import TaskType
from src.models.user import User
from src.utils.db import db


def test_stats_completed_work_endpoint_no_jwt(app):
    # post stats requires jwt
    res = app.test_client().get('api/v1/stats/work/completed')
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}


def test_stats_completed_work_endpoint_bad_jwt(app, active_token):
    # get stats requires jwt with admin flag
    res = app.test_client().get(
        'api/v1/stats/work/completed',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}


def test_stats_completed_work_endpoint_bad_params(app, admin_token):
    # get stats returns 400 if results_per_page and page are not supplied
    res = app.test_client().get(
        'api/v1/stats/work/completed',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert res.status_code == 400
    assert res.json['status'] == 'error'
    assert res.json['error'] == 'malformed_request'


@patch('src.resources.work.dispatch_cuckoo_event', new=Mock())
@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
@patch('src.resources.work.run_beehave_pr_github_bot', new=Mock())
def test_stats_completed_work_endpoint(
    app, active_token, admin_token, inner_token, active_token_user_id
):
    # get stats might return any data at this point since this test is not the first to run
    res = app.test_client().get(
        'api/v1/stats/work/completed',
        headers={'Authorization': f'Bearer {admin_token}'},
        query_string={'resultsPerPage': 25, 'page': 1}
    )
    assert res.status_code == 200
    assert res.json['data']['page'] == 1
    assert 'totalCount' in res.json['data']
    assert 'work' in res.json['data']

    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create task
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
    test_stats_completed_work_endpoint.task_ids = [task_id]

    # get stats should not return the task since it was not completed
    res = app.test_client().get(
        'api/v1/stats/work/completed',
        headers={'Authorization': f'Bearer {admin_token}'},
        query_string={'resultsPerPage': 25, 'page': 1}
    )
    assert res.status_code == 200
    assert len(list(filter(lambda w: w['taskId'] == task_id, res.json['data']['work']))) == 0

    # get work for task
    res = app.test_client().get(
        f'api/v1/backoffice/task/{task_id}/work',
        headers={'X-BEE-AUTH': inner_token}
    )
    assert res.status_code == 200

    work_id = res.json['data'][0]['id']

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
        json={'workId': work_id, 'durationSeconds': 10, 'solutionUrl': 'https://github.com/my-org/my-repo/pull/1'}
    )
    assert res.status_code == 200

    # get stats should now return the task since it is solved
    res = app.test_client().get(
        'api/v1/stats/work/completed',
        headers={'Authorization': f'Bearer {admin_token}'},
        query_string={'resultsPerPage': 25, 'page': 1}
    )
    assert res.status_code == 200
    completed_tasks = list(filter(lambda w: w['taskId'] == task_id, res.json['data']['work']))
    assert len(completed_tasks) == 1
    assert completed_tasks[0]['workRecordsCount'] == 1
    assert completed_tasks[0]['workRecordsTotalDurationSeconds'] == 10
    assert completed_tasks[0]['workerId'] == active_token_user_id


@patch('src.resources.work.dispatch_cuckoo_event', new=Mock())
@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
@patch('src.resources.work.run_beehave_pr_github_bot', new=Mock())
def test_stats_completed_work_endpoint_multiple_work_records(
    app, active_token, second_active_token, admin_token, inner_token, active_token_user_id
):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create task
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
    test_stats_completed_work_endpoint_multiple_work_records.task_ids = [task_id]

    # get stats should not return the task since it was not completed
    res = app.test_client().get(
        'api/v1/stats/work/completed',
        headers={'Authorization': f'Bearer {admin_token}'},
        query_string={'resultsPerPage': 25, 'page': 1}
    )
    assert res.status_code == 200
    assert len(list(filter(lambda w: w['taskId'] == task_id, res.json['data']['work']))) == 0

    # get work for task
    res = app.test_client().get(
        f'api/v1/backoffice/task/{task_id}/work',
        headers={'X-BEE-AUTH': inner_token}
    )
    assert res.status_code == 200

    work_id = res.json['data'][0]['id']

    # start work on work item using the second user
    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work_id, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200

    # cancel work
    res = app.test_client().post(
        f'api/v1/work/finish',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work_id, 'durationSeconds': 10}
    )
    assert res.status_code == 200

    # start work on work item again using the second user
    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work_id, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200

    # cancel work again
    res = app.test_client().post(
        f'api/v1/work/finish',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work_id, 'durationSeconds': 10}
    )
    assert res.status_code == 200
    
    # get stats should still not return the task since it was still not completed
    res = app.test_client().get(
        'api/v1/stats/work/completed',
        headers={'Authorization': f'Bearer {admin_token}'},
        query_string={'resultsPerPage': 25, 'page': 1}
    )
    assert res.status_code == 200
    assert len(list(filter(lambda w: w['taskId'] == task_id, res.json['data']['work']))) == 0

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
        json={'workId': work_id, 'durationSeconds': 10, 'solutionUrl': 'https://github.com/my-org/my-repo/pull/1'}
    )
    assert res.status_code == 200

    # get stats should now return the task since it is solved
    res = app.test_client().get(
        'api/v1/stats/work/completed',
        headers={'Authorization': f'Bearer {admin_token}'},
        query_string={'resultsPerPage': 25, 'page': 1}
    )
    assert res.status_code == 200
    completed_tasks = list(filter(lambda w: w['taskId'] == task_id, res.json['data']['work']))
    assert len(completed_tasks) == 1
    assert completed_tasks[0]['workRecordsCount'] == 3
    assert completed_tasks[0]['workRecordsTotalDurationSeconds'] == 30
    assert completed_tasks[0]['workerId'] == active_token_user_id


@patch('src.resources.work.dispatch_cuckoo_event', new=Mock())
@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
@patch('src.resources.work.run_beehave_pr_github_bot', new=Mock())
def test_stats_completed_work_endpoint_different_users(
    app, second_active_token, admin_token, inner_token, active_token_user_id, second_active_token_user_id
):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create task
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
    test_stats_completed_work_endpoint_different_users.task_ids = [task_id]

    # get work for task
    res = app.test_client().get(
        f'api/v1/backoffice/task/{task_id}/work',
        headers={'X-BEE-AUTH': inner_token}
    )
    assert res.status_code == 200

    work_id = res.json['data'][0]['id']

    # start work on work item
    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work_id, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200

    # finish work with some solution code
    res = app.test_client().post(
        f'api/v1/work/finish',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work_id, 'durationSeconds': 10, 'solutionUrl': 'https://github.com/my-org/my-repo/pull/1'}
    )
    assert res.status_code == 200

    # get stats should return the task since it is solved
    res = app.test_client().get(
        'api/v1/stats/work/completed',
        headers={'Authorization': f'Bearer {admin_token}'},
        query_string={'resultsPerPage': 25, 'page': 1}
    )
    assert res.status_code == 200
    completed_tasks = list(filter(lambda w: w['taskId'] == task_id, res.json['data']['work']))
    assert len(completed_tasks) == 1
    assert completed_tasks[0]['task']['delegatingUserId'] == active_token_user_id
    assert completed_tasks[0]['workerId'] == second_active_token_user_id


def test_stats_user_endpoint_no_jwt(app):
    # post stats requires jwt
    res = app.test_client().get('api/v1/stats/user')
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}


def test_stats_user_endpoint_bad_jwt(app, active_token):
    # get stats requires jwt with admin flag
    res = app.test_client().get(
        'api/v1/stats/user',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}


def test_stats_user_endpoint_bad_params(app, admin_token):
    # get stats returns 400 if results_per_page and page are not supplied
    res = app.test_client().get(
        'api/v1/stats/user',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert res.status_code == 400
    assert res.json['status'] == 'error'
    assert res.json['error'] == 'malformed_request'


def test_stats_user_endpoint(app, admin_token, active_token_user_id):
    res = app.test_client().get(
        'api/v1/stats/user',
        headers={'Authorization': f'Bearer {admin_token}'},
        query_string={'resultsPerPage': 100, 'page': 1}
    )
    
    assert res.status_code == 200
    assert res.json['data']['page'] == 1
    assert 'totalCount' in res.json['data']
    assert 'users' in res.json['data']
    assert len(list(filter(lambda w: w['userId'] == active_token_user_id, res.json['data']['users']))) == 1


def test_stats_honeycomb_endpoint_no_jwt(app):
    # post stats requires jwt
    res = app.test_client().get('api/v1/stats/honeycomb')
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}


def test_stats_honeycomb_endpoint_bad_jwt(app, active_token):
    # get stats requires jwt with admin flag
    res = app.test_client().get(
        'api/v1/stats/honeycomb',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}


def test_stats_honeycomb_endpoint_bad_params(app, admin_token):
    # get stats returns 400 if results_per_page and page are not supplied
    res = app.test_client().get(
        'api/v1/stats/honeycomb',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert res.status_code == 400
    assert res.json['status'] == 'error'
    assert res.json['error'] == 'malformed_request'


def test_stats_honeycomb_endpoint(app, admin_token):
    with app.app_context():
        # create two honeycombs
        honeycomb_1 = Honeycomb(
            name='honeycomb 1',
            description='description of honeycomb 1',
            version=1,
            code={'file.py': 'code'},
            honeycomb_dependencies=[]
        )
        db.session.add(honeycomb_1)
        db.session.commit()

        honeycomb_2 = Honeycomb(
            name='honeycomb 2',
            description='description of honeycomb 2',
            version=2,
            code={'file.py': 'code'},
            honeycomb_dependencies=[honeycomb_1]
        )
        db.session.add(honeycomb_2)
        db.session.commit()

    res = app.test_client().get(
        'api/v1/stats/honeycomb',
        headers={'Authorization': f'Bearer {admin_token}'},
        query_string={'resultsPerPage': 100, 'page': 1}
    )

    assert res.status_code == 200
    assert res.json['data']['page'] == 1
    assert 'totalCount' in res.json['data']
    assert 'honeycombs' in res.json['data']
    assert len(res.json['data']['honeycombs']) > 0
    stats_honeycomb_1 = list(filter(lambda h: h['id'] == honeycomb_1.id, res.json['data']['honeycombs']))
    assert len(stats_honeycomb_1) == 1
    assert stats_honeycomb_1[0]['name'] == 'honeycomb 1'
    assert stats_honeycomb_1[0]['description'] == 'description of honeycomb 1'
    assert stats_honeycomb_1[0]['version'] == 1
    assert stats_honeycomb_1[0]['code'] == {'file.py': 'code'}
    assert stats_honeycomb_1[0]['honeycombDependencyNames'] == []
    stats_honeycomb_2 = list(filter(lambda h: h['id'] == honeycomb_2.id, res.json['data']['honeycombs']))
    assert len(stats_honeycomb_2) == 1
    assert stats_honeycomb_2[0]['name'] == 'honeycomb 2'
    assert stats_honeycomb_2[0]['description'] == 'description of honeycomb 2'
    assert stats_honeycomb_2[0]['version'] == 2
    assert stats_honeycomb_2[0]['code'] == {'file.py': 'code'}
    assert stats_honeycomb_2[0]['honeycombDependencyNames'] == ['honeycomb 1']

    with app.app_context():
        db.session.delete(honeycomb_2)
        db.session.delete(honeycomb_1)


@patch('src.resources.stats.dispatch_cuckoo_event', return_value=True)
@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
def test_stats_reserve_work_endpoint(
    mock_dispatch_cuckoo_event, app, active_token, admin_token, inner_token, active_token_user_id, second_active_token, second_active_token_user_id
):
    tag = 'project:random'

    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create task
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'Test reservation to contributor task',
            'userName': trello_user,
            'tags': [tag],
            'skills': ['Python']
        }
    )
    assert res.status_code == 200
    task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_stats_reserve_work_endpoint.task_ids = [task_id]

    # tag both users to this project
    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'tags': [tag]
        }
    )
    assert res.status_code == 200
    
    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{second_active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'tags': [tag]
        }
    )
    assert res.status_code == 200

    # get pending work items should return this task unreserved
    res = app.test_client().get(
        'api/v1/stats/work/pending',
        headers={'Authorization': f'Bearer {admin_token}'},
        query_string={'resultsPerPage': 25, 'page': 1}
    )
    assert res.status_code == 200
    assert res.json['data']['page'] == 1
    assert 'totalCount' in res.json['data']
    assert 'work' in res.json['data']
    work = [w for w in res.json['data']['work'] if w['taskId'] == task_id]
    assert len(work) == 1
    work_id = work[0]['id']
    assert work[0]['reservedWorkerId'] is None

    # reserve work for second user for 48 hours
    hours_reserved = 48
    epoch_expected_reserved = int(time.time() * 1000) + hours_reserved * 60 * 60 * 1000
    res = app.test_client().post(
        f'api/v1/stats/work/{work_id}/reserve/{second_active_token_user_id}',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'hoursReserved': hours_reserved
        }
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 1
    assert res.json['data']['reservedWorkerId'] == second_active_token_user_id
    assert epoch_expected_reserved - res.json['data']['reservedUntilEpochMs'] < 50

    # get available work for first user should not return this task since its reserved for second
    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 404

    # get available work for second user should return this task
    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id

    # dismiss reservation from first user should fail since it's not reserved to her
    res = app.test_client().delete(
        f'api/v1/stats/work/{work_id}/reserve/{active_token_user_id}',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert res.status_code == 404
    assert mock_dispatch_cuckoo_event.call_count == 1

    # dismiss reservation from second user should succeed
    res = app.test_client().delete(
        f'api/v1/stats/work/{work_id}/reserve/{second_active_token_user_id}',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 2
    
    # get available work for first user should now show this task
    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id


@patch('src.resources.stats.dispatch_cuckoo_event', return_value=True)
@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
def test_stats_prohibit_work_endpoint(
    mock_dispatch_cuckoo_event, app, active_token, admin_token, inner_token, active_token_user_id, second_active_token, second_active_token_user_id
):
    tag = 'project:random'

    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create task
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'Test Prohibition to contributor task',
            'userName': trello_user,
            'tags': [tag],
            'skills': ['React']
        }
    )
    assert res.status_code == 200
    task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_stats_reserve_work_endpoint.task_ids = [task_id]

    # tag both users to this project
    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'tags': [tag]
        }
    )
    assert res.status_code == 200
    
    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{second_active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'tags': [tag]
        }
    )
    assert res.status_code == 200

    # get pending work items should return this task unprohibited
    res = app.test_client().get(
        'api/v1/stats/work/pending',
        headers={'Authorization': f'Bearer {admin_token}'},
        query_string={'resultsPerPage': 25, 'page': 1}
    )
    assert res.status_code == 200
    assert res.json['data']['page'] == 1
    assert 'totalCount' in res.json['data']
    assert 'work' in res.json['data']
    work = [w for w in res.json['data']['work'] if w['taskId'] == task_id]
    assert len(work) == 1
    work_id = work[0]['id']
    assert work[0]['reservedWorkerId'] is None

    # prohibit work for second user
    res = app.test_client().get(
        f'api/v1/stats/work/{work_id}/prohibit/{second_active_token_user_id}',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 1
    assert res.json['data']['prohibitedWorkerId'] == second_active_token_user_id

    # get available work for first user should return this task since its unprohibited for him
    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id

    # get available work for second user should not return this task as it's prohibited
    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 404

    # dismiss prohibition from first user should fail since it's not prohibited to her
    res = app.test_client().delete(
        f'api/v1/stats/work/{work_id}/prohibit/{active_token_user_id}',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert res.status_code == 404
    assert mock_dispatch_cuckoo_event.call_count == 1

    # dismiss prohibition from second user should succeed
    res = app.test_client().delete(
        f'api/v1/stats/work/{work_id}/prohibit/{second_active_token_user_id}',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 2
    
    # get available work for second user should now show this task
    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
