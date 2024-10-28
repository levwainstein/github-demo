from datetime import datetime, timedelta
import time
from unittest.mock import Mock, patch

import pytest

from src.models.task import Task, TaskStatus, TaskType
from src.models.upwork import WorkRecordUpworkDiary
from src.models.user import User
from src.models.work import Work, WorkStatus, WorkType
from src.models.work_record import WorkOutcome, WorkRecord
from src.schemas.upwork import UpworkDiarySchema
from src.utils.db import db
from src.utils.upwork import UpworkClient


@patch('src.jobs.work.dispatch_cuckoo_event', return_value=True)
@patch('src.resources.work.dispatch_cuckoo_event', return_value=True)
@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
def test_find_deserted_cuckoo_work(mock_dispatch_cuckoo_event_resource, mock_dispatch_cuckoo_event_job, app, active_token, active_token_user_id, second_active_token, inner_token):
    # import here since importing the job requires an initialized flask app
    from src.jobs.work import find_deserted_work

    # execute job to make sure it runs
    with app.app_context():
        find_deserted_work.queue()

    assert mock_dispatch_cuckoo_event_job.call_count == 0

    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create task
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'test cuckoo task',
            'userName': trello_user
        }
    )
    assert res.status_code == 200

    task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_find_deserted_cuckoo_work.task_ids = [task_id]

    # get available work returns the single work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id

    with app.app_context():
        # check work
        work = Work.query.filter_by(task_id=task_id).all()
        assert len(work) == 1
        assert work[0].status == WorkStatus.AVAILABLE
        work_record = WorkRecord.query.filter_by(work_id=work[0].id).all()
        assert len(work_record) == 0
        task = Task.query.filter_by(id=task_id).all()
        assert len(task) == 1
        assert task[0].status == TaskStatus.PENDING

    # job should not change anything
    with app.app_context():
        find_deserted_work.queue()

    assert mock_dispatch_cuckoo_event_job.call_count == 0

    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).all()
        assert len(work) == 1
        assert work[0].status == WorkStatus.AVAILABLE
        work_record = WorkRecord.query.filter_by(work_id=work[0].id).all()
        assert len(work_record) == 0
        task = Task.query.filter_by(id=task_id).all()
        assert len(task) == 1
        assert task[0].status == TaskStatus.PENDING

    # start work
    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work[0].id, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event_resource.call_count == 1

    # get available work for the first user should return the active work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    assert res.json['data']['workRecord']['workId'] == res.json['data']['work']['id']

    # get available work for the second user should return no work
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}

    # job should not change anything
    with app.app_context():
        find_deserted_work.queue()

    assert mock_dispatch_cuckoo_event_job.call_count == 0

    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).all()
        assert len(work) == 1
        assert work[0].status == WorkStatus.UNAVAILABLE
        work_record = WorkRecord.query.filter_by(work_id=work[0].id).all()
        assert len(work_record) == 1
        assert work_record[0].active == True
        assert work_record[0].duration_seconds is None
        task = Task.query.filter_by(id=task_id).all()
        assert len(task) == 1
        assert task[0].status == TaskStatus.IN_PROCESS

    # get available work for the first user should return the active work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    assert res.json['data']['workRecord']['workId'] == res.json['data']['work']['id']

    # get available work for the second user should return no work
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}

    # modify work record to be started three days in the past
    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).first()
        work_record = WorkRecord.query.filter_by(work_id=work.id).first()
        work_record.start_time_epoch_ms = work_record.start_time_epoch_ms - 72 * 60 * 60 * 1000
        db.session.commit()

    # job should finish work record and make work available again
    with app.app_context():
        find_deserted_work.queue()

    assert mock_dispatch_cuckoo_event_job.call_count == 1

    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).all()
        assert len(work) == 1
        assert work[0].status == WorkStatus.AVAILABLE
        work_record = WorkRecord.query.filter_by(work_id=work[0].id).all()
        assert len(work_record) == 1
        assert work_record[0].active == False
        assert work_record[0].duration_seconds is not None
        task = Task.query.filter_by(id=task_id).all()
        assert len(task) == 1
        assert task[0].status == TaskStatus.PENDING

    # the work item is freed and get available work should return it
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id


@patch('src.jobs.work.dispatch_cuckoo_event', return_value=True)
@patch('src.resources.stats.dispatch_cuckoo_event', return_value=True)
@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
def test_find_past_reserved_cuckoo_work(mock_dispatch_cuckoo_event_resource, mock_dispatch_cuckoo_event_job, app, active_token, active_token_user_id, second_active_token, second_active_token_user_id, inner_token, admin_token):
    # import here since importing the job requires an initialized flask app
    from src.jobs.work import find_past_reserved_work

    # execute job to make sure it runs
    with app.app_context():
        find_past_reserved_work.queue()

    assert mock_dispatch_cuckoo_event_job.call_count == 0

    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create task
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'test past reservation cuckoo task',
            'userName': trello_user
        }
    )
    assert res.status_code == 200
    task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_find_past_reserved_cuckoo_work.task_ids = [task_id]

    # get available work returns the single work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id

    # check work
    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).all()
        assert len(work) == 1
        assert work[0].status == WorkStatus.AVAILABLE
        work_record = WorkRecord.query.filter_by(work_id=work[0].id).all()
        assert len(work_record) == 0
        task = Task.query.filter_by(id=task_id).all()
        assert len(task) == 1
        assert task[0].status == TaskStatus.PENDING

    # job should not change anything
    with app.app_context():
        find_past_reserved_work.queue()

    assert mock_dispatch_cuckoo_event_job.call_count == 0

    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).all()
        assert len(work) == 1
        assert work[0].status == WorkStatus.AVAILABLE
        work_record = WorkRecord.query.filter_by(work_id=work[0].id).all()
        assert len(work_record) == 0
        task = Task.query.filter_by(id=task_id).all()
        assert len(task) == 1
        assert task[0].status == TaskStatus.PENDING

    # reserve work to second user
    hours_reserved = 10
    epoch_expected_reserved = int(time.time() * 1000) + hours_reserved * 60 * 60 * 1000
    res = app.test_client().post(
        f'api/v1/stats/work/{work[0].id}/reserve/{second_active_token_user_id}',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'hoursReserved': hours_reserved
        }
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event_resource.call_count == 1

    # verify reservation
    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).all()
        assert len(work) == 1
        assert work[0].status == WorkStatus.AVAILABLE
        assert work[0].reserved_until_epoch_ms - epoch_expected_reserved < 150
        assert work[0].reserved_worker_id == second_active_token_user_id
        work_record = WorkRecord.query.filter_by(work_id=work[0].id).all()
        assert len(work_record) == 0
        task = Task.query.filter_by(id=task_id).all()
        assert len(task) == 1
        assert task[0].status == TaskStatus.PENDING

    # get available work for the second user should return the active work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    assert res.json['data']['work']['id'] == work[0].id

    # get available work for the first user should return no work
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}

    # job should not change anything
    with app.app_context():
        find_past_reserved_work.queue()

    assert mock_dispatch_cuckoo_event_job.call_count == 0

    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).all()
        assert len(work) == 1
        assert work[0].status == WorkStatus.AVAILABLE
        assert work[0].reserved_until_epoch_ms - epoch_expected_reserved < 150
        assert work[0].reserved_worker_id == second_active_token_user_id
        work_record = WorkRecord.query.filter_by(work_id=work[0].id).all()
        assert len(work_record) == 0
        task = Task.query.filter_by(id=task_id).all()
        assert len(task) == 1
        assert task[0].status == TaskStatus.PENDING

    # get available work for the second user should return the active work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    assert res.json['data']['work']['id'] == work[0].id

    # get available work for the first user should return no work
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}

    # modify work record to be reserved until one day in the past
    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).first()
        work.reserved_until_epoch_ms = work.reserved_until_epoch_ms - 24 * 60 * 60 * 1000
        db.session.commit()

    # job should dismiss work reservation and make work available to all contributors
    with app.app_context():
        find_past_reserved_work.queue()

    assert mock_dispatch_cuckoo_event_job.call_count == 1

    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).all()
        assert len(work) == 1
        assert work[0].status == WorkStatus.AVAILABLE
        assert work[0].reserved_until_epoch_ms == None
        assert work[0].reserved_worker_id == None
        work_record = WorkRecord.query.filter_by(work_id=work[0].id).all()
        assert len(work_record) == 0
        task = Task.query.filter_by(id=task_id).all()
        assert len(task) == 1
        assert task[0].status == TaskStatus.PENDING

    # the work item is freed and get available work should return it for first user
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    assert res.json['data']['work']['id'] == work[0].id

    # the work item is freed and get available work should return it for second user too
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    assert res.json['data']['work']['id'] == work[0].id


