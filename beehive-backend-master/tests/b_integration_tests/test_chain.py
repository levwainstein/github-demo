import time
from unittest.mock import Mock, patch

from bh_grpc.generated.beehive.robobee.v1.github_pb2 import GetPRInfoRequest, GetPRInfoResponse, PRBranch

from src.models.task import ReviewStatus, Task, TaskStatus
from src.models.user import User
from src.models.work import Work, WorkType
from src.models.work_record import WorkRecord
from src.utils.grpc_client import GRPCClient


@patch('src.resources.work.dispatch_cuckoo_event', return_value=True)
@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
@patch('src.resources.work.grpc_client')
@patch('src.resources.work.run_beehave_pr_github_bot', new=Mock())
def test_chain_qa_and_adequate_review(mock_grpc_client, mock_dispatch_cuckoo_event, app, active_token, active_token_user_id, second_active_token, second_active_token_user_id, inner_token):
    task_coding_description = 'description for coding task'
    task_qa_description = 'description for qa chained task'

    tag = 'random-repo'
    qa_skill = 'qa_tasks'

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
        user = User.query.filter_by(id=active_token_user_id).first()
    trello_user = user.trello_user

    # create task
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': task_coding_description,
            'userName': trello_user,
            'tags': [tag],
            'skills': ['Python'],
            'chainReview': True,
            'chainDescription': task_qa_description
        }
    )
    assert res.status_code == 200

    task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_chain_qa_and_adequate_review.task_ids = [task_id]

    # post was successful and the task is saved with pending status
    res = app.test_client().get(
        f'api/v1/task/{task_id}',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['status'] == TaskStatus.PENDING

    # update user tags so work comes up in available work
    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            "tags": [tag]
        }
    )
    assert res.status_code == 200

    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{second_active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            "skills": [qa_skill],
            "tags": [tag]
        }
    )
    assert res.status_code == 200

    # get available work returns a single work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    assert res.json['data']['work']['workType'] == WorkType.CUCKOO_CODING
    assert res.json['data']['work']['description'] == task_coding_description
    assert mock_dispatch_cuckoo_event.call_count == 0

    work_id_1 = res.json['data']['work']['id']
    
    # assert pr info isn't requested in first iteration
    assert len(mock_grpc_client.github_stub.method_calls) == 0

    # there are no other available work items
    res = app.test_client().get(
        'api/v1/work/available',
        headers={'Authorization': f'Bearer {active_token}'},
        query_string={'currentWorkId': work_id_1}
    )
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}

    # assert pr info isn't requested in first iteration
    assert len(mock_grpc_client.github_stub.method_calls) == 0

    # start work on work item
    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work_id_1, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 1

    solution_url = 'https://github.com/my-org/my-repo/pull/1'

    # finish work with some solution url
    res = app.test_client().post(
        f'api/v1/work/finish',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work_id_1, 'durationSeconds': 20, 'solutionUrl': solution_url}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 2

    # since we chained more work even though we finished the task should still be in process
    res = app.test_client().get(
        f'api/v1/task/{task_id}',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['status'] == TaskStatus.IN_PROCESS
    assert mock_dispatch_cuckoo_event.call_count == 2

    # get available work should now return a qa work item derived from the same task
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    assert res.json['data']['work']['workType'] == WorkType.CUCKOO_QA
    assert res.json['data']['work']['description'] == f'{task_qa_description}\n\n---\n\n**Original Task:**\n{task_coding_description}'
    assert mock_dispatch_cuckoo_event.call_count == 2

    work_id_2 = res.json['data']['work']['id']

    assert work_id_1 != work_id_2

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

    # there are no other available work items
    res = app.test_client().get(
        'api/v1/work/available',
        headers={'Authorization': f'Bearer {second_active_token}'},
        query_string={'currentWorkId': work_id_2}
    )
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}
    assert mock_dispatch_cuckoo_event.call_count == 2
    assert mock_grpc_client.github_stub.GetPRInfo.call_count == 1

    # start work on qa work item
    res = app.test_client().post(
        'api/v1/work/start',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work_id_2, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 3

    # finish review work with some review
    res = app.test_client().post(
        'api/v1/work/finish',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work_id_2, 'durationSeconds': 10, 'reviewStatus': ReviewStatus.ADEQUATE, 'reviewFeedback': 'this is review'}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 4

    # no other work items are available
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}
    assert mock_dispatch_cuckoo_event.call_count == 4
    assert mock_grpc_client.github_stub.GetPRInfo.call_count == 1

    # task should now be solved and have the review feedback and status
    res = app.test_client().get(
        f'api/v1/task/{task_id}',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['status'] == TaskStatus.SOLVED
    assert res.json['data']['reviewFeedback'] == 'this is review'
    assert res.json['data']['reviewStatus'] == ReviewStatus.ADEQUATE
    assert mock_dispatch_cuckoo_event.call_count == 4


@patch('src.resources.work.dispatch_cuckoo_event', return_value=True)
@patch('src.jobs.task.get_task_type_classification')
@patch('src.models.work_record.WorkRecord.get_ratings', return_value={'id':1,'user':'user','object_key':'o','subject':'s','score':5.0,'text':'text'})
@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
@patch('src.resources.work.grpc_client')
@patch('src.resources.work.run_beehave_pr_github_bot', new=Mock())
def test_chain_qa_and_inadequate_review(mock_grpc_client, mock_work_record_get_ratings, mock_get_task_type_classification, mock_dispatch_cuckoo_event, app, active_token, active_token_user_id, second_active_token, second_active_token_user_id, inner_token, delegation):
    task_coding_description = 'description for faulty coding task'
    task_qa_description = 'description for qa chained task'

    tag = f'project:{delegation[0].name}'
    qa_skill = 'qa_tasks'
    
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
        user = User.query.filter_by(id=active_token_user_id).first()
        trello_user = user.trello_user

    # create task with max 2 qa iterations
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': task_coding_description,
            'userName': trello_user,
            'tags': [tag],
            'chainReview': True,
            'maxChainIterations': 2,
            'chainDescription': task_qa_description
        }
    )
    assert res.status_code == 200

    task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_chain_qa_and_inadequate_review.task_ids = [task_id]

    # post was successful and the task is saved with pending status
    res = app.test_client().get(
        f'api/v1/task/{task_id}',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['status'] == TaskStatus.PENDING
    assert mock_get_task_type_classification.call_count == 1
    assert mock_work_record_get_ratings.call_count == 0

    # update developer user tags so work comes up in available work
    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{second_active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            "tags": [tag]
        }
    )
    assert res.status_code == 200

    # get available work returns a single work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    assert res.json['data']['work']['workType'] == WorkType.CUCKOO_CODING
    assert res.json['data']['work']['description'] == task_coding_description
    assert mock_dispatch_cuckoo_event.call_count == 0
    assert mock_grpc_client.github_stub.GetPRInfo.call_count == 0

    work_id_1 = res.json['data']['work']['id']

    # start coding work on work item
    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work_id_1, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 1
    assert mock_work_record_get_ratings.call_count == 0

    solution_url = 'https://github.com/my-org/my-repo/pull/1'

    # finish coding work with some solution url
    res = app.test_client().post(
        f'api/v1/work/finish',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work_id_1, 'durationSeconds': 20, 'solutionUrl': solution_url}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 2
    assert mock_work_record_get_ratings.call_count == 0

    # since we chained more work even though we finished the task should still be in process
    res = app.test_client().get(
        f'api/v1/task/{task_id}',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['status'] == TaskStatus.IN_PROCESS
    assert mock_dispatch_cuckoo_event.call_count == 2
    assert mock_work_record_get_ratings.call_count == 0

    # update qa user tags so work comes up in available work
    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            "skills": [qa_skill],
            "tags": [tag]
        }
    )
    assert res.status_code == 200

    # get available work should now return a qa work item derived from the same task
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    assert res.json['data']['work']['workType'] == WorkType.CUCKOO_QA
    assert res.json['data']['work']['description'] == f'{task_qa_description}\n\n---\n\n**Original Task:**\n{task_coding_description}'
    assert mock_dispatch_cuckoo_event.call_count == 2
    assert mock_work_record_get_ratings.call_count == 0

    work_id_2 = res.json['data']['work']['id']
    assert work_id_2 != work_id_1
    
    # assert pull request data is fetched from robobee and exists in available work response
    assert len(mock_grpc_client.github_stub.method_calls) > 0
    assert mock_grpc_client.github_stub.GetPRInfo.call_count == 1
    assert res.json['data']['work']['branchName'] == 'external/cool-user/cool-feature'

    # there are no other available work items for qa
    res = app.test_client().get(
        'api/v1/work/available',
        headers={'Authorization': f'Bearer {active_token}'},
        query_string={'currentWorkId': work_id_2}
    )
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}
    assert mock_dispatch_cuckoo_event.call_count == 2
    assert mock_work_record_get_ratings.call_count == 0

    # start work on qa work item
    res = app.test_client().post(
        'api/v1/work/start',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work_id_2, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 3
    assert mock_work_record_get_ratings.call_count == 0

    # finish qa work with inadequate review
    res = app.test_client().post(
        'api/v1/work/finish',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work_id_2, 'durationSeconds': 10, 'reviewStatus': ReviewStatus.INADEQUATE}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 4
    assert mock_work_record_get_ratings.call_count == 0

    # no other work items are available for qa user
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}
    assert mock_dispatch_cuckoo_event.call_count == 4
    assert mock_work_record_get_ratings.call_count == 0

    # task should now still be in process and have the review updated
    res = app.test_client().get(
        f'api/v1/task/{task_id}',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['status'] == TaskStatus.IN_PROCESS
    assert res.json['data']['reviewStatus'] == ReviewStatus.INADEQUATE
    assert mock_dispatch_cuckoo_event.call_count == 4
    assert mock_work_record_get_ratings.call_count == 0

    # get available work returns a coding work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    assert res.json['data']['work']['workType'] == WorkType.CUCKOO_CODING
    assert mock_dispatch_cuckoo_event.call_count == 4
    assert mock_work_record_get_ratings.call_count == 0
    
    # assert pull request data is fetched from robobee and exists in available work response
    assert len(mock_grpc_client.github_stub.method_calls) > 0
    assert mock_grpc_client.github_stub.GetPRInfo.call_count == 2
    assert res.json['data']['work']['branchName'] == 'external/cool-user/cool-feature'

    work_id_3 = res.json['data']['work']['id']
    assert work_id_3 != work_id_2
    assert work_id_3 != work_id_1

    # start work on second coding work item
    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work_id_3, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 5
    assert mock_work_record_get_ratings.call_count == 0

    # finish second coding work with some solution url
    res = app.test_client().post(
        f'api/v1/work/finish',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work_id_3, 'durationSeconds': 40, 'solutionUrl': solution_url}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 6

    # get available work should return a second qa work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    assert res.json['data']['work']['workType'] == WorkType.CUCKOO_QA
    assert res.json['data']['work']['description'] == f'{task_qa_description}\n\n---\n\n**Original Task:**\n{task_coding_description}'
    assert mock_dispatch_cuckoo_event.call_count == 6
    assert mock_work_record_get_ratings.call_count == 0

    work_id_4 = res.json['data']['work']['id']
    assert work_id_4 != work_id_3
    assert work_id_4 != work_id_2
    assert work_id_4 != work_id_1

    # assert pull request data is fetched from robobee and exists in available work response
    assert len(mock_grpc_client.github_stub.method_calls) > 0
    assert mock_grpc_client.github_stub.GetPRInfo.call_count == 3
    assert res.json['data']['work']['branchName'] == 'external/cool-user/cool-feature'

    # start work on second qa work item
    res = app.test_client().post(
        'api/v1/work/start',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work_id_4, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 7
    assert mock_work_record_get_ratings.call_count == 0

    # finish qa work with inadequate review
    res = app.test_client().post(
        'api/v1/work/finish',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work_id_4, 'durationSeconds': 10, 'reviewStatus': ReviewStatus.INADEQUATE}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event.call_count == 8
    assert mock_work_record_get_ratings.call_count == 0

    # no other work items are available for qa user
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}
    assert mock_dispatch_cuckoo_event.call_count == 8
    assert mock_work_record_get_ratings.call_count == 0

    # task should now be in status solved, although marked inadequate because chain has been exhausted
    res = app.test_client().get(
        f'api/v1/task/{task_id}',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert res.json['data']['status'] == TaskStatus.SOLVED
    assert mock_dispatch_cuckoo_event.call_count == 8
    assert mock_work_record_get_ratings.call_count == 0

    with app.app_context():
        work_record = WorkRecord.query.filter_by(work_id=work_id_4).all()
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

    # work record has updated start of review with correct timestamp but duration of review hasn't been concluded
    with app.app_context():
        reviewed_work_record = WorkRecord.query.filter_by(id=work_record.id).all()
    assert len(reviewed_work_record) == 1
    assert reviewed_work_record[0].active is False
    assert reviewed_work_record[0].review_tz_name == 'UTC'
    assert reviewed_work_record[0].review_start_time_epoch_ms is not None
    assert reviewed_work_record[0].review_duration_seconds is None

    # delegator requests for modifications, should create another chained coding task
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
    assert mock_dispatch_cuckoo_event.call_count == 8
    assert mock_work_record_get_ratings.call_count == 1

    # work record has updated duration
    with app.app_context():
        reviewed_work_record = WorkRecord.query.filter_by(id=work_record.id).all()
    assert len(reviewed_work_record) == 1
    assert reviewed_work_record[0].review_duration_seconds is not None

    # get available now returns the work reserved for original solving contributor
    res = app.test_client().get(
        'api/v1/work/available', 
        headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['workType'] == WorkType.CUCKOO_ITERATION
    assert mock_dispatch_cuckoo_event.call_count == 8
    assert mock_work_record_get_ratings.call_count == 1
    work_id = res.json['data']['work']['id']

    # assert pull request data is fetched from robobee and exists in available work response
    assert len(mock_grpc_client.github_stub.method_calls) > 0
    assert mock_grpc_client.github_stub.GetPRInfo.call_count == 4
    assert res.json['data']['work']['branchName'] == 'external/cool-user/cool-feature'

    with app.app_context():
        work = Work.query.filter_by(id=work_id).all()
    assert len(work) == 1
    assert work[0].reserved_worker_id == second_active_token_user_id

    # verify task has a qa chain similar to original task
    with app.app_context():
        task = Task.query.filter_by(id=task_id).all()
    assert len(task) == 1
    assert task[0].status == TaskStatus.MODIFICATIONS_REQUESTED
    task_advanced_options = task[0].advanced_options
    assert task_advanced_options.get('chainReview') is True
    assert task_advanced_options.get('chainDescription') is not None
    assert task_advanced_options.get('maxChainIterations') == 2
