import csv
from datetime import datetime, timedelta
from io import StringIO
import json
import os

from unittest.mock import patch, Mock
import pytest
from src.models.user import User

from src.schemas.upwork import UpworkDiarySchema
from src.utils.upwork import UpworkClient
from src.utils.db import db
from src.models.upwork import UpworkDiary, WorkRecordUpworkDiary


@patch.object(UpworkClient, 'get_access_token', return_value={"access_token": "oauth2v2_1e3704277095e1a98ba48ea3e2928ab2","refresh_token": "oauth2v2_98a2b87a42e9c68db1236d4fa05f76bb","token_type": "Bearer","expires_in": 86400,"expires_at": "1712730000"})
@patch.object(UpworkClient, 'get_organization_id', return_value='nkzlfefsnelbn4opkwhnra')
@patch.object(UpworkClient, 'refresh_token', return_value={"access_token": "oauth2v2_1e3704277095e1a98ba48ea3e2928ab2","refresh_token": "oauth2v2_98a2b87a42e9c68db1236d4fa05f76bb","token_type": "Bearer","expires_in": 86400,"expires_at": "1712730000"})
def test_upwork_callback(mock_refresh_token, mock_get_organization_id, mock_get_access_token, app):

    # no code request parameter
    res = app.test_client().get(
        f'/api/v1/upwork-callback?state=example-state'
    )
    assert res.status_code == 400
    assert res.json['status'] == 'error'
    assert res.json['error'] == 'malformed_request'
    assert res.json['description'].startswith('code parameter is not found in callback url query string:')

    # no state request parameter should succeed
    res = app.test_client().get(
        f'/api/v1/upwork-callback?code=example-code'
    )

    assert res.status_code == 200
    assert res.json['status'] == 'ok'
    assert res.json['data']['access_token'] == mock_get_access_token.return_value.get('access_token')
    assert res.json['data']['refresh_token'] == mock_get_access_token.return_value.get('refresh_token')
    assert res.json['data']['token_type'] == mock_get_access_token.return_value.get('token_type')
    assert res.json['data']['expires_in'] == mock_get_access_token.return_value.get('expires_in')
    assert res.json['data']['expires_at'] == mock_get_access_token.return_value.get('expires_at')

    res = app.test_client().get(
        f'/api/v1/upwork-callback?code=example-code&state=example-state'
    )
    assert res.status_code == 200
    assert res.json['status'] == 'ok'
    assert res.json['data']['access_token'] == mock_get_access_token.return_value.get('access_token')
    assert res.json['data']['refresh_token'] == mock_get_access_token.return_value.get('refresh_token')
    assert res.json['data']['token_type'] == mock_get_access_token.return_value.get('token_type')
    assert res.json['data']['expires_in'] == mock_get_access_token.return_value.get('expires_in')
    assert res.json['data']['expires_at'] == mock_get_access_token.return_value.get('expires_at')


@patch.object(UpworkClient, 'get_work_diary')
@patch.object(UpworkClient, 'get_organization_id', return_value='nkzlfefsnelbn4opkwhnra')
@patch.object(UpworkClient, 'refresh_token', return_value={"access_token": "oauth2v2_1e3704277095e1a98ba48ea3e2928ab2","refresh_token": "oauth2v2_98a2b87a42e9c68db1236d4fa05f76bb","token_type": "Bearer","expires_in": 86400,"expires_at": "1712730000"})
@patch('src.utils.upwork.UpworkAuthToken.get_recent_token', return_value={"access_token":"access_token","refresh_token":"refresh_token","token_type":"token_type","expires_in":1,"expires_at":1111.111})
def test_upwork_workdiary(mock_get_recent_token, mock_refresh_token, mock_get_organizaion_id, mock_get_work_diary, app, active_token, inner_token):
    # load mock json response
    file = str(os.path.join(os.path.dirname(__file__), '..', 'mocks', 'upwork_diary_response.json'))
    with open(file) as f:
        json_work_diaries = json.load(f)
    mock_get_work_diary.return_value = UpworkDiarySchema().load(json_work_diaries.get('data').get('workDiaryCompany'))

    res = app.test_client().get(
        f'/api/v1/backoffice/upwork-diary'
    )
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}

    # normal jwt won't work
    res = app.test_client().get(
        f'/api/v1/backoffice/upwork-diary',
        headers={'Authorization': f'Bearer {active_token}'},
    )
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}
        
    # only inner token succeeds
    res = app.test_client().get(
        f'/api/v1/backoffice/upwork-diary',
        headers={'X-BEE-AUTH': inner_token},
        query_string={'startDate': '20230101', 'endDate': '20230101'}
    )
    assert res.status_code == 200
    assert res.json['status'] == 'ok'
    assert len(res.json['data']) == len(mock_get_work_diary.return_value.get('snapshots'))

    # remove created upwork diary objects
    upwork_diary_ids = [d.get('id') for d in res.json['data']]

    with app.app_context():
        UpworkDiary.query.filter(UpworkDiary.id.in_(upwork_diary_ids)).delete(synchronize_session=False)
        db.session.commit()

