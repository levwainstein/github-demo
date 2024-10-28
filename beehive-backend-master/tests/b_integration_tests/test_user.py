from datetime import datetime, timedelta
import time
from unittest.mock import patch
import uuid

from src.models.user import User
from src.models.user_code import UserCode, UserCodeType
from src.models.skill import Skill
from src.models.tag import Tag
from src.utils.db import db


def test_user_signup_invalid_code(app):
    # not providing code results in immediate error
    res = app.test_client().post(
        'api/v1/signup',
        json={
            'email': f'user-{int(time.time() * 1000)}@test.test',
            'password': '1234'
        }
    )
    assert res.status_code == 400
    assert res.json == {'status': 'error', 'error': 'invalid_registration_code'}

    # providing wrong code will result in error
    res = app.test_client().post(
        'api/v1/signup',
        json={
            'email': f'user-{int(time.time() * 1000)}@test.test',
            'password': '1234',
            'code': 'invalid'
        }
    )
    assert res.status_code == 400
    assert res.json == {'status': 'error', 'error': 'invalid_registration_code'}

    with app.app_context():
        # providing expired code will result in error
        expired_user_code = UserCode(
            code_type=UserCodeType.REGISTRATION,
            expires=datetime.utcnow() - timedelta(seconds=1)
        )
        db.session.add(expired_user_code)

    res = app.test_client().post(
        'api/v1/signup',
        json={
            'email': f'user-{int(time.time() * 1000)}@test.test',
            'password': '1234',
            'code': expired_user_code.id
        }
    )
    assert res.status_code == 400
    assert res.json == {'status': 'error', 'error': 'invalid_registration_code'}

    # providing used code will result in error
    with app.app_context():
        used_user_code = UserCode(code_type=UserCodeType.REGISTRATION, used=True)
        db.session.add(used_user_code)
        db.session.commit()

    res = app.test_client().post(
        'api/v1/signup',
        json={
            'email': f'user-{int(time.time() * 1000)}@test.test',
            'password': '1234',
            'code': used_user_code.id
        }
    )
    assert res.status_code == 400
    assert res.json == {'status': 'error', 'error': 'invalid_registration_code'}


def test_user_signup_code_reuse(app):
    with app.app_context():
        user_code = UserCode(code_type=UserCodeType.REGISTRATION)
        db.session.add(user_code)
        db.session.commit()

    # using the code once should work
    res = app.test_client().post(
        'api/v1/signup',
        json={
            'email': f'user-{int(time.time() * 1000)}@test.test',
            'password': '1234',
            'code': user_code.id
        }
    )
    assert res.status_code == 200
    assert 'userId' in res.json['data']
    assert 'accessToken' in res.json['data']

    # using the code a second time should not work
    res = app.test_client().post(
        'api/v1/signup',
        json={
            'email': f'user-{int(time.time() * 1000) + 1}@test.test',
            'password': '1234',
            'code': user_code.id
        }
    )
    assert res.status_code == 400
    assert res.json == {'status': 'error', 'error': 'invalid_registration_code'}


def test_user_signup_invalid_params(app):
    email = f'user-{int(time.time() * 1000)}@test.test'

    # invalid email should not work
    res = app.test_client().post(
        'api/v1/signup',
        json={
            'email': 'invalid',
            'password': '1234',
            'code': 'whatever'
        }
    )
    assert res.status_code == 400
    assert res.json['status'] == 'error'
    assert res.json['error'] == 'malformed_request'
    assert res.json['description'] == {'email': ['Not a valid email address.']}

    # short password should not work
    res = app.test_client().post(
        'api/v1/signup',
        json={
            'email': email,
            'password': '123',
            'code': 'whatever'
        }
    )
    assert res.status_code == 400
    assert res.json['status'] == 'error'
    assert res.json['error'] == 'malformed_request'
    assert res.json['description'] == {'password': ['Shorter than minimum length 4.']}

    # using an email once should work
    with app.app_context():
        user_code_1 = UserCode(code_type=UserCodeType.REGISTRATION)
        db.session.add(user_code_1)
        db.session.commit()

    res = app.test_client().post(
        'api/v1/signup',
        json={
            'email': email,
            'password': '1234',
            'code': user_code_1.id
        }
    )
    assert res.status_code == 200
    assert 'userId' in res.json['data']
    assert 'accessToken' in res.json['data']

    # using the email a second time should not work
    with app.app_context():
        user_code_2 = UserCode(code_type=UserCodeType.REGISTRATION)
        db.session.add(user_code_2)
        db.session.commit()

    res = app.test_client().post(
        'api/v1/signup',
        json={
            'email': email,
            'password': '1234',
            'code': user_code_2.id
        }
    )
    assert res.status_code == 400
    assert res.json == {'status': 'error', 'error': 'email_exists'}

    # using the same email with a different case should not work
    res = app.test_client().post(
        'api/v1/signup',
        json={
            'email': email.upper(),
            'password': '1234',
            'code': user_code_2.id
        }
    )
    assert res.status_code == 400
    assert res.json == {'status': 'error', 'error': 'email_exists'}


