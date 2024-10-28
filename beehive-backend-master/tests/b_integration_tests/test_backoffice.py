from datetime import datetime, timedelta
import time

from freezegun import freeze_time

from src.models.task import TaskStatus, TaskType
from src.models.tag import Tag
from src.models.skill import Skill


def test_backoffice_put_user_profile_endpoint_no_bee_key(app, active_token):
    user_id = f'user-{int(time.time() * 1000)}'

    # put user profile update requires backoffice auth
    res = app.test_client().put(f'api/v1/backoffice/user-profile/{user_id}', json={'tags': ['a-tag']})
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}

    # normal jwt won't work
    res = app.test_client().put(
        f'api/v1/backoffice/user-profile/{user_id}', 
        headers={'Authorization': f'Bearer {active_token}'},
        json={'tags': ['a-tag']})
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}

    # wrong backoffice key will be rejected
    res = app.test_client().put(
        f'api/v1/backoffice/user-profile/{user_id}', 
        headers={'X-BEE-AUTH': 'bad-token'},
        json={'tags': ['a-tag']}
    )
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}


def test_backoffice_get_user_profile_endpoint_no_bee_key(app, active_token):
    user_id = f'user-{int(time.time() * 1000)}'

    # get user profile requires backoffice auth
    res = app.test_client().get(f'api/v1/backoffice/user-profile/{user_id}')
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}

    # normal jwt won't work
    res = app.test_client().get(
        f'api/v1/backoffice/user-profile/{user_id}', 
        headers={'Authorization': f'Bearer {active_token}'}
    )    
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}

    # wrong backoffice key will be rejected
    res = app.test_client().get(
        f'api/v1/backoffice/user-profile/{user_id}', 
        headers={'X-BEE-AUTH': 'bad-token'}
    )
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}


def test_backoffice_delete_user_profile_endpoint_no_bee_key(app, active_token):
    user_id = f'user-{int(time.time() * 1000)}'

    # delete user profile requires backoffice auth
    res = app.test_client().delete(f'api/v1/backoffice/user-profile/{user_id}', json={'tags': ['a-tag']})
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}

    # normal jwt won't work
    res = app.test_client().delete(
        f'api/v1/backoffice/user-profile/{user_id}', 
        headers={'Authorization': f'Bearer {active_token}'},
        json={'tags': ['a-tag']})
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}

    # wrong backoffice key will be rejected
    res = app.test_client().delete(
        f'api/v1/backoffice/user-profile/{user_id}', 
        headers={'X-BEE-AUTH': 'bad-token'},
        json={'tags': ['a-tag']}
    )
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}


def test_backoffice_put_user_profile_endpoint_success(
    app, active_token, active_token_user_id, inner_token
):
    # updating profile works
    new_tags = ['random-tag','another-tag']
    new_skills = ['random-skill']

    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'tags': new_tags,
            'skills': new_skills
        }
    )
    assert res.status_code == 200

    # the entities should exist now
    res = app.test_client().get(
        'api/v1/backoffice/tag',
        headers={'X-BEE-AUTH': inner_token}
    )
    assert res.status_code == 200
    created_tags = [p['name'] for p in res.json['data'] if p['name'] in new_tags]
    assert sorted(new_tags) == sorted(created_tags)

    res = app.test_client().get(
        'api/v1/skill',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    created_skills = [p['name'] for p in res.json['data'] if p['name'] in new_skills]
    assert sorted(new_skills) == sorted(created_skills)

    # user profile should be updated with these entities only
    res = app.test_client().get(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token}
    )
    assert res.status_code == 200
    assert sorted(res.json['tags']) == sorted(new_tags)
    assert sorted(res.json['skills']) == sorted(new_skills)

    # delete entities we created
    res = app.test_client().delete(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={
            'tags': new_tags,
            'skills': new_skills
        }
    )
    assert res.status_code == 200
    assert not any(item in new_tags for item in res.json['tags'])
    assert not any(item in new_skills for item in res.json['skills'])

    for tag_name in new_tags:
        res = app.test_client().delete(
            f'api/v1/backoffice/tag',
            headers={'X-BEE-AUTH': inner_token},
            json={'tagName': tag_name}
        )
        assert res.status_code == 200

        with app.app_context():
            tag = Tag.query.filter_by(name=tag_name).first()
            assert tag is None

    for skill_name in new_skills:
        res = app.test_client().delete(
            f'api/v1/backoffice/skill',
            headers={'X-BEE-AUTH': inner_token},
            json={'skillName': skill_name}
        )
        assert res.status_code == 200

        with app.app_context():
            skill = Skill.query.filter_by(name=skill_name).first()
            assert skill is None


def test_put_user_profile_invalid_params(app, inner_token, active_token_user_id):
    # incorrect user id results in error
    wrong_user_id = f'user-{int(time.time() * 1000)}'
    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{wrong_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={"tags": ["a-tag"]}
    )
    assert res.status_code == 404
    assert res.json == {'status': 'error', 'error': 'not_found'}

    # not providing tags and skills results in error
    res = app.test_client().put(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={}
    )
    assert res.status_code == 400
    assert res.json == {'status': 'error', \
        'error': 'malformed_request', \
            'description': {'_schema': ['at least one field must be provided']}}
