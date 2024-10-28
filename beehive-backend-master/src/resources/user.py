from datetime import datetime, timedelta

from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required
)
from sqlalchemy import or_

from ..logic.user import activation_email, reset_password_email
from ..models.user import User
from ..models.user_code import UserCode, UserCodeType
from ..models.skill import Skill, UserSkill
from ..schemas import EmptyResponseSchema
from ..schemas.user import (
    ActivationRequestSchema,
    ResetPasswordChangeRequestSchema,
    ResetPasswordRequestSchema,
    SigninRequestSchema,
    SigninResponseSchema,
    SignupRequestSchema,
    SignupResponseSchema,
    UserProfileRequestSchema,
    UserProfileSchema,
    UserTokenRefreshResponseSchema
)
from ..utils.auth import JWT_ADDITIONAL_CLAIM_PREFIX, unactivated_jwt_required
from ..utils.db import db
from ..utils.errors import abort
from ..utils.jwt import add_revoked_token
from ..utils.marshmallow import parser
from ..utils.slack_bot import notify_user_profile_change


class UserSignup(MethodView):
    # Registers a new user
    @parser.use_args(SignupRequestSchema(), as_kwargs=True)
    def post(
        self,
        email,
        password,
        code=None,
        first_name=None,
        last_name=None,
        github_user=None,
        trello_user=None,
        availability_weekly_hours=None,
        price_per_hour=None,
        upwork_user=None,
        client=None
    ):
        current_app.logger.info(f'Trying to register {email}')

        # override code is used for testing
        if current_app.config['USER_REGISTRATION_OVERRIDE_CODE'] and \
            code == current_app.config['USER_REGISTRATION_OVERRIDE_CODE']:
            user_code = None
        else:
            if code:
                user_code = UserCode.query.filter_by(
                    id=code, code_type=UserCodeType.REGISTRATION, used=False
                ) \
                    .filter(or_(UserCode.expires == None, UserCode.expires > datetime.utcnow())) \
                    .first()
            if not code or not user_code:
                abort(400, code='invalid_registration_code')

        # Saving user in database
        user_id, signup_error, activation_token = User.signup(
            email, password, first_name, last_name, github_user, trello_user, upwork_user,
            availability_weekly_hours, price_per_hour,
            client and client.startswith('frontend')
        )

        if not user_id:
            abort(400, code=signup_error)

        if user_code:
            # update user code so it can't be used again
            user_code.used = True
            db.session.commit()

        # send activation email
        activation_email(user_id, activation_token)

        # generate access and refresh tokens
        access_token = create_access_token(identity=user_id, additional_claims={f'{JWT_ADDITIONAL_CLAIM_PREFIX}activated': False})

        current_app.logger.info(f'Registered new user {email}')

        result = {
            'user_id': user_id,
            'access_token': access_token
        }

        # successful signup results in a signin
        return SignupResponseSchema().jsonify(result)


class UserSignin(MethodView):
    # Logs a new user
    @parser.use_args(SigninRequestSchema(), as_kwargs=True)
    def post(self, email, password):
        current_app.logger.info(f'Login attempt by {email}')

        user_id, user_admin, activated = User.signin(email, password)

        if not user_id:
            current_app.logger.warning(f'Logging attempt by {email} failed')
            abort(401)

        if activated:
            user_claims = {
                f'{JWT_ADDITIONAL_CLAIM_PREFIX}activated': True
            }

            if user_admin:
                user_claims[f'{JWT_ADDITIONAL_CLAIM_PREFIX}admin'] = True

            # generate access and refresh tokens
            access_token = create_access_token(identity=user_id, additional_claims=user_claims)
            refresh_token = create_refresh_token(identity=user_id, additional_claims=user_claims)

            current_app.logger.info(f'Logging attempt by {email} succeeded')

            result = {
                'user_id': user_id,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'activated': True,
                'is_admin': user_admin
            }

            if 'JWT_ACCESS_TOKEN_EXPIRES' in current_app.config:
                # returning the configured timedelta for token expiration might not
                # be super-accurate (since it might take some time for the token to
                # be generated), but is close enough
                result['expires_in'] = int(
                    current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()
                )
        else:
            access_token = create_access_token(identity=user_id, additional_claims={f'{JWT_ADDITIONAL_CLAIM_PREFIX}activated': False})

            current_app.logger.info(f'Logging attempt by unactivated user {email} succeeded')

            result = {
                'user_id': user_id,
                'access_token': access_token,
                'activated': False,
                'is_admin': user_admin
            }

        # successful signin
        return SigninResponseSchema().jsonify(result)


class UserSignout(MethodView):
    # jwt is required so that only if a user signs out with a still-valid token we
    # add it to the revoked list. if the user's token is expired it already is not-
    # usable anyhow
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        user_id = get_jwt_identity()

        try:
            add_revoked_token(jti, user_id)
        except Exception as ex:
            current_app.logger.error(f'error occurred when attempting to add revoked token: {ex}')

        return EmptyResponseSchema().jsonify()


# Refresh an access token
class UserTokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        user_id = get_jwt_identity()
        user_claims = {k: v for k, v in get_jwt().items() if k.startswith(JWT_ADDITIONAL_CLAIM_PREFIX)}

        access_token = create_access_token(identity=user_id, additional_claims=user_claims)

        result = {'access_token': access_token}

        if 'JWT_ACCESS_TOKEN_EXPIRES' in current_app.config:
            # returning the configured timedelta for token expiration might not
            # be super-accurate (since it might take some time for the token to
            # be generated), but is close enough
            result['expires_in'] = int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())

        return UserTokenRefreshResponseSchema().jsonify(result)