def test_user_signup_notifications(app):
    # user signing up with no client should have notifications set to false
    email_1 = f'user1-{int(time.time() * 1000)}@test.test'
    with app.app_context():
        user_code_1 = UserCode(code_type=UserCodeType.REGISTRATION)
        db.session.add(user_code_1)
        db.session.commit()

    res = app.test_client().post(
        'api/v1/signup',
        json={
            'email': email_1,
            'password': '1234',
            'code': user_code_1.id,
            'githubUser': 'github_user1', 
            'trelloUser': 'trello_user1', 
            'upworkUser': 'upwork_user1', 
            'availabilityWeeklyHours': 10,
            'pricePerHour': 15
        }
    )
    assert res.status_code == 200
    assert 'userId' in res.json['data']

    with app.app_context():
        assert User.query.filter_by(id=res.json['data']['userId']).first().notifications == False

    # user signing up with a client which is not frontend should have notifications set to false
    email_2 = f'user2-{int(time.time() * 1000)}@test.test'
    with app.app_context():
        user_code_2 = UserCode(code_type=UserCodeType.REGISTRATION)
        db.session.add(user_code_2)
        db.session.commit()

    res = app.test_client().post(
        'api/v1/signup',
        json={
            'email': email_2,
            'password': '1234',
            'code': user_code_2.id,
            'client': 'extension-0.1.0',
            'githubUser': 'github_user2', 
            'trelloUser': 'trello_user2', 
            'upworkUser': 'upwork_user2', 
            'availabilityWeeklyHours': 10,
            'pricePerHour': 20

        }
    )
    assert res.status_code == 200
    assert 'userId' in res.json['data']

    with app.app_context():
        assert User.query.filter_by(id=res.json['data']['userId']).first().notifications == False

    # user signing up with a client which is frontend should have notifications set to true
    email_3 = f'user3-{int(time.time() * 1000)}@test.test'
    with app.app_context():
        user_code_3 = UserCode(code_type=UserCodeType.REGISTRATION)
        db.session.add(user_code_3)
        db.session.commit()

    res = app.test_client().post(
        'api/v1/signup',
        json={
            'email': email_3,
            'password': '1234',
            'code': user_code_3.id,
            'client': 'frontend-0.1.0'
        }
    )
    assert res.status_code == 200
    assert 'userId' in res.json['data']

    with app.app_context():
        assert User.query.filter_by(id=res.json['data']['userId']).first().notifications == True