@patch.object(UpworkClient, 'get_work_diary')
@patch.object(UpworkClient, 'get_organization_id', return_value='nkzlfefsnelbn4opkwhnra')
@patch.object(UpworkClient, 'refresh_token', return_value={"access_token": "oauth2v2_1e3704277095e1a98ba48ea3e2928ab2","refresh_token": "oauth2v2_98a2b87a42e9c68db1236d4fa05f76bb","token_type": "Bearer","expires_in": 86400,"expires_at": "1712730000"})
@patch('src.jobs.work.dispatch_cuckoo_event', new=Mock())
@patch('src.resources.work.dispatch_cuckoo_event', new=Mock())
def test_find_net_duration_work_records(mock_refresh_token, mock_get_organization_id, mock_get_work_diary, app, active_token, active_token_user_id, inner_token):
    # import here since importing the job requires an initialized flask app
    from src.jobs.upwork import find_net_duration_work_records

    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create task
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'test find net duration cuckoo task',
            'userName': trello_user
        }
    )
    assert res.status_code == 200
    task_id = res.json['data']['id']

    # set task ids so the fixture teardown can delete them
    test_find_net_duration_work_records.task_ids = [task_id]

    # check work
    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).all()
        assert len(work) == 1
        assert work[0].status == WorkStatus.AVAILABLE
        work_record = WorkRecord.query.filter_by(work_id=work[0].id).all()
        assert len(work_record) == 0
        task = Task.query.filter_by(id=task_id).all()
        assert len(task) == 1
        assert task[0].status == TaskStatus.PENDING

    # start work
    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work[0].id, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200

    # job should not change anything
    with app.app_context():
        find_net_duration_work_records.queue()

    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).all()
        assert len(work) == 1
        assert work[0].status == WorkStatus.UNAVAILABLE
        work_record = WorkRecord.query.filter_by(work_id=work[0].id).all()
        assert len(work_record) == 1
        assert work_record[0].active == True
        assert work_record[0].duration_seconds is None
        task = Task.query.filter_by(id=task_id).all()
        assert len(task) == 1
        assert task[0].status == TaskStatus.IN_PROCESS

        # modify work record to be started two days in the past
        work_record[0].start_time_epoch_ms = work_record[0].start_time_epoch_ms - 50 * 60 * 60 * 1000
        db.session.commit()

    # mock upwork diaries
    json_work_diaries = {
        "data": {
            "workDiaryCompany": {
                "total": 1,
                "snapshots": [
                    {
                        "task": {
                            "id": "",
                            "code": "",
                            "description": "",
                            "memo": ""
                        },
                        "contract": {
                            "id": "31312642",
                            "contractTitle": "contract name"
                        },
                        "duration": "0hr 10 min",
                        "durationInt": "10",
                        "user": {
                            "id": "upwork_user1",
                            "name": "Upwork user 1"
                        },
                        "time": {
                            "trackedTime": "10",
                            "manualTime": "0",
                            "overtime": "0",
                            "firstWorked": "05:18 AM",
                            "lastWorked": "05:18 AM",
                            "firstWorkedInt": "1673241510",
                            "lastWorkedInt": "1673241510",
                            "lastScreenshot": "1673241510"
                        },
                        "screenshots": [
                            {
                                "activity": "3",
                                "flags": {
                                    "hideScreenshots": "",
                                    "downsampleScreenshots": ""
                                },
                                "hasScreenshot": "1",
                                "screenshotUrl": "https://www.upwork.com/snapshot/#31312642/1673241510",
                                "screenshotImage": "https://upwork-usw2-prod-agora-tracker.s3.us-west-2.amazonaws.com/tracker/s/31312642/2023/1/9/1673241510?X-Amz-Security-Token=IQoJb3JpZ2luX2VjECwaCXVzLXdlc3QtMiJHMEUCIEovVfMupjvjrFeSoZlefpETvSVETJuY1x6agDp2dMiEAiEAynb420qj3DjlgolaIz9c2vXndl4wN5TpxM9ikeEOewcqzAQIhf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw3Mzk5MzkxNzM4MTkiDECCD%2BjDRWx3XR5WOiqgBMolRrwA3xK06WhhRf2WYo3EOy4pasGkHbi%2Bu0zoZU7YoOctvtfkKdcLFimPChUiYgClfa%2FhzeA1dSSDDG9xOzQ9HpFa1BVMmkMBZYoCB85nCAq8tRXkxBcuzzEDKdrYNRpUzmP6SVuVh%2B7kZ5qbrRWgGH5B2Gcktv2YT7eE2DFAUZ6%2Fq25eR9N1%2B6lig5Ei37l6FQLeScT%2FhO2yB3yZCyzGCjIGvAffsFEQTmY3TT7rgleIRanfyBsZiZYS5PnIS41L1NblIdVQhNxhlEczib5cjvxbDR6l13wbmKDgdDG8cre1viUdv%2BL1KANYcjwJhJfQDk3Haa%2B2LpTdNaz%2B9opWEjfnZ4%2BzQqF7t8xIxTyCiq2%2FJ%2BzcVdJ5Pqv6O9UrbzYH2PlspPvyBioYnwtCqp1jmDJZjX2AwNZboR0oSLQS30yETHRZ94Wm00m6s%2BVjOJsAQ%2FxwAMddVxWFvzovZa%2FlaTsUbVCwcYU5KUYRq1exAeSwtz4pxwFdkn1xYcNtr08m2rOY2IzbHoWZ0XdDLum4UI0mw8ynh%2FlOdcSJ89aPy3M5SJR9WUD3zD5PTXeWwDVXyeN9JCFVP4CwBt6ndJvrp5jtpJ8H9fLjLDWIJoK5nNV0L2Uq9R6bSNf%2Fy8D%2F6kQcy8cNDPJm5QL3vyDsAQriO0NKitOGP4LxrzpunVK6Fe5jl5nEW7yIBeYEEMc2Q060ER1SKAlvMJo0hxJtkcYwqsbznQY6pgHf0i6JTl%2FKdiQNttxLmNcN2QCW42FWa7rsvpDPacuZqY7ByIR4Cfy1hFTk2XSC%2B7GMxjy%2F08d0FjSKHotLfN43h7ebx2pQ0LM2rSWy9r052mPgO4T4DDWX5%2FgBDE%2Bwz4ODdSUP%2BqXQbluNbKHCqzgOa5whJAbJUETKPnMirv4Ro%2Bu3W5cdBd0cmRJRU4vrQ07qlFlk1GJZmfdH4Nq5C38DxBYseRtz&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230110T042227Z&X-Amz-SignedHeaders=host&X-Amz-Expires=600&X-Amz-Credential=ASIA2YR6PYW5YSI4S5V3%2F20230110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=977edcb7b7ef06ee67e572f8c62d420f60eeee7f4ca610b6875adc8b78ab0185",
                                "screenshotImageLarge": "https://upwork-usw2-prod-agora-tracker.s3.us-west-2.amazonaws.com/tracker_resized/s/31312642/2023/1/9/1673241510-lrg?X-Amz-Security-Token=IQoJb3JpZ2luX2VjECwaCXVzLXdlc3QtMiJHMEUCIEovVfMupjvjrFeSoZlefpETvSVETJuY1x6agDp2dMiEAiEAynb420qj3DjlgolaIz9c2vXndl4wN5TpxM9ikeEOewcqzAQIhf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw3Mzk5MzkxNzM4MTkiDECCD%2BjDRWx3XR5WOiqgBMolRrwA3xK06WhhRf2WYo3EOy4pasGkHbi%2Bu0zoZU7YoOctvtfkKdcLFimPChUiYgClfa%2FhzeA1dSSDDG9xOzQ9HpFa1BVMmkMBZYoCB85nCAq8tRXkxBcuzzEDKdrYNRpUzmP6SVuVh%2B7kZ5qbrRWgGH5B2Gcktv2YT7eE2DFAUZ6%2Fq25eR9N1%2B6lig5Ei37l6FQLeScT%2FhO2yB3yZCyzGCjIGvAffsFEQTmY3TT7rgleIRanfyBsZiZYS5PnIS41L1NblIdVQhNxhlEczib5cjvxbDR6l13wbmKDgdDG8cre1viUdv%2BL1KANYcjwJhJfQDk3Haa%2B2LpTdNaz%2B9opWEjfnZ4%2BzQqF7t8xIxTyCiq2%2FJ%2BzcVdJ5Pqv6O9UrbzYH2PlspPvyBioYnwtCqp1jmDJZjX2AwNZboR0oSLQS30yETHRZ94Wm00m6s%2BVjOJsAQ%2FxwAMddVxWFvzovZa%2FlaTsUbVCwcYU5KUYRq1exAeSwtz4pxwFdkn1xYcNtr08m2rOY2IzbHoWZ0XdDLum4UI0mw8ynh%2FlOdcSJ89aPy3M5SJR9WUD3zD5PTXeWwDVXyeN9JCFVP4CwBt6ndJvrp5jtpJ8H9fLjLDWIJoK5nNV0L2Uq9R6bSNf%2Fy8D%2F6kQcy8cNDPJm5QL3vyDsAQriO0NKitOGP4LxrzpunVK6Fe5jl5nEW7yIBeYEEMc2Q060ER1SKAlvMJo0hxJtkcYwqsbznQY6pgHf0i6JTl%2FKdiQNttxLmNcN2QCW42FWa7rsvpDPacuZqY7ByIR4Cfy1hFTk2XSC%2B7GMxjy%2F08d0FjSKHotLfN43h7ebx2pQ0LM2rSWy9r052mPgO4T4DDWX5%2FgBDE%2Bwz4ODdSUP%2BqXQbluNbKHCqzgOa5whJAbJUETKPnMirv4Ro%2Bu3W5cdBd0cmRJRU4vrQ07qlFlk1GJZmfdH4Nq5C38DxBYseRtz&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230110T042227Z&X-Amz-SignedHeaders=host&X-Amz-Expires=600&X-Amz-Credential=ASIA2YR6PYW5YSI4S5V3%2F20230110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=35256f0472ca6692d9e8a8c53565e7144e43e866ceae48b548775cb4aaf7a78e",
                                "screenshotImageMedium": "https://upwork-usw2-prod-agora-tracker.s3.us-west-2.amazonaws.com/tracker_resized/s/31312642/2023/1/9/1673241510-med?X-Amz-Security-Token=IQoJb3JpZ2luX2VjECwaCXVzLXdlc3QtMiJHMEUCIEovVfMupjvjrFeSoZlefpETvSVETJuY1x6agDp2dMiEAiEAynb420qj3DjlgolaIz9c2vXndl4wN5TpxM9ikeEOewcqzAQIhf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw3Mzk5MzkxNzM4MTkiDECCD%2BjDRWx3XR5WOiqgBMolRrwA3xK06WhhRf2WYo3EOy4pasGkHbi%2Bu0zoZU7YoOctvtfkKdcLFimPChUiYgClfa%2FhzeA1dSSDDG9xOzQ9HpFa1BVMmkMBZYoCB85nCAq8tRXkxBcuzzEDKdrYNRpUzmP6SVuVh%2B7kZ5qbrRWgGH5B2Gcktv2YT7eE2DFAUZ6%2Fq25eR9N1%2B6lig5Ei37l6FQLeScT%2FhO2yB3yZCyzGCjIGvAffsFEQTmY3TT7rgleIRanfyBsZiZYS5PnIS41L1NblIdVQhNxhlEczib5cjvxbDR6l13wbmKDgdDG8cre1viUdv%2BL1KANYcjwJhJfQDk3Haa%2B2LpTdNaz%2B9opWEjfnZ4%2BzQqF7t8xIxTyCiq2%2FJ%2BzcVdJ5Pqv6O9UrbzYH2PlspPvyBioYnwtCqp1jmDJZjX2AwNZboR0oSLQS30yETHRZ94Wm00m6s%2BVjOJsAQ%2FxwAMddVxWFvzovZa%2FlaTsUbVCwcYU5KUYRq1exAeSwtz4pxwFdkn1xYcNtr08m2rOY2IzbHoWZ0XdDLum4UI0mw8ynh%2FlOdcSJ89aPy3M5SJR9WUD3zD5PTXeWwDVXyeN9JCFVP4CwBt6ndJvrp5jtpJ8H9fLjLDWIJoK5nNV0L2Uq9R6bSNf%2Fy8D%2F6kQcy8cNDPJm5QL3vyDsAQriO0NKitOGP4LxrzpunVK6Fe5jl5nEW7yIBeYEEMc2Q060ER1SKAlvMJo0hxJtkcYwqsbznQY6pgHf0i6JTl%2FKdiQNttxLmNcN2QCW42FWa7rsvpDPacuZqY7ByIR4Cfy1hFTk2XSC%2B7GMxjy%2F08d0FjSKHotLfN43h7ebx2pQ0LM2rSWy9r052mPgO4T4DDWX5%2FgBDE%2Bwz4ODdSUP%2BqXQbluNbKHCqzgOa5whJAbJUETKPnMirv4Ro%2Bu3W5cdBd0cmRJRU4vrQ07qlFlk1GJZmfdH4Nq5C38DxBYseRtz&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230110T042227Z&X-Amz-SignedHeaders=host&X-Amz-Expires=600&X-Amz-Credential=ASIA2YR6PYW5YSI4S5V3%2F20230110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=98a0c640371243f3f7287eb39b710b0237451efb8ea120e44d2750670d4529f0",
                                "screenshotImageThumbnail": "https://upwork-usw2-prod-agora-tracker.s3.us-west-2.amazonaws.com/tracker_resized/s/31312642/2023/1/9/1673241510-thmb?X-Amz-Security-Token=IQoJb3JpZ2luX2VjECwaCXVzLXdlc3QtMiJHMEUCIEovVfMupjvjrFeSoZlefpETvSVETJuY1x6agDp2dMiEAiEAynb420qj3DjlgolaIz9c2vXndl4wN5TpxM9ikeEOewcqzAQIhf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw3Mzk5MzkxNzM4MTkiDECCD%2BjDRWx3XR5WOiqgBMolRrwA3xK06WhhRf2WYo3EOy4pasGkHbi%2Bu0zoZU7YoOctvtfkKdcLFimPChUiYgClfa%2FhzeA1dSSDDG9xOzQ9HpFa1BVMmkMBZYoCB85nCAq8tRXkxBcuzzEDKdrYNRpUzmP6SVuVh%2B7kZ5qbrRWgGH5B2Gcktv2YT7eE2DFAUZ6%2Fq25eR9N1%2B6lig5Ei37l6FQLeScT%2FhO2yB3yZCyzGCjIGvAffsFEQTmY3TT7rgleIRanfyBsZiZYS5PnIS41L1NblIdVQhNxhlEczib5cjvxbDR6l13wbmKDgdDG8cre1viUdv%2BL1KANYcjwJhJfQDk3Haa%2B2LpTdNaz%2B9opWEjfnZ4%2BzQqF7t8xIxTyCiq2%2FJ%2BzcVdJ5Pqv6O9UrbzYH2PlspPvyBioYnwtCqp1jmDJZjX2AwNZboR0oSLQS30yETHRZ94Wm00m6s%2BVjOJsAQ%2FxwAMddVxWFvzovZa%2FlaTsUbVCwcYU5KUYRq1exAeSwtz4pxwFdkn1xYcNtr08m2rOY2IzbHoWZ0XdDLum4UI0mw8ynh%2FlOdcSJ89aPy3M5SJR9WUD3zD5PTXeWwDVXyeN9JCFVP4CwBt6ndJvrp5jtpJ8H9fLjLDWIJoK5nNV0L2Uq9R6bSNf%2Fy8D%2F6kQcy8cNDPJm5QL3vyDsAQriO0NKitOGP4LxrzpunVK6Fe5jl5nEW7yIBeYEEMc2Q060ER1SKAlvMJo0hxJtkcYwqsbznQY6pgHf0i6JTl%2FKdiQNttxLmNcN2QCW42FWa7rsvpDPacuZqY7ByIR4Cfy1hFTk2XSC%2B7GMxjy%2F08d0FjSKHotLfN43h7ebx2pQ0LM2rSWy9r052mPgO4T4DDWX5%2FgBDE%2Bwz4ODdSUP%2BqXQbluNbKHCqzgOa5whJAbJUETKPnMirv4Ro%2Bu3W5cdBd0cmRJRU4vrQ07qlFlk1GJZmfdH4Nq5C38DxBYseRtz&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230110T042227Z&X-Amz-SignedHeaders=host&X-Amz-Expires=599&X-Amz-Credential=ASIA2YR6PYW5YSI4S5V3%2F20230110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=95c7c8594fb9525dc6980bbd3627f42dc3bf55b5ac36c5f5813f167f85f59e90",
                                "hasWebcam": "",
                                "webcamUrl": "",
                                "webcamImage": "",
                                "webcamImageThumbnail": ""
                            }
                        ]
                    }
                ]
            }
        }
    }
    mock_get_work_diary.return_value = UpworkDiarySchema().load(json_work_diaries.get('data').get('workDiaryCompany'))

    # job should update db with work diaries and calculate net duration with previous work record
    with app.app_context():
        find_net_duration_work_records.queue()