@patch.object(UpworkClient, 'get_work_diary')
@patch.object(UpworkClient, 'get_organization_id', return_value='nkzlfefsnelbn4opkwhnra')
@patch.object(UpworkClient, 'refresh_token', return_value={"access_token": "oauth2v2_1e3704277095e1a98ba48ea3e2928ab2","refresh_token": "oauth2v2_98a2b87a42e9c68db1236d4fa05f76bb","token_type": "Bearer","expires_in": 86400,"expires_at": "1712730000"})
@patch('src.utils.upwork.UpworkAuthToken.get_recent_token', return_value={"access_token":"access_token","refresh_token":"refresh_token","token_type":"token_type","expires_in":1,"expires_at":1111.111})
def test_upwork_cost_report_no_work_records(mock_get_recent_token, mock_refresh_token, mock_get_organization_id, mock_get_work_diary, app, admin_token, inner_token):
    # load mock json response
    file = str(os.path.join(os.path.dirname(__file__), '..', 'mocks', 'upwork_diary_response.json'))
    with open(file) as f:
        json_work_diaries = json.load(f)
    mock_get_work_diary.return_value = UpworkDiarySchema().load(json_work_diaries.get('data').get('workDiaryCompany'))
   
    # get_work_diary mock called per day, so we're testing on only one day
    start_date = '20231210'
    end_date = '20231210'

    # insert upwork diaries to database
    res = app.test_client().get(
        f'/api/v1/backoffice/upwork-diary',
        headers={'X-BEE-AUTH': inner_token},
        query_string={'startDate': start_date, 'endDate': end_date}
    )
    assert res.status_code == 200
    assert res.json['status'] == 'ok'
    assert len(res.json['data']) == len(mock_get_work_diary.return_value.get('snapshots'))

    # inner token unauthorized
    res = app.test_client().get(
        f'/api/v1/backoffice/cost-report',
        headers={'X-BEE-AUTH': inner_token},
        query_string={'startDate': start_date, 'endDate': end_date}
    )
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}

    # get cost report with admin token
    expected_filename = f'cost_{start_date}-{end_date}.csv'
    cost_report_headers = ['ID','Upwork user id','Upwork user name','Upwork interval','Upwork duration','Upwork cost','Net duration','Work Record id','Work id','Task id','Task name','User id','User name','Project','Skills','Work Record interval','Work Record duration']
    res = app.test_client().get(
        f'/api/v1/backoffice/cost-report',
        headers={'Authorization': f'Bearer {admin_token}'},
        query_string={'startDate': start_date, 'endDate': end_date}
    )
    assert res.status_code == 200
    assert res.headers['Content-Disposition'] == f'attachment; filename={expected_filename}'
    assert res.headers['Content-Type'] == 'text/csv; charset=utf-8'
    
    reader = csv.reader(res.text.split('\n'), delimiter=',')
    rows = [row for row in reader if len(row)>0]
    headers = rows.pop(0)
    assert cost_report_headers == headers
    assert len(rows) == mock_get_work_diary.return_value.get('total')

    # remove created upwork diary objects
    upwork_diary_ids = [row[0] for row in rows]

    with app.app_context():
        UpworkDiary.query.filter(UpworkDiary.id.in_(upwork_diary_ids)).delete(synchronize_session=False)
        db.session.commit()