def test_user_signin(app):
    email = f'user-{int(time.time() * 1000)}@test.test'

    # signin with non-existing email should fail
    res = app.test_client().post(
        'api/v1/signin',
        json={
            'email': email,
            'password': '1234'
        }
    )
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}

    # register the email
    with app.app_context():
        user_code_1 = UserCode(code_type=UserCodeType.REGISTRATION)
        db.session.add(user_code_1)
        db.session.commit()

    res = app.test_client().post(
        'api/v1/signup',
        json={
            'email': email,
            'password': '1234',
            'code': user_code_1.id
        }
    )
    assert res.status_code == 200
    assert 'userId' in res.json['data']
    assert 'accessToken' in res.json['data']

    # signin with wrong password should fail
    res = app.test_client().post(
        'api/v1/signin',
        json={
            'email': email,
            'password': '123'
        }
    )
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}

    # signin with correct credentials should work
    res = app.test_client().post(
        'api/v1/signin',
        json={
            'email': email,
            'password': '1234'
        }
    )
    assert res.status_code == 200
    assert 'userId' in res.json['data']
    assert 'accessToken' in res.json['data']
    assert res.json['data']['activated'] == False

    # signin with correct email with different case and correct password should work
    res = app.test_client().post(
        'api/v1/signin',
        json={
            'email': email.upper(),
            'password': '1234'
        }
    )
    assert res.status_code == 200
    assert 'userId' in res.json['data']
    assert 'accessToken' in res.json['data']
    assert res.json['data']['activated'] == False


@patch('src.logic.user.send_user_activation_email', return_value=None)
def test_user_activation(mock_send_email, app):
    email = f'user-{int(time.time() * 1000)}@test.test'

    # generate a random activation token which will be used when we register an account
    activation_token_uuid = uuid.uuid4()

    # mock uuid.uuid4 method to return the previously-generated uuid we hold a copy of
    # and send_user_activation_email method to count the number of emails sent
    with patch('uuid.uuid4') as mock_uuid:
        mock_uuid.return_value = activation_token_uuid

        # no user activation emails were sent yet
        assert mock_send_email.call_count == 0

        # register the email
        with app.app_context():
            user_code_1 = UserCode(code_type=UserCodeType.REGISTRATION)
            db.session.add(user_code_1)
            db.session.commit()

        res = app.test_client().post(
            'api/v1/signup',
            json={
                'email': email,
                'password': '1234',
                'code': user_code_1.id
            }
        )
        assert res.status_code == 200
        assert 'userId' in res.json['data']
        assert 'accessToken' in res.json['data']

    # one user activation emails should have been sent
    assert mock_send_email.call_count == 1

    # signin with correct credentials should work, but the token is an
    # un-activated one
    res = app.test_client().post(
        'api/v1/signin',
        json={
            'email': email,
            'password': '1234'
        }
    )
    assert res.status_code == 200
    assert 'userId' in res.json['data']
    assert 'accessToken' in res.json['data']
    assert 'refreshToken' not in res.json['data']
    assert res.json['data']['activated'] == False

    unactivated_token = res.json['data']['accessToken']

    # most endpoints (get available work in this case) will not work with an
    # un-activated token
    res = app.test_client().get(
        'api/v1/work/available',
        headers={'Authorization': f'Bearer {unactivated_token}'}
    )
    assert res.status_code == 401

    # resend user activation email endpoint is the only one that works with an
    # un-activated token
    res = app.test_client().post(
        'api/v1/auth/resend',
        headers={'Authorization': f'Bearer {unactivated_token}'}
    )
    assert res.status_code == 200

    # two user activation emails should have been sent
    assert mock_send_email.call_count == 2

    # activate the user
    res = app.test_client().post(
        'api/v1/auth/activate',
        json={'activationToken': activation_token_uuid.hex}
    )
    assert res.status_code == 200

    # sign in to receive an activated token
    res = app.test_client().post(
        'api/v1/signin',
        json={
            'email': email,
            'password': '1234'
        }
    )
    assert res.status_code == 200
    assert 'userId' in res.json['data']
    assert 'accessToken' in res.json['data']
    assert 'refreshToken' in res.json['data']
    assert res.json['data']['activated'] == True

    activated_token = res.json['data']['accessToken']

    # get available work (and other) endpoint should work with the new token
    res = app.test_client().get(
        'api/v1/work/available',
        headers={'Authorization': f'Bearer {activated_token}'}
    )
    assert res.status_code == 404

    # resend user activation email endpoint should not work with an activated
    # token
    res = app.test_client().post(
        'api/v1/auth/resend',
        headers={'Authorization': f'Bearer {activated_token}'}
    )
    assert res.status_code == 401

    # activation works multiple times
    res = app.test_client().post(
        'api/v1/auth/activate',
        json={'activationToken': activation_token_uuid.hex}
    )
    assert res.status_code == 200

    # only two user activation emails should have been sent
    assert mock_send_email.call_count == 2