@patch.object(UpworkClient, 'get_work_diary')
@patch.object(UpworkClient, 'get_organization_id', return_value='nkzlfefsnelbn4opkwhnra')
@patch.object(UpworkClient, 'refresh_token', return_value={"access_token": "oauth2v2_1e3704277095e1a98ba48ea3e2928ab2","refresh_token": "oauth2v2_98a2b87a42e9c68db1236d4fa05f76bb","token_type": "Bearer","expires_in": 86400,"expires_at": "1712730000"})
@patch('src.jobs.upwork.dispatch_cuckoo_event', return_value=True)
@patch('src.resources.work.dispatch_cuckoo_event', return_value=True)
@patch('src.models.work_record.WorkRecord.get_ratings', return_value={'id':1,'user':'user','object_key':'o','subject':'s','score':5.0,'text':'text'})
@patch('src.resources.work.get_praesepe_authorization_code', return_value='test_auth_code')
@patch('src.utils.upwork.UpworkAuthToken.get_recent_token', return_value={"access_token":"access_token","refresh_token":"refresh_token","token_type":"token_type","expires_in":1,"expires_at":1111.111})
@patch('src.resources.work.run_beehave_pr_github_bot', new=Mock())
def test_find_net_duration_cuckoo_accepted_tasks_single_work_record(
    mock_get_recent_token,
    mock_get_praesepe_authorization_code,
    mock_work_record_get_ratings,
    mock_dispatch_cuckoo_event_resource,
    mock_dispatch_cuckoo_event_job,
    mock_refresh_token,
    mock_get_organization_id,
    mock_get_work_diary,
    app, active_token_user_id, second_active_token, second_active_token_user_id, inner_token
):
    # import here since importing the job requires an initialized flask app
    from src.jobs.upwork import find_net_duration_cuckoo_accepted_tasks

    # execute job to make sure it runs
    with app.app_context():
        find_net_duration_cuckoo_accepted_tasks.queue()

    assert mock_dispatch_cuckoo_event_job.call_count == 0
    assert mock_get_praesepe_authorization_code.call_count == 0

    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create task
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'test net duration for completed cuckoo task',
            'userName': trello_user
        }
    )
    assert res.status_code == 200
    task_id = res.json['data']['id']
    assert mock_get_praesepe_authorization_code.call_count == 0

    # set task ids so the fixture teardown can delete them
    test_find_net_duration_cuckoo_accepted_tasks_single_work_record.task_ids = [task_id]

    # get available work returns the single work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    work_id = res.json['data']['work']['id']
    assert mock_get_praesepe_authorization_code.call_count == 1

    # check work
    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).all()
        assert len(work) == 1
        assert work[0].status == WorkStatus.AVAILABLE
        work_record = WorkRecord.query.filter_by(work_id=work[0].id).all()
        assert len(work_record) == 0
        task = Task.query.filter_by(id=task_id).all()
        assert len(task) == 1
        assert task[0].status == TaskStatus.PENDING

    # job should not change anything
    with app.app_context():
        find_net_duration_cuckoo_accepted_tasks.queue()

    assert mock_dispatch_cuckoo_event_job.call_count == 0
    assert mock_get_praesepe_authorization_code.call_count == 1

    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).all()
        assert len(work) == 1
        assert work[0].status == WorkStatus.AVAILABLE
        work_record = WorkRecord.query.filter_by(work_id=work[0].id).all()
        assert len(work_record) == 0
        task = Task.query.filter_by(id=task_id).all()
        assert len(task) == 1
        assert task[0].status == TaskStatus.PENDING
        assert task[0].total_net_duration_seconds is None

    # start work
    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work[0].id, 'startTimeEpochMs': int(time.time() * 1000), 'tzName': 'UTC'}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event_resource.call_count == 1
    assert mock_get_praesepe_authorization_code.call_count == 1

    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).all()
        assert len(work) == 1
        assert work[0].status == WorkStatus.UNAVAILABLE
        work_record = WorkRecord.query.filter_by(work_id=work[0].id).all()
        assert len(work_record) == 1
        work_record_start_epoch_ms = work_record[0].start_time_epoch_ms
        task = Task.query.filter_by(id=task_id).all()
        assert len(task) == 1
        assert task[0].status == TaskStatus.IN_PROCESS

    solution_url = 'https://github.com/my-org/my-repo/pull/1'
    duration_seconds = 1200

    # finish work with some solution code
    res = app.test_client().post(
        f'api/v1/work/finish',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work_id, 'durationSeconds': duration_seconds, 'solutionUrl': solution_url}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event_resource.call_count == 2
    assert mock_get_praesepe_authorization_code.call_count == 2

    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).all()
        assert len(work) == 1
        assert work[0].status == WorkStatus.COMPLETE
        work_record = WorkRecord.query.filter_by(work_id=work[0].id).all()
        assert len(work_record) == 1
        assert work_record[0].outcome == WorkOutcome.SOLVED
        assert work_record[0].solution_url == solution_url
        assert work_record[0].duration_seconds == duration_seconds
        task = Task.query.filter_by(id=task_id).all()
        assert len(task) == 1
        assert task[0].status == TaskStatus.SOLVED

    # set task status to accepted
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

    # job should not change anything
    with app.app_context():
        find_net_duration_cuckoo_accepted_tasks.queue()

    assert mock_dispatch_cuckoo_event_job.call_count == 0
    assert mock_work_record_get_ratings.call_count == 1

    with app.app_context():
        task = Task.query.filter_by(id=task_id).first()
        assert task.total_net_duration_seconds is None

    # mock upwork diaries for this task
    with app.app_context():
        contributor_upwork_user = User.query.filter_by(id=second_active_token_user_id).first().upwork_user

    # upwork times may differ from beehive, start time is 10 minutes after our system and end time is 3 minutes after
    # beehive task duration is 20 minutes, so net should be 10 minutes
    upwork_start_epoch_sec = (work_record_start_epoch_ms / 1000) + (10*60)  ## upwork time is in seconds from epoch
    upwork_end_epoch_sec = (work_record_start_epoch_ms / 1000) + duration_seconds + (3*60)

    json_work_diaries = {
        "data": {
            "workDiaryCompany": {
                "total": 1,
                "snapshots": [
                    {
                        "task": {
                            "id": "",
                            "code": "",
                            "description": "",
                            "memo": ""
                        },
                        "contract": {
                            "id": "31312642",
                            "contractTitle": "contract1"
                        },
                        "duration": "0hr 10 min",
                        "durationInt": "10",
                        "user": {
                            "id": contributor_upwork_user,
                            "name": "Upwork user 1"
                        },
                        "time": {
                            "trackedTime": "10",
                            "manualTime": "0",
                            "overtime": "0",
                            "firstWorked": "05:18 AM",
                            "lastWorked": "05:18 AM",
                            "firstWorkedInt": upwork_start_epoch_sec,
                            "lastWorkedInt": upwork_end_epoch_sec,
                            "lastScreenshot": "1673241510"
                        },
                        "screenshots": [
                            {
                                "activity": "3",
                                "flags": {
                                    "hideScreenshots": "",
                                    "downsampleScreenshots": ""
                                },
                                "hasScreenshot": "1",
                                "screenshotUrl": "https://www.upwork.com/snapshot/#31312642/1673241510",
                                "screenshotImage": "https://upwork-usw2-prod-agora-tracker.s3.us-west-2.amazonaws.com/tracker/s/31312642/2023/1/9/1673241510?X-Amz-Security-Token=IQoJb3JpZ2luX2VjECwaCXVzLXdlc3QtMiJHMEUCIEovVfMupjvjrFeSoZlefpETvSVETJuY1x6agDp2dMiEAiEAynb420qj3DjlgolaIz9c2vXndl4wN5TpxM9ikeEOewcqzAQIhf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw3Mzk5MzkxNzM4MTkiDECCD%2BjDRWx3XR5WOiqgBMolRrwA3xK06WhhRf2WYo3EOy4pasGkHbi%2Bu0zoZU7YoOctvtfkKdcLFimPChUiYgClfa%2FhzeA1dSSDDG9xOzQ9HpFa1BVMmkMBZYoCB85nCAq8tRXkxBcuzzEDKdrYNRpUzmP6SVuVh%2B7kZ5qbrRWgGH5B2Gcktv2YT7eE2DFAUZ6%2Fq25eR9N1%2B6lig5Ei37l6FQLeScT%2FhO2yB3yZCyzGCjIGvAffsFEQTmY3TT7rgleIRanfyBsZiZYS5PnIS41L1NblIdVQhNxhlEczib5cjvxbDR6l13wbmKDgdDG8cre1viUdv%2BL1KANYcjwJhJfQDk3Haa%2B2LpTdNaz%2B9opWEjfnZ4%2BzQqF7t8xIxTyCiq2%2FJ%2BzcVdJ5Pqv6O9UrbzYH2PlspPvyBioYnwtCqp1jmDJZjX2AwNZboR0oSLQS30yETHRZ94Wm00m6s%2BVjOJsAQ%2FxwAMddVxWFvzovZa%2FlaTsUbVCwcYU5KUYRq1exAeSwtz4pxwFdkn1xYcNtr08m2rOY2IzbHoWZ0XdDLum4UI0mw8ynh%2FlOdcSJ89aPy3M5SJR9WUD3zD5PTXeWwDVXyeN9JCFVP4CwBt6ndJvrp5jtpJ8H9fLjLDWIJoK5nNV0L2Uq9R6bSNf%2Fy8D%2F6kQcy8cNDPJm5QL3vyDsAQriO0NKitOGP4LxrzpunVK6Fe5jl5nEW7yIBeYEEMc2Q060ER1SKAlvMJo0hxJtkcYwqsbznQY6pgHf0i6JTl%2FKdiQNttxLmNcN2QCW42FWa7rsvpDPacuZqY7ByIR4Cfy1hFTk2XSC%2B7GMxjy%2F08d0FjSKHotLfN43h7ebx2pQ0LM2rSWy9r052mPgO4T4DDWX5%2FgBDE%2Bwz4ODdSUP%2BqXQbluNbKHCqzgOa5whJAbJUETKPnMirv4Ro%2Bu3W5cdBd0cmRJRU4vrQ07qlFlk1GJZmfdH4Nq5C38DxBYseRtz&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230110T042227Z&X-Amz-SignedHeaders=host&X-Amz-Expires=600&X-Amz-Credential=ASIA2YR6PYW5YSI4S5V3%2F20230110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=977edcb7b7ef06ee67e572f8c62d420f60eeee7f4ca610b6875adc8b78ab0185",
                                "screenshotImageLarge": "https://upwork-usw2-prod-agora-tracker.s3.us-west-2.amazonaws.com/tracker_resized/s/31312642/2023/1/9/1673241510-lrg?X-Amz-Security-Token=IQoJb3JpZ2luX2VjECwaCXVzLXdlc3QtMiJHMEUCIEovVfMupjvjrFeSoZlefpETvSVETJuY1x6agDp2dMiEAiEAynb420qj3DjlgolaIz9c2vXndl4wN5TpxM9ikeEOewcqzAQIhf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw3Mzk5MzkxNzM4MTkiDECCD%2BjDRWx3XR5WOiqgBMolRrwA3xK06WhhRf2WYo3EOy4pasGkHbi%2Bu0zoZU7YoOctvtfkKdcLFimPChUiYgClfa%2FhzeA1dSSDDG9xOzQ9HpFa1BVMmkMBZYoCB85nCAq8tRXkxBcuzzEDKdrYNRpUzmP6SVuVh%2B7kZ5qbrRWgGH5B2Gcktv2YT7eE2DFAUZ6%2Fq25eR9N1%2B6lig5Ei37l6FQLeScT%2FhO2yB3yZCyzGCjIGvAffsFEQTmY3TT7rgleIRanfyBsZiZYS5PnIS41L1NblIdVQhNxhlEczib5cjvxbDR6l13wbmKDgdDG8cre1viUdv%2BL1KANYcjwJhJfQDk3Haa%2B2LpTdNaz%2B9opWEjfnZ4%2BzQqF7t8xIxTyCiq2%2FJ%2BzcVdJ5Pqv6O9UrbzYH2PlspPvyBioYnwtCqp1jmDJZjX2AwNZboR0oSLQS30yETHRZ94Wm00m6s%2BVjOJsAQ%2FxwAMddVxWFvzovZa%2FlaTsUbVCwcYU5KUYRq1exAeSwtz4pxwFdkn1xYcNtr08m2rOY2IzbHoWZ0XdDLum4UI0mw8ynh%2FlOdcSJ89aPy3M5SJR9WUD3zD5PTXeWwDVXyeN9JCFVP4CwBt6ndJvrp5jtpJ8H9fLjLDWIJoK5nNV0L2Uq9R6bSNf%2Fy8D%2F6kQcy8cNDPJm5QL3vyDsAQriO0NKitOGP4LxrzpunVK6Fe5jl5nEW7yIBeYEEMc2Q060ER1SKAlvMJo0hxJtkcYwqsbznQY6pgHf0i6JTl%2FKdiQNttxLmNcN2QCW42FWa7rsvpDPacuZqY7ByIR4Cfy1hFTk2XSC%2B7GMxjy%2F08d0FjSKHotLfN43h7ebx2pQ0LM2rSWy9r052mPgO4T4DDWX5%2FgBDE%2Bwz4ODdSUP%2BqXQbluNbKHCqzgOa5whJAbJUETKPnMirv4Ro%2Bu3W5cdBd0cmRJRU4vrQ07qlFlk1GJZmfdH4Nq5C38DxBYseRtz&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230110T042227Z&X-Amz-SignedHeaders=host&X-Amz-Expires=600&X-Amz-Credential=ASIA2YR6PYW5YSI4S5V3%2F20230110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=35256f0472ca6692d9e8a8c53565e7144e43e866ceae48b548775cb4aaf7a78e",
                                "screenshotImageMedium": "https://upwork-usw2-prod-agora-tracker.s3.us-west-2.amazonaws.com/tracker_resized/s/31312642/2023/1/9/1673241510-med?X-Amz-Security-Token=IQoJb3JpZ2luX2VjECwaCXVzLXdlc3QtMiJHMEUCIEovVfMupjvjrFeSoZlefpETvSVETJuY1x6agDp2dMiEAiEAynb420qj3DjlgolaIz9c2vXndl4wN5TpxM9ikeEOewcqzAQIhf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw3Mzk5MzkxNzM4MTkiDECCD%2BjDRWx3XR5WOiqgBMolRrwA3xK06WhhRf2WYo3EOy4pasGkHbi%2Bu0zoZU7YoOctvtfkKdcLFimPChUiYgClfa%2FhzeA1dSSDDG9xOzQ9HpFa1BVMmkMBZYoCB85nCAq8tRXkxBcuzzEDKdrYNRpUzmP6SVuVh%2B7kZ5qbrRWgGH5B2Gcktv2YT7eE2DFAUZ6%2Fq25eR9N1%2B6lig5Ei37l6FQLeScT%2FhO2yB3yZCyzGCjIGvAffsFEQTmY3TT7rgleIRanfyBsZiZYS5PnIS41L1NblIdVQhNxhlEczib5cjvxbDR6l13wbmKDgdDG8cre1viUdv%2BL1KANYcjwJhJfQDk3Haa%2B2LpTdNaz%2B9opWEjfnZ4%2BzQqF7t8xIxTyCiq2%2FJ%2BzcVdJ5Pqv6O9UrbzYH2PlspPvyBioYnwtCqp1jmDJZjX2AwNZboR0oSLQS30yETHRZ94Wm00m6s%2BVjOJsAQ%2FxwAMddVxWFvzovZa%2FlaTsUbVCwcYU5KUYRq1exAeSwtz4pxwFdkn1xYcNtr08m2rOY2IzbHoWZ0XdDLum4UI0mw8ynh%2FlOdcSJ89aPy3M5SJR9WUD3zD5PTXeWwDVXyeN9JCFVP4CwBt6ndJvrp5jtpJ8H9fLjLDWIJoK5nNV0L2Uq9R6bSNf%2Fy8D%2F6kQcy8cNDPJm5QL3vyDsAQriO0NKitOGP4LxrzpunVK6Fe5jl5nEW7yIBeYEEMc2Q060ER1SKAlvMJo0hxJtkcYwqsbznQY6pgHf0i6JTl%2FKdiQNttxLmNcN2QCW42FWa7rsvpDPacuZqY7ByIR4Cfy1hFTk2XSC%2B7GMxjy%2F08d0FjSKHotLfN43h7ebx2pQ0LM2rSWy9r052mPgO4T4DDWX5%2FgBDE%2Bwz4ODdSUP%2BqXQbluNbKHCqzgOa5whJAbJUETKPnMirv4Ro%2Bu3W5cdBd0cmRJRU4vrQ07qlFlk1GJZmfdH4Nq5C38DxBYseRtz&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230110T042227Z&X-Amz-SignedHeaders=host&X-Amz-Expires=600&X-Amz-Credential=ASIA2YR6PYW5YSI4S5V3%2F20230110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=98a0c640371243f3f7287eb39b710b0237451efb8ea120e44d2750670d4529f0",
                                "screenshotImageThumbnail": "https://upwork-usw2-prod-agora-tracker.s3.us-west-2.amazonaws.com/tracker_resized/s/31312642/2023/1/9/1673241510-thmb?X-Amz-Security-Token=IQoJb3JpZ2luX2VjECwaCXVzLXdlc3QtMiJHMEUCIEovVfMupjvjrFeSoZlefpETvSVETJuY1x6agDp2dMiEAiEAynb420qj3DjlgolaIz9c2vXndl4wN5TpxM9ikeEOewcqzAQIhf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw3Mzk5MzkxNzM4MTkiDECCD%2BjDRWx3XR5WOiqgBMolRrwA3xK06WhhRf2WYo3EOy4pasGkHbi%2Bu0zoZU7YoOctvtfkKdcLFimPChUiYgClfa%2FhzeA1dSSDDG9xOzQ9HpFa1BVMmkMBZYoCB85nCAq8tRXkxBcuzzEDKdrYNRpUzmP6SVuVh%2B7kZ5qbrRWgGH5B2Gcktv2YT7eE2DFAUZ6%2Fq25eR9N1%2B6lig5Ei37l6FQLeScT%2FhO2yB3yZCyzGCjIGvAffsFEQTmY3TT7rgleIRanfyBsZiZYS5PnIS41L1NblIdVQhNxhlEczib5cjvxbDR6l13wbmKDgdDG8cre1viUdv%2BL1KANYcjwJhJfQDk3Haa%2B2LpTdNaz%2B9opWEjfnZ4%2BzQqF7t8xIxTyCiq2%2FJ%2BzcVdJ5Pqv6O9UrbzYH2PlspPvyBioYnwtCqp1jmDJZjX2AwNZboR0oSLQS30yETHRZ94Wm00m6s%2BVjOJsAQ%2FxwAMddVxWFvzovZa%2FlaTsUbVCwcYU5KUYRq1exAeSwtz4pxwFdkn1xYcNtr08m2rOY2IzbHoWZ0XdDLum4UI0mw8ynh%2FlOdcSJ89aPy3M5SJR9WUD3zD5PTXeWwDVXyeN9JCFVP4CwBt6ndJvrp5jtpJ8H9fLjLDWIJoK5nNV0L2Uq9R6bSNf%2Fy8D%2F6kQcy8cNDPJm5QL3vyDsAQriO0NKitOGP4LxrzpunVK6Fe5jl5nEW7yIBeYEEMc2Q060ER1SKAlvMJo0hxJtkcYwqsbznQY6pgHf0i6JTl%2FKdiQNttxLmNcN2QCW42FWa7rsvpDPacuZqY7ByIR4Cfy1hFTk2XSC%2B7GMxjy%2F08d0FjSKHotLfN43h7ebx2pQ0LM2rSWy9r052mPgO4T4DDWX5%2FgBDE%2Bwz4ODdSUP%2BqXQbluNbKHCqzgOa5whJAbJUETKPnMirv4Ro%2Bu3W5cdBd0cmRJRU4vrQ07qlFlk1GJZmfdH4Nq5C38DxBYseRtz&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230110T042227Z&X-Amz-SignedHeaders=host&X-Amz-Expires=599&X-Amz-Credential=ASIA2YR6PYW5YSI4S5V3%2F20230110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=95c7c8594fb9525dc6980bbd3627f42dc3bf55b5ac36c5f5813f167f85f59e90",
                                "hasWebcam": "",
                                "webcamUrl": "",
                                "webcamImage": "",
                                "webcamImageThumbnail": ""
                            }
                        ]
                    }
                ]
            }
        }
    }
    mock_get_work_diary.return_value = UpworkDiarySchema().load(json_work_diaries.get('data').get('workDiaryCompany'))

    # save and process upwork diaries (dates in query params don't matter because the response is mocked)
    res = app.test_client().get(
        f'/api/v1/backoffice/upwork-diary',
        headers={'X-BEE-AUTH': inner_token},
        query_string={'startDate': '20230101', 'endDate': '20230101'}
    )
    assert res.status_code == 200
    assert res.json['status'] == 'ok'
    assert len(res.json['data']) == len(mock_get_work_diary.return_value.get('snapshots'))
    upwork_diary_ids = [d.get('id') for d in res.json['data']]

    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).first()
        work_record = WorkRecord.query.filter_by(work_id=work.id).first()
        work_record_upwork_diary = WorkRecordUpworkDiary.query.filter_by(work_record_id=work_record.id).all()
        assert len(work_record_upwork_diary) == 1
        assert work_record_upwork_diary[0].upwork_diary_id == upwork_diary_ids[0]

    # job should not change anything because task hasn't been accepted *yesterday*
    with app.app_context():
        find_net_duration_cuckoo_accepted_tasks.queue()

    assert mock_dispatch_cuckoo_event_job.call_count == 0

    with app.app_context():
        task = Task.query.filter_by(id=task_id).first()
        assert task.total_net_duration_seconds is None

        # modify task updated timestamp to yesterday
        task.updated = task.updated - timedelta(days=1)
        db.session.commit()

    # job should notify cuckoo about tasks total net duration
    with app.app_context():
        find_net_duration_cuckoo_accepted_tasks.queue()

    assert mock_dispatch_cuckoo_event_job.call_count == 1

    with app.app_context():
        task = Task.query.filter_by(id=task_id).first()
        work = Work.query.filter_by(task_id=task_id).first()
        work_record = WorkRecord.query.filter_by(work_id=work.id).first()
        work_record_upwork_diary = WorkRecordUpworkDiary.query.filter_by(work_record_id=work_record.id).first()
        assert task.total_net_duration_seconds == work_record_upwork_diary.upwork_duration_seconds


