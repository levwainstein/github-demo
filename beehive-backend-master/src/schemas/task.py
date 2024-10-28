from ..models.task import Task, TaskStatus, TaskType
from ..utils.marshmallow import BeehiveSchemaMixin, ma
from ..models.work_record import SolutionRating


class TaskSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Task

    id = ma.auto_field()
    created = ma.auto_field()
    delegating_user_id = ma.auto_field(data_key='delegatingUserId')
    description = ma.auto_field()
    title = ma.auto_field(data_key='title')
    func_name = ma.auto_field(data_key='functionName')
    status = ma.auto_field()
    feedback = ma.auto_field()
    priority = ma.auto_field(data_key='priority')
    task_type = ma.auto_field(data_key='taskType')
    review_status = ma.auto_field(data_key='reviewStatus')
    review_feedback = ma.auto_field(data_key='reviewFeedback')
    review_completed = ma.auto_field(data_key='reviewCompleted')
    advanced_options = ma.auto_field(data_key='advancedOptions')
    tags = ma.List(ma.String(), data_key='tags')
    skills = ma.List(ma.String(), data_key='skills')
    quest_id = ma.auto_field(data_key='questId')


class RatingSchema(ma.Schema):
    user = ma.String(data_key='user')
    objectKey = ma.String(data_key='objectKey')
    subject = ma.String(data_key='subject')
    score = ma.Decimal(places=2, data_key='score', as_string=True)
    text = ma.String(data_key='text')
    created = ma.String()


class TaskResponseSchema(TaskSchema, BeehiveSchemaMixin):
    ratings = ma.List(ma.Nested(RatingSchema), required=False, data_key='ratings')


class CreateCuckooTaskRequestSchema(ma.Schema):
    description = ma.String(required=True, data_key='description')
    title = ma.String(required=False, data_key='title')
    user_name = ma.String(required=True, data_key='userName')
    priority = ma.Integer(required=False)
    tags = ma.List(ma.String(data_key='tags', required=False))
    skills = ma.List(ma.String(data_key='skills', required=False))
    repository_name = ma.String(required=False, data_key='repositoryName')
    feature = ma.String(required=False, data_key='feature', allow_none=True)
    chain_review = ma.Boolean(required=False, data_key='chainReview', load_default=False)
    max_chain_iterations = ma.Integer(required=False, data_key='maxChainIterations', allow_none=True)
    chain_description = ma.String(required=False, data_key='chainDescription', allow_none=True)
    quest_id = ma.String(required=False, data_key='questId', allow_none=True)


class PartialUpdateCuckooTaskRequestSchema(ma.Schema):
    task_id = ma.String(required=True, data_key='taskId')
    user_name = ma.String(required=True, data_key='userName')
    description = ma.String(required=False, allow_none=True)
    status = ma.Enum(TaskStatus, allow_none=True)
    tags = ma.List(ma.String(), data_key='tags', required=False, allow_none=True)
    skills = ma.List(ma.String(), data_key='skills', required=False, allow_none=True)
    repository_name = ma.String(required=False, data_key='repositoryName')
    quest_id = ma.String(required=False, data_key='questId', allow_none=True)


class NotifyContributorsRequestSchema(ma.Schema, BeehiveSchemaMixin):
    num_of_contributors = ma.Integer(data_key='numOfContributors')
    tasks = ma.List(ma.String())