def test_system_user_signin_forbidden(app):
    # signin with non-existing email should fail
    res = app.test_client().post(
        'api/v1/signin',
        json={
            'email': 'system@beehivesoftware.com',
            'password': ''
        }
    )
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}


@patch('src.logic.user.send_user_reset_password_email', return_value=None)
def test_user_reset_password(mock_send_email, app):
    email = f'user-{int(time.time() * 1000)}@test.test'

    # requesting a password reset with no email should fail
    res = app.test_client().post(
        'api/v1/auth/reset',
        json={}
    )
    assert res.status_code == 400
    assert res.json['status'] == 'error'
    assert res.json['error'] == 'malformed_request'

    # requesting a password reset for non-registered email should return success
    # but not call email function
    res = app.test_client().post(
        'api/v1/auth/reset',
        json={
            'email': email
        }
    )
    assert res.status_code == 200
    assert res.json['status'] == 'ok'

    # no reset password emails were sent yet
    assert mock_send_email.call_count == 0

    # register user
    with app.app_context():
        user_code = UserCode(code_type=UserCodeType.REGISTRATION)
        db.session.add(user_code)
        db.session.commit()

    res = app.test_client().post(
        'api/v1/signup',
        json={
            'email': email,
            'password': '1234',
            'code': user_code.id
        }
    )
    assert res.status_code == 200
    user_id = res.json['data']['userId']

    # requesting a password reset for registered email should return success and
    # call email function
    res = app.test_client().post(
        'api/v1/auth/reset',
        json={
            'email': email
        }
    )
    assert res.status_code == 200
    assert res.json['status'] == 'ok'

    # one reset password email was now sent
    assert mock_send_email.call_count == 1

    # reset url passed to send email function can be parsed for code. code should
    # exist and be of RESET_PASSWORD type with the correct user_id
    reset_code_id_1 = mock_send_email.call_args.args[1]
    assert reset_code_id_1 is not None
    # remove url part, leave only code
    reset_code_id_1 = reset_code_id_1[reset_code_id_1.index('=') + 1:]

    with app.app_context():
        reset_code_1 = UserCode.query.filter_by(id=reset_code_id_1).first()
        assert reset_code_1 is not None
        assert reset_code_1.code_type == UserCodeType.RESET_PASSWORD
        assert reset_code_1.used == False
        assert reset_code_1.user_id == user_id
        assert reset_code_1.expires > datetime.utcnow()

    # requesting a password reset for registered email with different case should
    # be successful as well
    res = app.test_client().post(
        'api/v1/auth/reset',
        json={
            'email': email.upper()
        }
    )
    assert res.status_code == 200
    assert res.json['status'] == 'ok'

    # two reset password email were now sent
    assert mock_send_email.call_count == 2

    # reset url passed to send email function can be parsed for code. code should
    # exist and be of RESET_PASSWORD type with the correct user_id
    reset_code_id_2 = mock_send_email.call_args.args[1]
    assert reset_code_id_2 is not None
    # remove url part, leave only code
    reset_code_id_2 = reset_code_id_2[reset_code_id_2.index('=') + 1:]
    assert reset_code_id_2 != reset_code_id_1

    with app.app_context():
        reset_code_2 = UserCode.query.filter_by(id=reset_code_id_1).first()
        assert reset_code_2 is not None
        assert reset_code_2.code_type == UserCodeType.RESET_PASSWORD
        assert reset_code_2.used == False
        assert reset_code_2.user_id == user_id
        assert reset_code_2.expires > datetime.utcnow()


