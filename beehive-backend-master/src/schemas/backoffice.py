from marshmallow import validates_schema
from marshmallow.validate import Length, ValidationError, Email

from .work import WorkSchema
from ..utils.marshmallow import ma, BeehiveSchemaMixin

from ..models.tag import Tag


class UpdateTaskFeedbackRequestSchema(ma.Schema):
    feedback = ma.String(data_key='feedback')

    @validates_schema
    def validate_any_field(self, data, **kwargs):
        # make sure data has at least one value
        if len(data) == 0:
            raise ValidationError('at least one field must be provided')

class UpdateWorkPriorityRequestSchema(ma.Schema):
    priority = ma.Integer(required=True, data_key='priority')
      
class CreateSupportedPackageRequestSchema(ma.Schema):
    package_name = ma.String(required=True, data_key='packageName', validate=Length(min=1))


class TestSupportedPackageRequestSchema(ma.Schema):
    package_name = ma.String(required=True, data_key='packageName', validate=Length(min=1))
    extra_code = ma.String(data_key='extraCode')


class TestSupportedPackageResponseSchema(ma.Schema, BeehiveSchemaMixin):
    output = ma.String()


class CreateUserCodeRequestSchema(ma.Schema):
    expires = ma.String()


class CreateUserCodeResponseSchema(ma.Schema, BeehiveSchemaMixin):
    code = ma.String()


class TaskWorkResponseSchema(WorkSchema, BeehiveSchemaMixin):
    pass


class BackofficeUserProfileRequestSchema(ma.Schema):
    tags = ma.List(ma.String(), required=False, data_key='tags')
    skills = ma.List(ma.String(), required=False, data_key='skills')

    @validates_schema
    def validate_any_field(self, data, **kwargs):
        # make sure data has at least one value
        if len(data) == 0:
            raise ValidationError('at least one field must be provided')


class BackofficeUserProfileResponseSchema(ma.Schema):
    id = ma.String(data_key='userId')
    email = ma.Email(data_key='email')
    first_name = ma.String(data_key='firstName')
    last_name = ma.String(data_key='lastName')
    github_user = ma.String(data_key='githubUser')
    trello_user = ma.String(data_key='trelloUser')
    upwork_user = ma.String(data_key='upworkUser')
    availability_weekly_hours = ma.Integer(data_key='availabilityWeeklyHours')
    price_per_hour = ma.Decimal(data_key='pricePerHour', places=2, as_string=True)
    tags = ma.List(ma.String(), data_key='tags')
    skills = ma.List(ma.String(), data_key='skills')


class TagSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Tag

    id = ma.auto_field()
    name = ma.auto_field()


class TagRequestSchema(ma.Schema):
    tag_name = ma.String(required=True, data_key='tagName', validate=Length(min=1))


class TagResponseSchema(TagSchema, BeehiveSchemaMixin):
    users = ma.List(ma.String(), data_key='users')


class SkillRequestSchema(ma.Schema):
    skill_name = ma.String(required=True, data_key='skillName', validate=Length(min=1))

class DiaryLogSchema(ma.Schema):
    user_email = ma.String(required=True, data_key='email', validate=Email(error='invalid email address'))
    project = ma.String(required=True, data_key='project', validate=Length(min=1))
    date = ma.Date(required=True, data_key='date', format='%Y-%m-%d')
    hours = ma.String(required=True, data_key='hours')
    text = ma.String(required=False, data_key='text')

class DiaryLogRequestSchema(DiaryLogSchema):
    pass