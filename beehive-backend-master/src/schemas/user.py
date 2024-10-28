from marshmallow.validate import Length, ValidationError
from marshmallow import validates_schema

from ..utils.marshmallow import BeehiveSchemaMixin, ma


class SignupRequestSchema(ma.Schema):
    email = ma.Email(required=True)
    password = ma.String(required=True, validate=Length(min=4))
    code = ma.String()
    first_name = ma.String(required=False, data_key='firstName')
    last_name = ma.String(required=False, data_key='lastName')
    github_user = ma.String(required=False, data_key='githubUser')
    trello_user = ma.String(required=False, data_key='trelloUser')
    availability_weekly_hours = ma.Integer(required=False, data_key='availabilityWeeklyHours')
    price_per_hour = ma.Decimal(required=False, data_key='pricePerHour', places=2, as_string=True)
    client = ma.String(required=False)
    upwork_user = ma.String(required=False, data_key='upworkUser')


class SignupResponseSchema(ma.Schema, BeehiveSchemaMixin):
    user_id = ma.String(data_key='userId')
    access_token = ma.String(data_key='accessToken')


class SigninRequestSchema(ma.Schema):
    email = ma.Email(required=True)
    password = ma.String(required=True)


class SigninResponseSchema(ma.Schema, BeehiveSchemaMixin):
    user_id = ma.String(data_key='userId')
    access_token = ma.String(data_key='accessToken')
    expires_in = ma.Integer(data_key='expiresIn')
    refresh_token = ma.String(data_key='refreshToken')
    activated = ma.Boolean()
    is_admin = ma.Boolean(data_key='isAdmin')


class UserTokenRefreshResponseSchema(ma.Schema, BeehiveSchemaMixin):
    access_token = ma.String(data_key='accessToken')
    expires_in = ma.Integer(data_key='expiresIn')

class ActivationRequestSchema(ma.Schema):
    activation_token = ma.String(required=True, data_key='activationToken')


class ResetPasswordRequestSchema(ma.Schema):
    email = ma.Email(required=True)


class ResetPasswordChangeRequestSchema(ma.Schema):
    code = ma.String(required=True)
    new_password = ma.String(required=False, data_key='newPassword', validate=Length(min=4))


class UserSchema(ma.Schema):
    id = ma.String(data_key='userId')
    email = ma.Email(data_key='email')
    first_name = ma.String(data_key='firstName')
    last_name = ma.String(data_key='lastName')
    name = ma.Function(lambda obj: f'{obj["first_name"]} {obj["last_name"]}' if obj["first_name"] and obj["last_name"] else None, data_key='name')
    github_user = ma.String(data_key='githubUser')
    trello_user = ma.String(data_key='trelloUser')
    upwork_user = ma.String(data_key='upworkUser')
    admin = ma.Boolean(data_key='admin')
    availability_weekly_hours = ma.Integer(data_key='availabilityWeeklyHours')
    price_per_hour = ma.Decimal(data_key='pricePerHour', places=2, as_string=True)
    tags = ma.List(ma.String(), data_key='tags')
    skills = ma.List(ma.String(), data_key='skills')


class UserProfileSchema(UserSchema, BeehiveSchemaMixin):
    pass


class UserProfileRequestSchema(ma.Schema):
    first_name = ma.String(required=False, data_key='firstName')
    last_name = ma.String(required=False, data_key='lastName')
    email = ma.Email(required=False, data_key='email')
    github_user = ma.String(required=False, data_key='githubUser')
    trello_user = ma.String(required=False, data_key='trelloUser')
    upwork_user = ma.String(required=False, data_key='upworkUser')
    skills = ma.List(ma.String(), required=False, data_key='skills')
    availability_weekly_hours = ma.Integer(required=False, data_key='availabilityWeeklyHours')
    price_per_hour = ma.Decimal(required=False, data_key='pricePerHour', places=2, as_string=True)

    @validates_schema
    def validate_any_field(self, data, **kwargs):
        # make sure data has at least one value
        if len(data) == 0:
            raise ValidationError('at least one field must be provided')
