import time
from flask_jwt_extended import create_access_token, decode_token
import pytest

from src import app as flask_app
from src.models.project import Project, ProjectDelegator
from src.models.repository import Repository
from src.models.skill import Skill, TaskTemplateSkill
from src.models.task import TaskType
from src.models.task_classification import TaskTypeClassification
from src.models.task_template import TaskTemplate
from src.models.user import User
from src.utils.db import db
from src.utils.rq import rq


@pytest.fixture
def app():
    app = flask_app.create_app('testing')

    yield app


@pytest.fixture
def active_token(request, app):
    user_email = f'user-{int(time.time() * 1000)}@test.test'

    # register user for access token
    res = app.test_client().post('api/v1/signup', json={'email': user_email, 'password': '1234', 'code': app.config['USER_REGISTRATION_OVERRIDE_CODE']})
    assert res.status_code == 200

    user_id = res.json['data']['userId']

    with app.app_context():
        # activate user
        user = User.query.filter_by(id=user_id).first()
        user.activated = True
        user.trello_user = 'test-trello-user'   # used for validating cuckoo service worflow
        user.github_user = 'test-github-user'   # used for sending to cuckoo service for creating github access
        user.upwork_user = 'test-upwork-user'   # used for validating upwork diaries
        db.session.commit()

    # sign in to receive a new token indicating the user is an admin
    res = app.test_client().post('api/v1/signin', json={'email': user_email, 'password': '1234'})
    assert res.status_code == 200

    access_token = res.json['data']['accessToken']

    yield access_token

    # teardown - remove created tasks
    task_ids = getattr(request.function, 'task_ids', [])

    for task_id in task_ids:
        # delete task
        res = app.test_client().delete(
            f'api/v1/task/{task_id}',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        assert res.status_code == 200

        # task does not exist
        res = app.test_client().get(
            f'api/v1/task/{task_id}',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        assert res.status_code == 404
        assert res.json == {'status': 'error', 'error': 'not_found'}

    # teardown - remove created quests
    quest_ids = getattr(request.function, 'quest_ids', [])

    for quest_id in quest_ids:
        # delete quest
        res = app.test_client().delete(
            f'api/v1/quest/{quest_id}',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        assert res.status_code == 200

        # query does not exist
        res = app.test_client().get(
            f'api/v1/quest/{quest_id}',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        assert res.status_code == 404
        assert res.json == {'status': 'error', 'error': 'not_found'}

    with app.app_context():
        # teardown - remove created user
        db.session.delete(user)
        db.session.commit()

        # user does not exist
        assert User.query.filter_by(id=user_id).first() is None

@pytest.fixture
def second_active_token(app):
    user_email = f'user-{int(time.time() * 1000)}@test.test'

    # register user for access token
    res = app.test_client().post('api/v1/signup', json={'email': user_email, 'password': '1234', 'code': app.config['USER_REGISTRATION_OVERRIDE_CODE']})
    assert res.status_code == 200

    user_id = res.json['data']['userId']

    with app.app_context():
        # activate user
        user = User.query.filter_by(id=user_id).first()
        user.activated = True
        user.trello_user = 'test-trello-second-user'   # used for validating cuckoo service worflow
        user.github_user = 'test-github-second-user'   # used for sending to cuckoo service for creating github access
        user.upwork_user = 'test-upwork-second-user'   # used for validating upwork diaries
        db.session.commit()

    # sign in to receive a new token indicating the user is an admin
    res = app.test_client().post('api/v1/signin', json={'email': user_email, 'password': '1234'})
    assert res.status_code == 200

    access_token = res.json['data']['accessToken']

    yield access_token

    with app.app_context():
        # teardown - remove created user
        db.session.delete(user)
        db.session.commit()

        # user does not exist
        assert User.query.filter_by(id=user_id).first() is None


@pytest.fixture
def admin_token(app):
    user_email = f'user-{int(time.time() * 1000)}@test.test'

    # register user for access token
    res = app.test_client().post('api/v1/signup', json={'email': user_email, 'password': '1234', 'code': app.config['USER_REGISTRATION_OVERRIDE_CODE']})
    assert res.status_code == 200

    user_id = res.json['data']['userId']

    with app.app_context():
        # activate user and make it an admin
        user = User.query.filter_by(id=user_id).first()
        user.activated = True
        user.admin = True
        db.session.commit()

    # sign in to receive a new token indicating the user is an admin
    res = app.test_client().post('api/v1/signin', json={'email': user_email, 'password': '1234'})
    assert res.status_code == 200

    access_token = res.json['data']['accessToken']

    yield access_token

    with app.app_context():
        # teardown - remove created user
        db.session.delete(user)
        db.session.commit()

        # user does not exist
        assert User.query.filter_by(id=user_id).first() is None


@pytest.fixture
def active_token_user_id(app, active_token):
    with app.app_context():
        # decode token and extract identity
        user_id = decode_token(active_token)['sub']

    yield user_id


@pytest.fixture
def second_active_token_user_id(app, second_active_token):
    with app.app_context():
        # decode token and extract identity
        user_id = decode_token(second_active_token)['sub']

    yield user_id


@pytest.fixture
def inner_token(app):
    yield app.config['INTER_SERVICE_AUTH_KEYS'][0]


@pytest.fixture
def rq_prepare_task_async_worker(app):
    # import here since importing the job requires an initialized flask app
    from src.jobs.task import prepare_task, prepare_cuckoo_task

    # get prepare task's queue and set it manually to async
    prepare_task_queue = rq.get_queue(prepare_task.helper.queue_name)
    prepare_task_queue._is_async = True

    # get prepare task's queue and set it manually to async
    prepare_cuckoo_task_queue = rq.get_queue(prepare_cuckoo_task.helper.queue_name)
    prepare_cuckoo_task_queue._is_async = True

    yield rq.get_worker()

    # revert queue async change
    prepare_task_queue._is_async = False
    prepare_cuckoo_task_queue._is_async = False


@pytest.fixture
def system_token(request, app):
    # create token manually since system user login is forbidden
    system_user_token = create_access_token(
        identity=app.config['SYSTEM_USER_ID'],
        user_claims={'activated': True}
    )

    yield system_user_token

    # teardown - remove created tasks
    task_ids = getattr(request.function, 'honeycomb_task_ids', [])

    for task_id in task_ids:
        # delete task
        res = app.test_client().delete(
            f'api/v1/task/{task_id}',
            headers={'Authorization': f'Bearer {system_user_token}'}
        )
        assert res.status_code == 200

        # task does not exist
        res = app.test_client().get(
            f'api/v1/task/{task_id}',
            headers={'Authorization': f'Bearer {system_user_token}'}
        )
        assert res.status_code == 404
        assert res.json == {'status': 'error', 'error': 'not_found'}

@pytest.fixture
def delegation(app, active_token_user_id, active_token):
    with app.app_context():
        project_id = 9999
        repo_id = 9999

        project = Project(project_id, 'test_project', 'missing', 'https://trello.com/b/hDjTIvGt/cuckoo-test')
        repo = Repository(repo_id, 'test_repo', 'test_url', project_id)
        template = TaskTemplate('test_name', 'test_description', TaskType.UPDATE_FUNCTION, repo_id, [Skill.get_or_create('test-skill')])
        delegator_link = ProjectDelegator(active_token_user_id, project_id)

        db.session.add(project)
        db.session.commit()
        db.session.add(repo)
        db.session.add(template)
        db.session.add(delegator_link)
        db.session.commit()

        yield project, repo, template

        # teardown
        db.session.delete(delegator_link)
        ts = TaskTemplateSkill.query.filter_by(task_template_id=template.id).first()
        db.session.delete(ts)
        db.session.delete(delegator_link)
        db.session.delete(template)
        db.session.delete(repo)
        db.session.delete(project)
        

        db.session.commit()
