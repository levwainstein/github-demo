from unittest.mock import Mock, patch

from src.models.task import TaskType


@patch('src.resources.delegation.dispatch_cuckoo_event', new=Mock())
def test_task_context_crud(app, active_token, delegation):
    with app.app_context():
        # post valid task
        res = app.test_client().post(
            'api/v1/task/delegate',
            headers={'Authorization': f'Bearer {active_token}'},
            json={
                'description': 'test-desc',
                'title': 'test-title',
                'priority': 3,
                'type': TaskType.CREATE_FUNCTION,
                'taskClassification': 'Modify/fix a page/screen',
                'tags': ['test-tag'],
                'skills': ['React'],
                'delegationTimeSeconds': 1000,
                'repositoryId': delegation[1].id,
            }
        )
        assert res.status_code == 200
        task_id = res.json['data']['id']
        # set task ids so the fixture teardown can delete them
        test_task_context_crud.task_ids = [task_id]

        # post a new context
        res = app.test_client().post(
            f'api/v1/task/{task_id}/context',
            headers={'Authorization': f'Bearer {active_token}'},
            json={
                'file': 'file test',
                'entity': 'entity test', 
                'potentialUse': 'potentialUse test'
            }
        )
        assert res.status_code == 200

        #get existing context
        res = app.test_client().get(
            f'api/v1/task/{task_id}/context',
            headers={'Authorization': f'Bearer {active_token}'}
        )
        assert res.status_code == 200
        assert res.json['data'][0]['entity'] == 'entity test'

        context_id = res.json['data'][0]['id']

        # post a new context
        res = app.test_client().put(
            f'api/v1/task/{task_id}/context/{context_id}',
            headers={'Authorization': f'Bearer {active_token}'},
            json={
                'file': 'file test',
                'entity': 'entity test 2', 
                'potentialUse': 'potentialUse test'
            }
        )
        assert res.status_code == 200

        # verify updates
        res = app.test_client().get(
            f'api/v1/task/{task_id}/context',
            headers={'Authorization': f'Bearer {active_token}'}
        )
        assert res.status_code == 200
        assert res.json['data'][0]['entity'] == 'entity test 2'

        # delete context
        res = app.test_client().delete(
            f'api/v1/task/{task_id}/context/{context_id}',
            headers={'Authorization': f'Bearer {active_token}'}
        )
        assert res.status_code == 200