@patch('src.resources.work.get_praesepe_authorization_code', new=Mock())
@patch('src.resources.work.dispatch_cuckoo_event', new=Mock())
@patch.object(UpworkClient, 'get_work_diary')
@patch.object(UpworkClient, 'get_organization_id', return_value='nkzlfefsnelbn4opkwhnra')
@patch.object(UpworkClient, 'refresh_token', return_value={"access_token": "oauth2v2_1e3704277095e1a98ba48ea3e2928ab2","refresh_token": "oauth2v2_98a2b87a42e9c68db1236d4fa05f76bb","token_type": "Bearer","expires_in": 86400,"expires_at": "1712730000"})
@patch('src.utils.upwork.UpworkAuthToken.get_recent_token', return_value={"access_token":"access_token","refresh_token":"refresh_token","token_type":"token_type","expires_in":1,"expires_at":1111.111})
@patch('src.resources.work.run_beehave_pr_github_bot', new=Mock())
def test_upwork_cost_report_with_matching_work_records(mock_get_recent_token, mock_refresh_token, mock_get_organization_id, mock_get_work_diary, app, admin_token, inner_token, active_token, active_token_user_id):
    # load mock json response from upwork
    file = str(os.path.join(os.path.dirname(__file__), '..', 'mocks', 'upwork_diary_response.json'))
    with open(file) as f:
        json_work_diaries = json.load(f)
    
    # work record start time cannot be too much in the past (schema validator) and should overlap with upwork diaries mock data
    def unix_time_ms(dt):
        return int((dt - datetime.utcfromtimestamp(0)).total_seconds() * 1000)

    start_time = datetime.utcnow() - timedelta(minutes=4)
    start_time_epoch_ms = unix_time_ms(start_time)

    # update mock data start time so some work records and upwork diaries overlap with 10 minutes
    first_worked_int = int((start_time_epoch_ms / 1000) - (5 * 60))
    json_work_diaries['data']['workDiaryCompany']['snapshots'][3]['time']['firstWorkedInt'] = first_worked_int
    json_work_diaries['data']['workDiaryCompany']['snapshots'][3]['time']['lastWorkedInt'] = first_worked_int + 28*60
    mock_get_work_diary.return_value = UpworkDiarySchema().load(json_work_diaries.get('data').get('workDiaryCompany'))
   
    # create task that was worked on at the same time period as upwork diaries
    with app.app_context():
        trello_user = User.query.filter_by(id=active_token_user_id).first().trello_user

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
    test_upwork_cost_report_with_matching_work_records.task_ids = [task_id]

    # get available work should return a single work item
    res = app.test_client().get('api/v1/work/available', headers={'Authorization': f'Bearer {active_token}'})
    assert res.status_code == 200
    assert res.json['data']['work']['taskId'] == task_id
    work_id = res.json['data']['work']['id']

    res = app.test_client().post(
        f'api/v1/work/start',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work_id, 'startTimeEpochMs': start_time_epoch_ms, 'tzName': 'UTC'}
    )
    assert res.status_code == 200

    # finish work with some solution code after 20 minutes
    duration_seconds = 20 * 60
    res = app.test_client().post(
        f'api/v1/work/finish',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'workId': work_id, 'durationSeconds': duration_seconds, 'solutionUrl': 'https://github.com/my-org/my-repo/pull/1'}
    )
    assert res.status_code == 200

    # get_work_diary mock called once per day, so we're testing on only one day to avoid duplicates
    start_date = '20231210'
    end_date = datetime.utcnow().strftime('%Y%m%d')

    # insert upwork diaries to database
    res = app.test_client().get(
        f'/api/v1/backoffice/upwork-diary',
        headers={'X-BEE-AUTH': inner_token},
        query_string={'startDate': start_date, 'endDate': start_date}
    )
    assert res.status_code == 200
    assert res.json['status'] == 'ok'
    assert len(res.json['data']) == len(mock_get_work_diary.return_value.get('snapshots'))

    # get cost report with admin token
    expected_filename = f'cost_{start_date}-{end_date}.csv'
    res = app.test_client().get(
        f'/api/v1/backoffice/cost-report',
        headers={'Authorization': f'Bearer {admin_token}'},
        query_string={'startDate': start_date, 'endDate': end_date}
    )
    assert res.status_code == 200
    assert res.headers['Content-Disposition'] == f'attachment; filename={expected_filename}'
    assert res.headers['Content-Type'] == 'text/csv; charset=utf-8'

    csv_reader = csv.DictReader(StringIO(res.text), delimiter=',')
    data = [row for row in csv_reader]
    assert len(data) == mock_get_work_diary.return_value.get('total')
    assert data[3]['Net duration'] != ''
    assert data[3]['Work Record id'] != ''
    assert data[0]['Net duration'] == ''
    assert data[0]['Work Record id'] == ''
    assert data[1]['Net duration'] == ''
    assert data[1]['Work Record id'] == ''
    assert data[2]['Net duration'] == ''
    assert data[2]['Work Record id'] == ''

    # remove created upwork diary objects
    upwork_diary_ids = [row["ID"] for row in data]

    with app.app_context():
        WorkRecordUpworkDiary.query.filter(WorkRecordUpworkDiary.upwork_diary_id.in_(upwork_diary_ids)).delete(synchronize_session=False)
        UpworkDiary.query.filter(UpworkDiary.id.in_(upwork_diary_ids)).delete(synchronize_session=False)
        db.session.commit()