def test_user_reset_password_change(app):
    email = f'user-{int(time.time() * 1000)}@test.test'

    # reset password change with no code or new password should fail
    res = app.test_client().post(
        'api/v1/auth/reset/change',
        json={}
    )
    assert res.status_code == 400
    assert res.json['status'] == 'error'
    assert res.json['error'] == 'malformed_request'

    # reset password change with only new password should fail
    res = app.test_client().post(
        'api/v1/auth/reset/change',
        json={
            'newPassword': '12345'
        }
    )
    assert res.status_code == 400
    assert res.json['status'] == 'error'
    assert res.json['error'] == 'malformed_request'

    # reset password change with empty code should fail
    res = app.test_client().post(
        'api/v1/auth/reset/change',
        json={
            'code': ''
        }
    )
    assert res.status_code == 404
    assert res.json['status'] == 'error'
    assert res.json['error'] == 'not_found'

    # reset password change with invalid code should fail
    res = app.test_client().post(
        'api/v1/auth/reset/change',
        json={
            'code': 'invalid'
        }
    )
    assert res.status_code == 404
    assert res.json['status'] == 'error'
    assert res.json['error'] == 'not_found'

    # reset password change with valid REGISTRATION code should fail
    with app.app_context():
        invalid_code_1 = UserCode(
            code_type=UserCodeType.REGISTRATION,
            expires=datetime.utcnow() + timedelta(minutes=1)
        )
        db.session.add(invalid_code_1)
        db.session.commit()

    res = app.test_client().post(
        'api/v1/auth/reset/change',
        json={
            'code': invalid_code_1.id
        }
    )
    assert res.status_code == 404
    assert res.json['status'] == 'error'
    assert res.json['error'] == 'not_found'

    # reset password change with valid RESET_PASSWORD code with no user_id should fail
    with app.app_context():
        invalid_code_2 = UserCode(
            code_type=UserCodeType.RESET_PASSWORD,
            expires=datetime.utcnow() + timedelta(minutes=1)
        )
        db.session.add(invalid_code_2)
        db.session.commit()

    res = app.test_client().post(
        'api/v1/auth/reset/change',
        json={
            'code': invalid_code_2.id
        }
    )
    assert res.status_code == 404
    assert res.json['status'] == 'error'
    assert res.json['error'] == 'not_found'

    # register user
    with app.app_context():
        user_code = UserCode(code_type=UserCodeType.REGISTRATION)
        db.session.add(user_code)
        db.session.commit()

    res = app.test_client().post(
        'api/v1/signup',
        json={
            'email': email,
            'password': '1234',
            'code': user_code.id
        }
    )
    assert res.status_code == 200
    user_id = res.json['data']['userId']

    # reset password change with valid expired code should fail
    with app.app_context():
        invalid_code_3 = UserCode(
            code_type=UserCodeType.RESET_PASSWORD,
            expires=datetime.utcnow() - timedelta(minutes=1),
            user_id=user_id
        )
        db.session.add(invalid_code_3)
        db.session.commit()

    res = app.test_client().post(
        'api/v1/auth/reset/change',
        json={
            'code': invalid_code_3.id
        }
    )
    assert res.status_code == 404
    assert res.json['status'] == 'error'
    assert res.json['error'] == 'not_found'

    # reset password change with valid code and no password should succeed but not
    # change password (code validation)
    with app.app_context():
        valid_code = UserCode(
            code_type=UserCodeType.RESET_PASSWORD,
            expires=datetime.utcnow() + timedelta(minutes=1),
            user_id=user_id
        )
        db.session.add(valid_code)
        db.session.commit()

    res = app.test_client().post(
        'api/v1/auth/reset/change',
        json={
            'code': valid_code.id
        }
    )
    assert res.status_code == 200
    assert res.json['status'] == 'ok'

    # login should still work with the original password
    res = app.test_client().post(
        'api/v1/signin',
        json={
            'email': email,
            'password': '1234'
        }
    )
    assert res.status_code == 200
    assert 'userId' in res.json['data']

    # reset password change with valid code and password should succeed and change
    # the user's password
    res = app.test_client().post(
        'api/v1/auth/reset/change',
        json={
            'code': valid_code.id,
            'newPassword': '12345'
        }
    )
    assert res.status_code == 200
    assert res.json['status'] == 'ok'

    # login should now only work with the new password
    res = app.test_client().post(
        'api/v1/signin',
        json={
            'email': email,
            'password': '1234'
        }
    )
    assert res.status_code == 401
    res = app.test_client().post(
        'api/v1/signin',
        json={
            'email': email,
            'password': '12345'
        }
    )
    assert res.status_code == 200
    assert 'userId' in res.json['data']