@patch.object(UpworkClient, 'get_work_diary')
@patch.object(UpworkClient, 'get_organization_id', return_value='nkzlfefsnelbn4opkwhnra')
@patch.object(UpworkClient, 'refresh_token', return_value={"access_token": "oauth2v2_1e3704277095e1a98ba48ea3e2928ab2","refresh_token": "oauth2v2_98a2b87a42e9c68db1236d4fa05f76bb","token_type": "Bearer","expires_in": 86400,"expires_at": "1712730000"})
@patch('src.jobs.upwork.dispatch_cuckoo_event', return_value=True)
@patch('src.resources.work.dispatch_cuckoo_event', return_value=True)
@patch('src.models.work_record.WorkRecord.get_ratings', return_value={'id':1,'user':'user','object_key':'o','subject':'s','score':5.0,'text':'text'})
@patch('src.resources.work.get_praesepe_authorization_code', return_value='test_auth_code')
@patch('src.utils.upwork.UpworkAuthToken.get_recent_token', return_value={"access_token":"access_token","refresh_token":"refresh_token","token_type":"token_type","expires_in":1,"expires_at":1111.111})
@patch('src.resources.work.run_beehave_pr_github_bot', new=Mock())
def test_find_net_duration_cuckoo_accepted_tasks_multiple_work_record(
    mock_get_recent_token,
    mock_get_praesepe_authorization_code,
    mock_work_record_get_ratings,
    mock_dispatch_cuckoo_event_resource,
    mock_dispatch_cuckoo_event_job,
    mock_refresh_token,
    mock_get_organization_id,
    mock_get_work_diary,
    app, active_token, active_token_user_id, second_active_token, second_active_token_user_id, inner_token, delegation
):
    # import here since importing the job requires an initialized flask app
    from src.jobs.upwork import find_net_duration_cuckoo_accepted_tasks

    # execute job to make sure it runs
    with app.app_context():
        find_net_duration_cuckoo_accepted_tasks.queue()

    assert mock_dispatch_cuckoo_event_job.call_count == 0
    assert mock_get_praesepe_authorization_code.call_count == 0

    work_record_ids = []

    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

    # create task
    res = app.test_client().post(
        'api/v1/task/cuckoo',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'description': 'test net duration for completed cuckoo task',
            'userName': trello_user
        }
    )
    assert res.status_code == 200
    task_id = res.json['data']['id']
    assert mock_get_praesepe_authorization_code.call_count == 0

    # set task ids so the fixture teardown can delete them
    test_find_net_duration_cuckoo_accepted_tasks_multiple_work_record.task_ids = [task_id]

    # get available work returns the single work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {second_active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    work_id = res.json['data']['work']['id']

    def unix_time_ms(dt):
        return int((dt - datetime.utcfromtimestamp(0)).total_seconds() * 1000)

    # start first work
    first_start_time = datetime.utcnow()
    first_start_time_epoch_ms = unix_time_ms(first_start_time)

    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work_id, 'startTimeEpochMs': first_start_time_epoch_ms, 'tzName': 'UTC'}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event_resource.call_count == 1
    assert mock_get_praesepe_authorization_code.call_count == 1

    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).all()
        assert len(work) == 1
        assert work[0].status == WorkStatus.UNAVAILABLE
        work_record = WorkRecord.query.filter_by(work_id=work[0].id).all()
        assert len(work_record) == 1
        work_record = work_record[0]
        first_work_record_start_epoch_ms = work_record.start_time_epoch_ms
        task = Task.query.filter_by(id=task_id).all()
        assert len(task) == 1
        assert task[0].status == TaskStatus.IN_PROCESS
        work_record_ids.append(work_record.id)

    # finish first work with some solution code
    solution_url = 'https://github.com/my-org/my-repo/pull/1'
    first_duration_seconds = 3 * 60 * 60

    res = app.test_client().post(
        f'api/v1/work/finish',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work_id, 'durationSeconds': first_duration_seconds, 'solutionUrl': solution_url}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event_resource.call_count == 2
    assert mock_get_praesepe_authorization_code.call_count == 2

    # delegator starts review
    res = app.test_client().post(
        f'api/v1/work/review',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workRecordId': work_record.id}
    )

    # assert redirected to pull request url
    assert res.status_code == 200
    assert res.json['data']['solutionUrl'] == solution_url

    # ask for modifications for this task
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
    assert mock_dispatch_cuckoo_event_resource.call_count == 2
    assert mock_work_record_get_ratings.call_count == 1
    assert mock_get_praesepe_authorization_code.call_count == 2

    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).all()
        assert len(work) == 2
        assert work[0].status == WorkStatus.COMPLETE
        assert work[1].status == WorkStatus.AVAILABLE
        work_record = WorkRecord.query.filter_by(work_id=work[1].id).all()
        assert len(work_record) == 0
        task = Task.query.filter_by(id=task_id).all()
        assert len(task) == 1
        assert task[0].status == TaskStatus.MODIFICATIONS_REQUESTED

    # start second work
    second_start_time = datetime.utcnow()
    second_start_time_epoch_ms = unix_time_ms(second_start_time)
    
    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work[1].id, 'startTimeEpochMs': second_start_time_epoch_ms, 'tzName': 'UTC'}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event_resource.call_count == 3
    assert mock_get_praesepe_authorization_code.call_count == 2

    with app.app_context():
        work = Work.query.filter_by(task_id=task_id).all()
        assert len(work) == 2
        assert work[1].status == WorkStatus.UNAVAILABLE
        work_record = WorkRecord.query.filter_by(work_id=work[1].id).all()
        assert len(work_record) == 1
        second_work_record_start_epoch_ms = work_record[0].start_time_epoch_ms
        task = Task.query.filter_by(id=task_id).all()
        assert len(task) == 1
        assert task[0].status == TaskStatus.IN_PROCESS
        work_record_ids.append(work_record[0].id)

    # finish second work with same solution code
    second_duration_seconds = 45 * 60
    res = app.test_client().post(
        f'api/v1/work/finish',
        headers={'Authorization': f'Bearer {second_active_token}'},
        json={'workId': work[1].id, 'durationSeconds': second_duration_seconds, 'solutionUrl': solution_url}
    )
    assert res.status_code == 200
    assert mock_dispatch_cuckoo_event_resource.call_count == 4
    assert mock_work_record_get_ratings.call_count == 1
    assert mock_get_praesepe_authorization_code.call_count == 3

    # delegator set task status to accepted
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

    # job should not change anything
    with app.app_context():
        find_net_duration_cuckoo_accepted_tasks.queue()

    assert mock_dispatch_cuckoo_event_job.call_count == 0
    assert mock_work_record_get_ratings.call_count == 3
    assert mock_get_praesepe_authorization_code.call_count == 3

    with app.app_context():
        task = Task.query.filter_by(id=task_id).first()
        assert task.total_net_duration_seconds is None

    # mock upwork diaries for this task
    with app.app_context():
        contributor_upwork_user = User.query.filter_by(id=second_active_token_user_id).first().upwork_user

    first_upwork_start_epoch_sec = first_work_record_start_epoch_ms / 1000
    first_upwork_end_epoch_sec = (first_work_record_start_epoch_ms / 1000) + first_duration_seconds
    second_upwork_start_epoch_sec = second_work_record_start_epoch_ms / 1000
    second_upwork_end_epoch_sec = (second_work_record_start_epoch_ms / 1000) + second_duration_seconds

    json_work_diaries = {
        "data": {
            "workDiaryCompany": {
                "total": 2,
                "snapshots": [
                    {
                        "task": {
                            "id": "",
                            "code": "",
                            "description": "",
                            "memo": ""
                        },
                        "contract": {
                            "id": "31312642",
                            "contractTitle": "Tech Lead -"
                        },
                        "duration": "0hr 50 min",
                        "durationInt": "50",
                        "user": {
                            "id": contributor_upwork_user,
                            "name": "Upwork user 1",
                        },
                        "time": {
                            "trackedTime": "50",
                            "manualTime": "0",
                            "overtime": "0",
                            "firstWorked": "05:18 AM",
                            "lastWorked": "05:18 AM",
                            "firstWorkedInt": first_upwork_start_epoch_sec,
                            "lastWorkedInt": first_upwork_end_epoch_sec,
                            "lastScreenshot": str(first_upwork_end_epoch_sec)
                        },
                        "screenshots": [
                            {
                                "activity": "3",
                                "flags": {
                                    "hideScreenshots": "",
                                    "downsampleScreenshots": ""
                                },
                                "hasScreenshot": "1",
                                "screenshotUrl": "https://www.upwork.com/snapshot/#31312642/1673241510",
                                "screenshotImage": "https://upwork-usw2-prod-agora-tracker.s3.us-west-2.amazonaws.com/tracker/s/31312642/2023/1/9/1673241510?X-Amz-Security-Token=IQoJb3JpZ2luX2VjECwaCXVzLXdlc3QtMiJHMEUCIEovVfMupjvjrFeSoZlefpETvSVETJuY1x6agDp2dMiEAiEAynb420qj3DjlgolaIz9c2vXndl4wN5TpxM9ikeEOewcqzAQIhf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw3Mzk5MzkxNzM4MTkiDECCD%2BjDRWx3XR5WOiqgBMolRrwA3xK06WhhRf2WYo3EOy4pasGkHbi%2Bu0zoZU7YoOctvtfkKdcLFimPChUiYgClfa%2FhzeA1dSSDDG9xOzQ9HpFa1BVMmkMBZYoCB85nCAq8tRXkxBcuzzEDKdrYNRpUzmP6SVuVh%2B7kZ5qbrRWgGH5B2Gcktv2YT7eE2DFAUZ6%2Fq25eR9N1%2B6lig5Ei37l6FQLeScT%2FhO2yB3yZCyzGCjIGvAffsFEQTmY3TT7rgleIRanfyBsZiZYS5PnIS41L1NblIdVQhNxhlEczib5cjvxbDR6l13wbmKDgdDG8cre1viUdv%2BL1KANYcjwJhJfQDk3Haa%2B2LpTdNaz%2B9opWEjfnZ4%2BzQqF7t8xIxTyCiq2%2FJ%2BzcVdJ5Pqv6O9UrbzYH2PlspPvyBioYnwtCqp1jmDJZjX2AwNZboR0oSLQS30yETHRZ94Wm00m6s%2BVjOJsAQ%2FxwAMddVxWFvzovZa%2FlaTsUbVCwcYU5KUYRq1exAeSwtz4pxwFdkn1xYcNtr08m2rOY2IzbHoWZ0XdDLum4UI0mw8ynh%2FlOdcSJ89aPy3M5SJR9WUD3zD5PTXeWwDVXyeN9JCFVP4CwBt6ndJvrp5jtpJ8H9fLjLDWIJoK5nNV0L2Uq9R6bSNf%2Fy8D%2F6kQcy8cNDPJm5QL3vyDsAQriO0NKitOGP4LxrzpunVK6Fe5jl5nEW7yIBeYEEMc2Q060ER1SKAlvMJo0hxJtkcYwqsbznQY6pgHf0i6JTl%2FKdiQNttxLmNcN2QCW42FWa7rsvpDPacuZqY7ByIR4Cfy1hFTk2XSC%2B7GMxjy%2F08d0FjSKHotLfN43h7ebx2pQ0LM2rSWy9r052mPgO4T4DDWX5%2FgBDE%2Bwz4ODdSUP%2BqXQbluNbKHCqzgOa5whJAbJUETKPnMirv4Ro%2Bu3W5cdBd0cmRJRU4vrQ07qlFlk1GJZmfdH4Nq5C38DxBYseRtz&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230110T042227Z&X-Amz-SignedHeaders=host&X-Amz-Expires=600&X-Amz-Credential=ASIA2YR6PYW5YSI4S5V3%2F20230110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=977edcb7b7ef06ee67e572f8c62d420f60eeee7f4ca610b6875adc8b78ab0185",
                                "screenshotImageLarge": "https://upwork-usw2-prod-agora-tracker.s3.us-west-2.amazonaws.com/tracker_resized/s/31312642/2023/1/9/1673241510-lrg?X-Amz-Security-Token=IQoJb3JpZ2luX2VjECwaCXVzLXdlc3QtMiJHMEUCIEovVfMupjvjrFeSoZlefpETvSVETJuY1x6agDp2dMiEAiEAynb420qj3DjlgolaIz9c2vXndl4wN5TpxM9ikeEOewcqzAQIhf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw3Mzk5MzkxNzM4MTkiDECCD%2BjDRWx3XR5WOiqgBMolRrwA3xK06WhhRf2WYo3EOy4pasGkHbi%2Bu0zoZU7YoOctvtfkKdcLFimPChUiYgClfa%2FhzeA1dSSDDG9xOzQ9HpFa1BVMmkMBZYoCB85nCAq8tRXkxBcuzzEDKdrYNRpUzmP6SVuVh%2B7kZ5qbrRWgGH5B2Gcktv2YT7eE2DFAUZ6%2Fq25eR9N1%2B6lig5Ei37l6FQLeScT%2FhO2yB3yZCyzGCjIGvAffsFEQTmY3TT7rgleIRanfyBsZiZYS5PnIS41L1NblIdVQhNxhlEczib5cjvxbDR6l13wbmKDgdDG8cre1viUdv%2BL1KANYcjwJhJfQDk3Haa%2B2LpTdNaz%2B9opWEjfnZ4%2BzQqF7t8xIxTyCiq2%2FJ%2BzcVdJ5Pqv6O9UrbzYH2PlspPvyBioYnwtCqp1jmDJZjX2AwNZboR0oSLQS30yETHRZ94Wm00m6s%2BVjOJsAQ%2FxwAMddVxWFvzovZa%2FlaTsUbVCwcYU5KUYRq1exAeSwtz4pxwFdkn1xYcNtr08m2rOY2IzbHoWZ0XdDLum4UI0mw8ynh%2FlOdcSJ89aPy3M5SJR9WUD3zD5PTXeWwDVXyeN9JCFVP4CwBt6ndJvrp5jtpJ8H9fLjLDWIJoK5nNV0L2Uq9R6bSNf%2Fy8D%2F6kQcy8cNDPJm5QL3vyDsAQriO0NKitOGP4LxrzpunVK6Fe5jl5nEW7yIBeYEEMc2Q060ER1SKAlvMJo0hxJtkcYwqsbznQY6pgHf0i6JTl%2FKdiQNttxLmNcN2QCW42FWa7rsvpDPacuZqY7ByIR4Cfy1hFTk2XSC%2B7GMxjy%2F08d0FjSKHotLfN43h7ebx2pQ0LM2rSWy9r052mPgO4T4DDWX5%2FgBDE%2Bwz4ODdSUP%2BqXQbluNbKHCqzgOa5whJAbJUETKPnMirv4Ro%2Bu3W5cdBd0cmRJRU4vrQ07qlFlk1GJZmfdH4Nq5C38DxBYseRtz&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230110T042227Z&X-Amz-SignedHeaders=host&X-Amz-Expires=600&X-Amz-Credential=ASIA2YR6PYW5YSI4S5V3%2F20230110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=35256f0472ca6692d9e8a8c53565e7144e43e866ceae48b548775cb4aaf7a78e",
                                "screenshotImageMedium": "https://upwork-usw2-prod-agora-tracker.s3.us-west-2.amazonaws.com/tracker_resized/s/31312642/2023/1/9/1673241510-med?X-Amz-Security-Token=IQoJb3JpZ2luX2VjECwaCXVzLXdlc3QtMiJHMEUCIEovVfMupjvjrFeSoZlefpETvSVETJuY1x6agDp2dMiEAiEAynb420qj3DjlgolaIz9c2vXndl4wN5TpxM9ikeEOewcqzAQIhf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw3Mzk5MzkxNzM4MTkiDECCD%2BjDRWx3XR5WOiqgBMolRrwA3xK06WhhRf2WYo3EOy4pasGkHbi%2Bu0zoZU7YoOctvtfkKdcLFimPChUiYgClfa%2FhzeA1dSSDDG9xOzQ9HpFa1BVMmkMBZYoCB85nCAq8tRXkxBcuzzEDKdrYNRpUzmP6SVuVh%2B7kZ5qbrRWgGH5B2Gcktv2YT7eE2DFAUZ6%2Fq25eR9N1%2B6lig5Ei37l6FQLeScT%2FhO2yB3yZCyzGCjIGvAffsFEQTmY3TT7rgleIRanfyBsZiZYS5PnIS41L1NblIdVQhNxhlEczib5cjvxbDR6l13wbmKDgdDG8cre1viUdv%2BL1KANYcjwJhJfQDk3Haa%2B2LpTdNaz%2B9opWEjfnZ4%2BzQqF7t8xIxTyCiq2%2FJ%2BzcVdJ5Pqv6O9UrbzYH2PlspPvyBioYnwtCqp1jmDJZjX2AwNZboR0oSLQS30yETHRZ94Wm00m6s%2BVjOJsAQ%2FxwAMddVxWFvzovZa%2FlaTsUbVCwcYU5KUYRq1exAeSwtz4pxwFdkn1xYcNtr08m2rOY2IzbHoWZ0XdDLum4UI0mw8ynh%2FlOdcSJ89aPy3M5SJR9WUD3zD5PTXeWwDVXyeN9JCFVP4CwBt6ndJvrp5jtpJ8H9fLjLDWIJoK5nNV0L2Uq9R6bSNf%2Fy8D%2F6kQcy8cNDPJm5QL3vyDsAQriO0NKitOGP4LxrzpunVK6Fe5jl5nEW7yIBeYEEMc2Q060ER1SKAlvMJo0hxJtkcYwqsbznQY6pgHf0i6JTl%2FKdiQNttxLmNcN2QCW42FWa7rsvpDPacuZqY7ByIR4Cfy1hFTk2XSC%2B7GMxjy%2F08d0FjSKHotLfN43h7ebx2pQ0LM2rSWy9r052mPgO4T4DDWX5%2FgBDE%2Bwz4ODdSUP%2BqXQbluNbKHCqzgOa5whJAbJUETKPnMirv4Ro%2Bu3W5cdBd0cmRJRU4vrQ07qlFlk1GJZmfdH4Nq5C38DxBYseRtz&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230110T042227Z&X-Amz-SignedHeaders=host&X-Amz-Expires=600&X-Amz-Credential=ASIA2YR6PYW5YSI4S5V3%2F20230110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=98a0c640371243f3f7287eb39b710b0237451efb8ea120e44d2750670d4529f0",
                                "screenshotImageThumbnail": "https://upwork-usw2-prod-agora-tracker.s3.us-west-2.amazonaws.com/tracker_resized/s/31312642/2023/1/9/1673241510-thmb?X-Amz-Security-Token=IQoJb3JpZ2luX2VjECwaCXVzLXdlc3QtMiJHMEUCIEovVfMupjvjrFeSoZlefpETvSVETJuY1x6agDp2dMiEAiEAynb420qj3DjlgolaIz9c2vXndl4wN5TpxM9ikeEOewcqzAQIhf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw3Mzk5MzkxNzM4MTkiDECCD%2BjDRWx3XR5WOiqgBMolRrwA3xK06WhhRf2WYo3EOy4pasGkHbi%2Bu0zoZU7YoOctvtfkKdcLFimPChUiYgClfa%2FhzeA1dSSDDG9xOzQ9HpFa1BVMmkMBZYoCB85nCAq8tRXkxBcuzzEDKdrYNRpUzmP6SVuVh%2B7kZ5qbrRWgGH5B2Gcktv2YT7eE2DFAUZ6%2Fq25eR9N1%2B6lig5Ei37l6FQLeScT%2FhO2yB3yZCyzGCjIGvAffsFEQTmY3TT7rgleIRanfyBsZiZYS5PnIS41L1NblIdVQhNxhlEczib5cjvxbDR6l13wbmKDgdDG8cre1viUdv%2BL1KANYcjwJhJfQDk3Haa%2B2LpTdNaz%2B9opWEjfnZ4%2BzQqF7t8xIxTyCiq2%2FJ%2BzcVdJ5Pqv6O9UrbzYH2PlspPvyBioYnwtCqp1jmDJZjX2AwNZboR0oSLQS30yETHRZ94Wm00m6s%2BVjOJsAQ%2FxwAMddVxWFvzovZa%2FlaTsUbVCwcYU5KUYRq1exAeSwtz4pxwFdkn1xYcNtr08m2rOY2IzbHoWZ0XdDLum4UI0mw8ynh%2FlOdcSJ89aPy3M5SJR9WUD3zD5PTXeWwDVXyeN9JCFVP4CwBt6ndJvrp5jtpJ8H9fLjLDWIJoK5nNV0L2Uq9R6bSNf%2Fy8D%2F6kQcy8cNDPJm5QL3vyDsAQriO0NKitOGP4LxrzpunVK6Fe5jl5nEW7yIBeYEEMc2Q060ER1SKAlvMJo0hxJtkcYwqsbznQY6pgHf0i6JTl%2FKdiQNttxLmNcN2QCW42FWa7rsvpDPacuZqY7ByIR4Cfy1hFTk2XSC%2B7GMxjy%2F08d0FjSKHotLfN43h7ebx2pQ0LM2rSWy9r052mPgO4T4DDWX5%2FgBDE%2Bwz4ODdSUP%2BqXQbluNbKHCqzgOa5whJAbJUETKPnMirv4Ro%2Bu3W5cdBd0cmRJRU4vrQ07qlFlk1GJZmfdH4Nq5C38DxBYseRtz&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230110T042227Z&X-Amz-SignedHeaders=host&X-Amz-Expires=599&X-Amz-Credential=ASIA2YR6PYW5YSI4S5V3%2F20230110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=95c7c8594fb9525dc6980bbd3627f42dc3bf55b5ac36c5f5813f167f85f59e90",
                                "hasWebcam": "",
                                "webcamUrl": "",
                                "webcamImage": "",
                                "webcamImageThumbnail": ""
                            }
                        ]
                    },
                    {
                        "task": {
                            "id": "",
                            "code": "",
                            "description": "",
                            "memo": ""
                        },
                        "contract": {
                            "id": "31312642",
                            "contractTitle": "Tech Lead -"
                        },
                        "duration": "0hr 30 min",
                        "durationInt": "30",
                        "user": {
                            "id": contributor_upwork_user,
                            "name": "Upwork user 1",
                        },
                        "time": {
                            "trackedTime": "30",
                            "manualTime": "0",
                            "overtime": "0",
                            "firstWorked": "05:18 AM",
                            "lastWorked": "05:18 AM",
                            "firstWorkedInt": second_upwork_start_epoch_sec,
                            "lastWorkedInt": second_upwork_end_epoch_sec,
                            "lastScreenshot": str(second_upwork_end_epoch_sec)
                        },
                        "screenshots": [
                            {
                                "activity": "4",
                                "flags": {
                                    "hideScreenshots": "",
                                    "downsampleScreenshots": ""
                                },
                                "hasScreenshot": "1",
                                "screenshotUrl": "https://www.upwork.com/snapshot/#31312642/1673241510",
                                "screenshotImage": "https://upwork-usw2-prod-agora-tracker.s3.us-west-2.amazonaws.com/tracker/s/31312642/2023/1/9/1673241510?X-Amz-Security-Token=IQoJb3JpZ2luX2VjECwaCXVzLXdlc3QtMiJHMEUCIEovVfMupjvjrFeSoZlefpETvSVETJuY1x6agDp2dMiEAiEAynb420qj3DjlgolaIz9c2vXndl4wN5TpxM9ikeEOewcqzAQIhf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw3Mzk5MzkxNzM4MTkiDECCD%2BjDRWx3XR5WOiqgBMolRrwA3xK06WhhRf2WYo3EOy4pasGkHbi%2Bu0zoZU7YoOctvtfkKdcLFimPChUiYgClfa%2FhzeA1dSSDDG9xOzQ9HpFa1BVMmkMBZYoCB85nCAq8tRXkxBcuzzEDKdrYNRpUzmP6SVuVh%2B7kZ5qbrRWgGH5B2Gcktv2YT7eE2DFAUZ6%2Fq25eR9N1%2B6lig5Ei37l6FQLeScT%2FhO2yB3yZCyzGCjIGvAffsFEQTmY3TT7rgleIRanfyBsZiZYS5PnIS41L1NblIdVQhNxhlEczib5cjvxbDR6l13wbmKDgdDG8cre1viUdv%2BL1KANYcjwJhJfQDk3Haa%2B2LpTdNaz%2B9opWEjfnZ4%2BzQqF7t8xIxTyCiq2%2FJ%2BzcVdJ5Pqv6O9UrbzYH2PlspPvyBioYnwtCqp1jmDJZjX2AwNZboR0oSLQS30yETHRZ94Wm00m6s%2BVjOJsAQ%2FxwAMddVxWFvzovZa%2FlaTsUbVCwcYU5KUYRq1exAeSwtz4pxwFdkn1xYcNtr08m2rOY2IzbHoWZ0XdDLum4UI0mw8ynh%2FlOdcSJ89aPy3M5SJR9WUD3zD5PTXeWwDVXyeN9JCFVP4CwBt6ndJvrp5jtpJ8H9fLjLDWIJoK5nNV0L2Uq9R6bSNf%2Fy8D%2F6kQcy8cNDPJm5QL3vyDsAQriO0NKitOGP4LxrzpunVK6Fe5jl5nEW7yIBeYEEMc2Q060ER1SKAlvMJo0hxJtkcYwqsbznQY6pgHf0i6JTl%2FKdiQNttxLmNcN2QCW42FWa7rsvpDPacuZqY7ByIR4Cfy1hFTk2XSC%2B7GMxjy%2F08d0FjSKHotLfN43h7ebx2pQ0LM2rSWy9r052mPgO4T4DDWX5%2FgBDE%2Bwz4ODdSUP%2BqXQbluNbKHCqzgOa5whJAbJUETKPnMirv4Ro%2Bu3W5cdBd0cmRJRU4vrQ07qlFlk1GJZmfdH4Nq5C38DxBYseRtz&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230110T042227Z&X-Amz-SignedHeaders=host&X-Amz-Expires=600&X-Amz-Credential=ASIA2YR6PYW5YSI4S5V3%2F20230110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=977edcb7b7ef06ee67e572f8c62d420f60eeee7f4ca610b6875adc8b78ab0185",
                                "screenshotImageLarge": "https://upwork-usw2-prod-agora-tracker.s3.us-west-2.amazonaws.com/tracker_resized/s/31312642/2023/1/9/1673241510-lrg?X-Amz-Security-Token=IQoJb3JpZ2luX2VjECwaCXVzLXdlc3QtMiJHMEUCIEovVfMupjvjrFeSoZlefpETvSVETJuY1x6agDp2dMiEAiEAynb420qj3DjlgolaIz9c2vXndl4wN5TpxM9ikeEOewcqzAQIhf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw3Mzk5MzkxNzM4MTkiDECCD%2BjDRWx3XR5WOiqgBMolRrwA3xK06WhhRf2WYo3EOy4pasGkHbi%2Bu0zoZU7YoOctvtfkKdcLFimPChUiYgClfa%2FhzeA1dSSDDG9xOzQ9HpFa1BVMmkMBZYoCB85nCAq8tRXkxBcuzzEDKdrYNRpUzmP6SVuVh%2B7kZ5qbrRWgGH5B2Gcktv2YT7eE2DFAUZ6%2Fq25eR9N1%2B6lig5Ei37l6FQLeScT%2FhO2yB3yZCyzGCjIGvAffsFEQTmY3TT7rgleIRanfyBsZiZYS5PnIS41L1NblIdVQhNxhlEczib5cjvxbDR6l13wbmKDgdDG8cre1viUdv%2BL1KANYcjwJhJfQDk3Haa%2B2LpTdNaz%2B9opWEjfnZ4%2BzQqF7t8xIxTyCiq2%2FJ%2BzcVdJ5Pqv6O9UrbzYH2PlspPvyBioYnwtCqp1jmDJZjX2AwNZboR0oSLQS30yETHRZ94Wm00m6s%2BVjOJsAQ%2FxwAMddVxWFvzovZa%2FlaTsUbVCwcYU5KUYRq1exAeSwtz4pxwFdkn1xYcNtr08m2rOY2IzbHoWZ0XdDLum4UI0mw8ynh%2FlOdcSJ89aPy3M5SJR9WUD3zD5PTXeWwDVXyeN9JCFVP4CwBt6ndJvrp5jtpJ8H9fLjLDWIJoK5nNV0L2Uq9R6bSNf%2Fy8D%2F6kQcy8cNDPJm5QL3vyDsAQriO0NKitOGP4LxrzpunVK6Fe5jl5nEW7yIBeYEEMc2Q060ER1SKAlvMJo0hxJtkcYwqsbznQY6pgHf0i6JTl%2FKdiQNttxLmNcN2QCW42FWa7rsvpDPacuZqY7ByIR4Cfy1hFTk2XSC%2B7GMxjy%2F08d0FjSKHotLfN43h7ebx2pQ0LM2rSWy9r052mPgO4T4DDWX5%2FgBDE%2Bwz4ODdSUP%2BqXQbluNbKHCqzgOa5whJAbJUETKPnMirv4Ro%2Bu3W5cdBd0cmRJRU4vrQ07qlFlk1GJZmfdH4Nq5C38DxBYseRtz&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230110T042227Z&X-Amz-SignedHeaders=host&X-Amz-Expires=600&X-Amz-Credential=ASIA2YR6PYW5YSI4S5V3%2F20230110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=35256f0472ca6692d9e8a8c53565e7144e43e866ceae48b548775cb4aaf7a78e",
                                "screenshotImageMedium": "https://upwork-usw2-prod-agora-tracker.s3.us-west-2.amazonaws.com/tracker_resized/s/31312642/2023/1/9/1673241510-med?X-Amz-Security-Token=IQoJb3JpZ2luX2VjECwaCXVzLXdlc3QtMiJHMEUCIEovVfMupjvjrFeSoZlefpETvSVETJuY1x6agDp2dMiEAiEAynb420qj3DjlgolaIz9c2vXndl4wN5TpxM9ikeEOewcqzAQIhf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw3Mzk5MzkxNzM4MTkiDECCD%2BjDRWx3XR5WOiqgBMolRrwA3xK06WhhRf2WYo3EOy4pasGkHbi%2Bu0zoZU7YoOctvtfkKdcLFimPChUiYgClfa%2FhzeA1dSSDDG9xOzQ9HpFa1BVMmkMBZYoCB85nCAq8tRXkxBcuzzEDKdrYNRpUzmP6SVuVh%2B7kZ5qbrRWgGH5B2Gcktv2YT7eE2DFAUZ6%2Fq25eR9N1%2B6lig5Ei37l6FQLeScT%2FhO2yB3yZCyzGCjIGvAffsFEQTmY3TT7rgleIRanfyBsZiZYS5PnIS41L1NblIdVQhNxhlEczib5cjvxbDR6l13wbmKDgdDG8cre1viUdv%2BL1KANYcjwJhJfQDk3Haa%2B2LpTdNaz%2B9opWEjfnZ4%2BzQqF7t8xIxTyCiq2%2FJ%2BzcVdJ5Pqv6O9UrbzYH2PlspPvyBioYnwtCqp1jmDJZjX2AwNZboR0oSLQS30yETHRZ94Wm00m6s%2BVjOJsAQ%2FxwAMddVxWFvzovZa%2FlaTsUbVCwcYU5KUYRq1exAeSwtz4pxwFdkn1xYcNtr08m2rOY2IzbHoWZ0XdDLum4UI0mw8ynh%2FlOdcSJ89aPy3M5SJR9WUD3zD5PTXeWwDVXyeN9JCFVP4CwBt6ndJvrp5jtpJ8H9fLjLDWIJoK5nNV0L2Uq9R6bSNf%2Fy8D%2F6kQcy8cNDPJm5QL3vyDsAQriO0NKitOGP4LxrzpunVK6Fe5jl5nEW7yIBeYEEMc2Q060ER1SKAlvMJo0hxJtkcYwqsbznQY6pgHf0i6JTl%2FKdiQNttxLmNcN2QCW42FWa7rsvpDPacuZqY7ByIR4Cfy1hFTk2XSC%2B7GMxjy%2F08d0FjSKHotLfN43h7ebx2pQ0LM2rSWy9r052mPgO4T4DDWX5%2FgBDE%2Bwz4ODdSUP%2BqXQbluNbKHCqzgOa5whJAbJUETKPnMirv4Ro%2Bu3W5cdBd0cmRJRU4vrQ07qlFlk1GJZmfdH4Nq5C38DxBYseRtz&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230110T042227Z&X-Amz-SignedHeaders=host&X-Amz-Expires=600&X-Amz-Credential=ASIA2YR6PYW5YSI4S5V3%2F20230110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=98a0c640371243f3f7287eb39b710b0237451efb8ea120e44d2750670d4529f0",
                                "screenshotImageThumbnail": "https://upwork-usw2-prod-agora-tracker.s3.us-west-2.amazonaws.com/tracker_resized/s/31312642/2023/1/9/1673241510-thmb?X-Amz-Security-Token=IQoJb3JpZ2luX2VjECwaCXVzLXdlc3QtMiJHMEUCIEovVfMupjvjrFeSoZlefpETvSVETJuY1x6agDp2dMiEAiEAynb420qj3DjlgolaIz9c2vXndl4wN5TpxM9ikeEOewcqzAQIhf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw3Mzk5MzkxNzM4MTkiDECCD%2BjDRWx3XR5WOiqgBMolRrwA3xK06WhhRf2WYo3EOy4pasGkHbi%2Bu0zoZU7YoOctvtfkKdcLFimPChUiYgClfa%2FhzeA1dSSDDG9xOzQ9HpFa1BVMmkMBZYoCB85nCAq8tRXkxBcuzzEDKdrYNRpUzmP6SVuVh%2B7kZ5qbrRWgGH5B2Gcktv2YT7eE2DFAUZ6%2Fq25eR9N1%2B6lig5Ei37l6FQLeScT%2FhO2yB3yZCyzGCjIGvAffsFEQTmY3TT7rgleIRanfyBsZiZYS5PnIS41L1NblIdVQhNxhlEczib5cjvxbDR6l13wbmKDgdDG8cre1viUdv%2BL1KANYcjwJhJfQDk3Haa%2B2LpTdNaz%2B9opWEjfnZ4%2BzQqF7t8xIxTyCiq2%2FJ%2BzcVdJ5Pqv6O9UrbzYH2PlspPvyBioYnwtCqp1jmDJZjX2AwNZboR0oSLQS30yETHRZ94Wm00m6s%2BVjOJsAQ%2FxwAMddVxWFvzovZa%2FlaTsUbVCwcYU5KUYRq1exAeSwtz4pxwFdkn1xYcNtr08m2rOY2IzbHoWZ0XdDLum4UI0mw8ynh%2FlOdcSJ89aPy3M5SJR9WUD3zD5PTXeWwDVXyeN9JCFVP4CwBt6ndJvrp5jtpJ8H9fLjLDWIJoK5nNV0L2Uq9R6bSNf%2Fy8D%2F6kQcy8cNDPJm5QL3vyDsAQriO0NKitOGP4LxrzpunVK6Fe5jl5nEW7yIBeYEEMc2Q060ER1SKAlvMJo0hxJtkcYwqsbznQY6pgHf0i6JTl%2FKdiQNttxLmNcN2QCW42FWa7rsvpDPacuZqY7ByIR4Cfy1hFTk2XSC%2B7GMxjy%2F08d0FjSKHotLfN43h7ebx2pQ0LM2rSWy9r052mPgO4T4DDWX5%2FgBDE%2Bwz4ODdSUP%2BqXQbluNbKHCqzgOa5whJAbJUETKPnMirv4Ro%2Bu3W5cdBd0cmRJRU4vrQ07qlFlk1GJZmfdH4Nq5C38DxBYseRtz&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230110T042227Z&X-Amz-SignedHeaders=host&X-Amz-Expires=599&X-Amz-Credential=ASIA2YR6PYW5YSI4S5V3%2F20230110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Signature=95c7c8594fb9525dc6980bbd3627f42dc3bf55b5ac36c5f5813f167f85f59e90",
                                "hasWebcam": "",
                                "webcamUrl": "",
                                "webcamImage": "",
                                "webcamImageThumbnail": ""
                            }
                        ]
                    }
                ]
            }
        }
    }
    mock_get_work_diary.return_value = UpworkDiarySchema().load(json_work_diaries.get('data').get('workDiaryCompany'))

    # save and process upwork diaries (dates in query params don't matter because the response is mocked)
    res = app.test_client().get(
        f'/api/v1/backoffice/upwork-diary',
        headers={'X-BEE-AUTH': inner_token},
        query_string={'startDate': '20230101', 'endDate': '20230101'}
    )
    assert res.status_code == 200
    assert res.json['status'] == 'ok'
    assert len(res.json['data']) == len(mock_get_work_diary.return_value.get('snapshots'))
    upwork_diary_ids = [d.get('id') for d in res.json['data']]

    with app.app_context():
        work_record_upwork_diary = WorkRecordUpworkDiary.query.filter(WorkRecordUpworkDiary.work_record_id.in_(work_record_ids)).all()
        assert len(work_record_upwork_diary) == 2
        assert work_record_upwork_diary[0].upwork_diary_id == upwork_diary_ids[0]
        assert work_record_upwork_diary[1].upwork_diary_id == upwork_diary_ids[1]

    # job should not change anything because task hasn't been accepted *yesterday*
    with app.app_context():
        find_net_duration_cuckoo_accepted_tasks.queue()

    assert mock_dispatch_cuckoo_event_job.call_count == 0
    assert mock_get_praesepe_authorization_code.call_count == 3

    with app.app_context():
        task = Task.query.filter_by(id=task_id).first()
        assert task.total_net_duration_seconds is None

        # modify task updated timestamp to yesterday
        task.updated = datetime.utcnow() - timedelta(days=1)
        db.session.commit()

    # job should notify cuckoo about tasks total net duration
    with app.app_context():
        find_net_duration_cuckoo_accepted_tasks.queue()

    assert mock_dispatch_cuckoo_event_job.call_count == 1

    with app.app_context():
        task = Task.query.filter_by(id=task_id).first()
        work_record_upwork_diary = WorkRecordUpworkDiary.query.filter(WorkRecordUpworkDiary.work_record_id.in_(work_record_ids)).all()
        assert task.total_net_duration_seconds == work_record_upwork_diary[0].upwork_duration_seconds + work_record_upwork_diary[1].upwork_duration_seconds
