
from src.models.quest import QuestType
from src.models.task import TaskType
from unittest.mock import patch


def test_template_crud(app, active_token, delegation):
    with app.app_context():

        repoId = delegation[1].id
        res = app.test_client().post(
            'api/v1/delegation/template',
            headers={'Authorization': f'Bearer {active_token}'},
            json={
                'name': 'test title',
                'taskDescription': 'test description',
                'taskType': TaskType.UPDATE_FUNCTION,
                'taskClassification': 'Uncertain',
                'skills': ['test-skill', 'also this'],
                'repositoryId': repoId,
            }
        )
        assert res.status_code == 200
        template_id = res.json['id']

        res = app.test_client().put(
            'api/v1/delegation/template',
            headers={'Authorization': f'Bearer {active_token}'},
            json={
                'templateId': template_id,
                'name': 'test title updated',
                'taskDescription': 'test description updated',
                'taskClassification': 'Uncertain',
                'skills': ['test-skill', 'another-skill', 'third-skill'],
                'repositoryId': repoId,
            }
        )
        assert res.status_code == 200

        res = app.test_client().delete(
            f'api/v1/delegation/template/{template_id}',
            headers={'Authorization': f'Bearer {active_token}'},
        )
        assert res.status_code == 200
    

def test_delegation_delegator_repositories(app, active_token, delegation):
    with app.app_context():
        res = app.test_client().get('api/v1/delegation/repositories', headers={'Authorization': f'Bearer {active_token}'})
        assert res.status_code == 200
        repos = res.json['repositories']
        assert len(repos) == 1
        assert repos[0]['url'] == delegation[1].url

def test_delegation_get_repo_templates(app, active_token, delegation):
    with app.app_context():
        res = app.test_client().get(f'api/v1/delegation/templates', headers={'Authorization': f'Bearer {active_token}'})
        assert res.status_code == 200
        templates = res.json['templates']
        assert len(templates) == 1
        assert templates[0]['name'] == delegation[2].name

@patch('src.resources.delegation.dispatch_cuckoo_event', return_value=True)
def test_delegation_delegate_task(mock_dispatch_cuckoo_event, app, active_token, delegation):

    # get the repo to delegate to, and some task template to create from
    with app.app_context():
        res = app.test_client().get('api/v1/delegation/repositories', headers={'Authorization': f'Bearer {active_token}'})
        repos = res.json['repositories']
        repoId = repos[0]['id']
        res = app.test_client().get(f'api/v1/delegation/templates', headers={'Authorization': f'Bearer {active_token}'})
        template = res.json['templates'][0]

    # post valid task
    res = app.test_client().post(
        'api/v1/task/delegate',
        headers={'Authorization': f'Bearer {active_token}'},
        json={
            'description': template['taskDescription'],
            'title': template['name'],
            'priority': 3,
            'type': TaskType.CREATE_FUNCTION,
            'taskClassification': 'Modify/fix a page/screen',
            'tags': ['test-tag'],
            'skills': template['skills'],
            'delegationTimeSeconds': 1000,
            'repositoryId': repoId,
        }
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 1
    task_id = res.json['data']['id']
    

    # set task ids so the fixture teardown can delete them
    test_delegation_delegate_task.task_ids = [task_id]

    # post was successful and the task is saved
    res = app.test_client().get(
        f'api/v1/task/{task_id}',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['title'] == template['name']
    assert res.json['data']['priority'] == 3
    assert 'test-skill' in res.json['data']['skills']
    assert 'project:test_project' in res.json['data']['tags']


@patch('src.resources.delegation.dispatch_cuckoo_event', return_value=True)
def test_delegation_delegate_quest(mock_dispatch_cuckoo_event, app, active_token, delegation):

    description = 'test quest description'
    title = 'test quest title'
    success_criteria = [{
        'title': 'success criteria title',
        'description': 'success criteria description',
        'explanation': 'success criteria explanation'
    }]
    # post valid quest
    res = app.test_client().post(
        'api/v1/quest/delegate',
        headers={'Authorization': f'Bearer {active_token}'},
        json={
            'description': description,
            'title': title,
            'projectId': delegation[0].id,
            'questType': QuestType.FEATURE,
            'successCriteria': success_criteria,
            'delegationTimeSeconds': 1000
        }
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 1
    quest_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_delegation_delegate_quest.quest_ids = [quest_id]

    # post was successful and the task is saved
    res = app.test_client().get(
        f'api/v1/quest/{quest_id}',
        headers={'Authorization': f'Bearer {active_token}'}
    )

    assert res.status_code == 200
    assert res.json['data']['title'] == title
    assert res.json['data']['description'] == description
    assert res.json['data']['successCriteria'][0]['title'] == success_criteria[0]['title']
    assert res.json['data']['successCriteria'][0]['description'] == success_criteria[0]['description']
    assert res.json['data']['successCriteria'][0]['explanation'] == success_criteria[0]['explanation']