def test_user_profile_put_endpoint_no_jwt_key(app, inner_token):
    # put user profile update requires jwt auth
    res = app.test_client().put(f'api/v1/user/profile', json={'email': 'email@email.com'})
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}

    # backoffice key won't work
    res = app.test_client().put(
        f'api/v1/user/profile',
        headers={'X-BEE-AUTH': inner_token},
        json={'skills': ['a-skill']}
    )
    assert res.status_code == 401
    assert res.json == {'status': 'error', 'error': 'unauthorized'}


def test_user_profile_put_endpoint_with_tags(app, active_token):
    # user facing endpoint should not support updating tags (which is an internal field)
    res = app.test_client().put(
        f'/api/v1/user/profile',
        headers={'Authorization': f'Bearer {active_token}'},
        json={
            "firstName": 'first',
            "lastName": 'last',
            "email": 'email@test.com',
            "githubUser": 'github',
            "trelloUser": 'trello',
            "upworkUser": 'upwork',
            "availabilityWeeklyHours": 15,
            "pricePerHour": 40,
            "tags": ['random-tag','another-tag'], 
            "skills": ['random-skill']
        }
    )

    assert res.status_code == 400


def test_user_profile_put_endpoint_success(
    app, active_token, active_token_user_id, inner_token
):
    # skill should not exist to begin with
    res = app.test_client().get(
        'api/v1/skill',
        headers={'Authorization': f'Bearer {active_token}'}
    )
    assert res.status_code == 200
    assert 'random-skill' not in [s['name'] for s in res.json['data']]

    # updating profile works
    res = app.test_client().put(
        f'/api/v1/user/profile',
        headers={'Authorization': f'Bearer {active_token}'},
        json={
            'firstName': 'first',
            'lastName': 'last',
            'githubUser': 'github',
            'trelloUser': 'trello',
            'upworkUser': 'upwork',
            'availabilityWeeklyHours': 15,
            'pricePerHour': 40,
            'skills': ['random-skill']
        }
    )
    assert res.status_code == 200

    # user profile should be updated but without the unavailable skill
    res = app.test_client().get(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token}
    )
    assert res.status_code == 200
    assert res.json['firstName'] == 'first'
    assert res.json['lastName'] == 'last'
    assert res.json['githubUser'] == 'github'
    assert res.json['trelloUser'] == 'trello'
    assert res.json['upworkUser'] == 'upwork'
    assert res.json['availabilityWeeklyHours'] == 15
    assert res.json['pricePerHour'] == '40.00'
    assert len(res.json['skills']) == 0
    assert len(res.json['tags']) == 0

    # create skill via backoffice
    res = app.test_client().post(
        f'/api/v1/backoffice/skill',
        headers={'X-BEE-AUTH': inner_token},
        json={'skillName': 'random-skill'}
    )
    assert res.status_code == 200

    # update user profile with the same skill
    res = app.test_client().put(
        f'/api/v1/user/profile',
        headers={'Authorization': f'Bearer {active_token}'},
        json={'skills': ['random-skill']}
    )
    assert res.status_code == 200

    # user profile should now have the skill
    res = app.test_client().get(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token}
    )
    assert res.status_code == 200
    assert len(res.json['skills']) == 1
    assert res.json['skills'][0] == 'random-skill'

    # delete entities we created
    res = app.test_client().delete(
        f'/api/v1/backoffice/user-profile/{active_token_user_id}',
        headers={'X-BEE-AUTH': inner_token},
        json={'skills': ['random-skill']}
    )
    assert res.status_code == 200
    assert len(res.json['skills']) == 0

    # delete the available skill we created
    res = app.test_client().delete(
        f'api/v1/backoffice/skill',
        headers={'X-BEE-AUTH': inner_token},
        json={'skillName': 'random-skill'}
    )
    assert res.status_code == 200

    with app.app_context():
        skill = Skill.query.filter_by(name='random-skill').first()
        assert skill is None
