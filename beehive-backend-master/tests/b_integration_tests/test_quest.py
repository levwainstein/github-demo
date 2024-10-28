from src.models.quest import QuestStatus, QuestType
from src.models.user import User


def test_quest_post_endpoint_no_token(app, active_token):
    # post quest requires an inner token
    res = app.test_client().post('api/v1/quest')
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}

    # post quest requires an inner token
    res = app.test_client().post(
        'api/v1/quest',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}


def test_quest_post_endpoint_bad_request(app, active_token_user_id, inner_token):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # post partial params quest
    res = app.test_client().post(
        'api/v1/quest',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'Test quest description',
            'userName': trello_user,
            'questType': QuestType.FEATURE.name
        }
    )
    assert res.status_code == 400
    assert res.json.get('status') == 'error'
    assert res.json.get('error') == 'malformed_request'

def test_quest_post_endpoint_no_project(app, active_token, active_token_user_id, inner_token):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # post valid quest
    res = app.test_client().post(
        'api/v1/quest',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'title': 'Test quest',
            'description': 'Test description',
            'userName': trello_user,
            'questType': QuestType.FEATURE.name
        }
    )
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}


def test_quest_post_endpoint_valid_task(app, active_token, active_token_user_id, inner_token, delegation):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # post valid quest with repo name
    repo_name = delegation[1].name
    res = app.test_client().post(
        'api/v1/quest',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'title': 'Test feature quest',
            'description': 'Test feature description',
            'userName': trello_user,
            'questType': QuestType.FEATURE.name,
            'repositoryName': repo_name
        }
    )
    assert res.status_code == 200

    quest_id = res.json['data']['id']

    # set quest ids so the fixture teardown can delete them
    test_quest_post_endpoint_valid_task.quest_ids = [quest_id]

    # post was successful and the quest is saved with new status
    res = app.test_client().get(
        f'api/v1/quest/{quest_id}',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['status'] == QuestStatus.NEW
    assert res.json['data']['questType'] == QuestType.FEATURE

    # post valid quest with trello board url
    trello_board_url = delegation[0].trello_link
    res = app.test_client().post(
        'api/v1/quest',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'title': 'Test bug quest',
            'description': 'Test bug description',
            'userName': trello_user,
            'questType': QuestType.BUG.name,
            'trelloUrl': trello_board_url
        }
    )
    assert res.status_code == 200

    quest_id2 = res.json['data']['id']

    # set quest ids so the fixture teardown can delete them
    test_quest_post_endpoint_valid_task.quest_ids.append(quest_id2)

    # post was successful and the quest is saved with new status
    res = app.test_client().get(
        f'api/v1/quest/{quest_id2}',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['status'] == QuestStatus.NEW
    assert res.json['data']['questType'] == QuestType.BUG


def test_quest_put_endpoint_non_existing_quest(app, active_token_user_id, inner_token):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # put non-existing quest id
    res = app.test_client().put(
        'api/v1/quest',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'questId': 'Non existing',
            'userName': trello_user,
        }
    )
    assert res.status_code == 404


def test_quest_put_endpoint_valid_params(app, active_token, active_token_user_id, inner_token, delegation):
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    trello_board_url = delegation[0].trello_link
    # post valid quest
    res = app.test_client().post(
        'api/v1/quest',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'title': 'Test quest',
            'description': 'initial description',
            'userName': trello_user,
            'questType': QuestType.FEATURE.name,
            'trelloUrl': trello_board_url
        }
    )
    assert res.status_code == 200

    quest_id = res.json['data']['id']

    # set quest ids so the fixture teardown can delete them
    test_quest_put_endpoint_valid_params.quest_ids = [quest_id]

    # post was successful and the quest is saved
    res = app.test_client().get(
        f'api/v1/quest/{quest_id}',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['description'] == 'initial description'
    assert res.json['data']['status'] == QuestStatus.NEW
    assert res.json['data']['questType'] == QuestType.FEATURE
    assert res.json['data']['title'] == 'Test quest'

    # update quest description
    res = app.test_client().put(
        f'api/v1/quest',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'questId': quest_id,
            'userName': trello_user,
            'description': 'new description'
        }
    )
    assert res.status_code == 200

    # update quest tasks with non existing task
    res = app.test_client().put(
        f'api/v1/quest',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'questId': quest_id,
            'userName': trello_user,
            'taskIds': ['test-task-id']
        }
    )
    assert res.status_code == 404

    # post the sub task object
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'sub task description',
            'userName': trello_user
        }
    )
    assert res.status_code == 200
    task_id = res.json['data']['id']

    # update quest tasks with existing task
    res = app.test_client().put(
        f'api/v1/quest',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'questId': quest_id,
            'userName': trello_user,
            'taskIds': [task_id]
        }
    )
    assert res.status_code == 200
    assert res.json['data']['description'] == 'new description'
    assert res.json['data']['tasks'][0]['id'] == task_id

    # update quest links
    res = app.test_client().put(
        f'api/v1/quest',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'questId': quest_id,
            'userName': trello_user,
            'links': {'test-link1': 'test-link-url1', 'test-link2': 'test-link-url2'}
        }
    )
    assert res.status_code == 200
    assert res.json['data']['description'] == 'new description'
    assert res.json['data']['links'] == {'test-link1': 'test-link-url1', 'test-link2': 'test-link-url2'}

    # update quest status
    res = app.test_client().put(
        f'api/v1/quest',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'questId': quest_id,
            'userName': trello_user,
            'status': QuestStatus.IN_PROCESS.name
        }
    )
    assert res.status_code == 200

    # quest fields should now be updated
    res = app.test_client().get(
        f'api/v1/quest/{quest_id}',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['description'] == 'new description'
    assert res.json['data']['status'] == QuestStatus.IN_PROCESS
    assert res.json['data']['links'] == {'test-link1': 'test-link-url1', 'test-link2': 'test-link-url2'}
    assert res.json['data']['tasks'][0]['id'] == task_id

    # make sure that the task's quest id is updated as well
    res = app.test_client().get(
        f'api/v1/task/{task_id}',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['description'] == 'sub task description'
    assert res.json['data']['questId'] == quest_id