class UserActivation(MethodView):
    @parser.use_args(ActivationRequestSchema(), as_kwargs=True)
    def post(self, activation_token):
        user = User.query.filter_by(activation_token=activation_token).first()
        if not user:
            abort(401)

        user.activated = True
        db.session.commit()

        return EmptyResponseSchema().jsonify()


class UserActivationResend(MethodView):
    @unactivated_jwt_required
    def post(self):
        user_id = get_jwt_identity()

        user = User.query.filter_by(id=user_id).first()
        if not user:
            abort(401)

        # too-many-requests error will be implemented when a separate email service
        # is set up which can track all emails sent

        # send activation email
        activation_email(user_id, user.activation_token)

        return EmptyResponseSchema().jsonify()


class UserResetPassword(MethodView):
    @parser.use_args(ResetPasswordRequestSchema(), as_kwargs=True)
    def post(self, email):
        user = User.query.filter_by(email=email.lower()).first()
        if user:
            current_app.logger.info(f'Reset password request by existing user {email}')

            # generate user reset password token
            expires_at = datetime.utcnow() + timedelta(days=1)
            reset_code = UserCode(
                UserCodeType.RESET_PASSWORD, expires=expires_at, user_id=user.id
            )
            db.session.add(reset_code)
            db.session.commit()

            # too-many-requests error will be implemented when a separate email service
            # is set up which can track all emails sent

            # queue email send only if user was found
            reset_password_email(user.id, reset_code.id)
        else:
            current_app.logger.warning(f'Reset password request by non-existing user {email}')

        # always return success
        return EmptyResponseSchema().jsonify()


class UserResetPasswordChange(MethodView):
    @parser.use_args(ResetPasswordChangeRequestSchema(), as_kwargs=True)
    def post(self, code, new_password=None):
        user_code = UserCode.query.filter_by(
            id=code, code_type=UserCodeType.RESET_PASSWORD, used=False
        ) \
            .filter(UserCode.user_id != None) \
            .filter(UserCode.expires > datetime.utcnow()) \
            .first()
        if not user_code:
            abort(404)

        # if no new password was provided this is just a validation of the reset code
        if new_password:
            user = User.query.filter_by(id=user_code.user_id).first()
            if not user:
                abort(404)

            # change user's password
            user.change_password(new_password)

            # update user code so it can't be used again
            user_code.used = True

            db.session.commit()

        return EmptyResponseSchema().jsonify()


class UserProfile(MethodView):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        user = User.query.filter_by(id=user_id).first()
        if not user:
            abort(401)

        # list specific fields to prevent accidentaly leaking sensitive data
        return UserProfileSchema().jsonify({
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'github_user': user.github_user,
            'trello_user': user.trello_user,
            'upwork_user': user.upwork_user,
            'availability_weekly_hours': user.availability_weekly_hours,
            'price_per_hour': user.price_per_hour,
            'skills': user.skills
        })

    @jwt_required()
    @parser.use_args(UserProfileRequestSchema(), as_kwargs=True)
    def put(
        self, first_name=None, last_name=None, email=None,
        github_user=None, trello_user=None, upwork_user=None,
        availability_weekly_hours=None, price_per_hour=None, 
        skills=None
    ):
        """
        Update an existing user profile by user
        """
        user_id = get_jwt_identity()

        user = User.query.filter_by(id=user_id).first()
        if not user:
            abort(401)
        
        if first_name:
            user.first_name = None if first_name == 'null' else first_name
        if last_name:
            user.last_name = None if last_name == 'null' else last_name
        # if email:
        #     user.email = email
        if github_user:
            user.github_user = None if github_user == 'null' else github_user
        if trello_user:
            user.trello_user = None if trello_user == 'null' else trello_user
        if upwork_user:
            user.upwork_user = None if upwork_user == 'null' else upwork_user
        if availability_weekly_hours:
            user.availability_weekly_hours = \
                None if availability_weekly_hours == -1 else availability_weekly_hours
        if price_per_hour:
            if user.price_per_hour != price_per_hour:
                notify_user_profile_change(user_id, 'price_per_hour', user.price_per_hour, price_per_hour)
            user.price_per_hour = None if price_per_hour == -1 else price_per_hour

        if skills is not None:
            current_user_skills = UserSkill.query.filter_by(user_id=user_id).all()
            updated_user_skill_ids = []

            for skill in skills:
                # pass on non-existing skills
                existing_skill = Skill.query.filter_by(name=skill).first()
                if not existing_skill:
                    current_app.logger.warning(f'User profile update skill "{skill}" does not exist')
                    continue

                updated_user_skill_ids.append(existing_skill.id)

                if not any(s.skill_id == existing_skill.id for s in current_user_skills):
                    existing_user_skill = UserSkill(user_id=user_id, skill_id=existing_skill.id)
                    db.session.add(existing_user_skill)
                    current_app.logger.info(f'Added skill "{skill}" to user {user_id}')
                else:
                    current_app.logger.info(f'User {user_id} already has skill "{skill}"')

            # delete skills that weren't provided in the update request
            for current_skill in current_user_skills:
                if current_skill.skill_id not in updated_user_skill_ids:
                    current_app.logger.info(
                        f'Removed skill "{current_skill.skill_id}" to user {user_id}'
                    )
                    db.session.delete(current_skill)

        db.session.commit()
        db.session.refresh(user)

        return EmptyResponseSchema().jsonify()
