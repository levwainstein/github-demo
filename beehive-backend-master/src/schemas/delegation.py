
from ..models.task import TaskType
from ..models.task_classification import TaskTypeClassification
from .task import RatingSchema, TaskSchema
from .task_context import TaskContextRequestSchema
from .quest import QuestSchema, QuestSuccessCriteriaSchema
from ..utils.marshmallow import BeehiveSchemaMixin, ma

class RepositoryResponseSchema(ma.Schema):
    id = ma.Integer()
    project_id = ma.Integer(data_key = 'projectId')
    name = ma.String()
    url = ma.String()

class DelegatorRepositoriesResponseSchema(ma.Schema):
    repositories = ma.List(ma.Nested(RepositoryResponseSchema))

class DelegationTemplateResponseSchema(ma.Schema):
    name = ma.String()
    task_description = ma.String(data_key = 'taskDescription')
    skills = ma.List(ma.String())
    task_classification = ma.String(data_key = 'taskClassification')
    task_type = ma.String(data_key = 'taskType')
    id = ma.Integer()
    repository_id = ma.Integer(data_key = 'repositoryId')

class DelegationTemplatesResponseSchema(ma.Schema):
    templates = ma.List(ma.Nested(DelegationTemplateResponseSchema))

class DelegateTaskRequestSchema(ma.Schema):
    description = ma.String(required=True, data_key='description')
    title = ma.String(required=True, data_key='title')
    repository_id = ma.Integer(required=True, data_key='repositoryId')
    type = ma.Integer(required=False)
    task_classification = ma.Enum(TaskTypeClassification, by_value=True, data_key='taskClassification')
    priority = ma.Integer(required=False)
    tags = ma.List(ma.String(data_key='tags', required=False))
    skills = ma.List(ma.String(data_key='skills', required=False))
    feature = ma.String(required=False, data_key='feature', allow_none=True)
    chain_review = ma.Boolean(required=False, data_key='chainReview', load_default=False)
    max_chain_iterations = ma.Integer(required=False, data_key='maxChainIterations', allow_none=True)
    chain_description = ma.String(required=False, data_key='chainDescription', allow_none=True)
    delegation_time_seconds = ma.Integer(required=False, data_key='delegationTimeSeconds')
    context = ma.List(ma.Nested(TaskContextRequestSchema), required=False)


class DelegateTaskSchema(TaskSchema, BeehiveSchemaMixin):
    ratings = ma.List(ma.Nested(RatingSchema), required=False, data_key='ratings')

class DelegateQuestRequestSchema(ma.Schema):
    description = ma.String(required=True, data_key='description')
    title = ma.String(required=True, data_key='title')
    project_id = ma.Integer(required=True, data_key='projectId')
    quest_type = ma.Integer(required=False, data_key='questType')
    success_criteria = ma.List(ma.Nested(QuestSuccessCriteriaSchema), required=False, data_key='successCriteria')
    links = ma.Dict(keys=ma.String(), values=ma.String(), data_key='links', required=False, allow_none=True, allow_blank=True)
    delegation_time_seconds = ma.Integer(required=False, data_key='delegationTimeSeconds')

class DelegateQuestResponseSchema(QuestSchema, BeehiveSchemaMixin):
    pass

class UpsertTemplateRequestSchema(ma.Schema):
    template_id = ma.Integer(data_key = 'templateId', required=False)
    repository_id = ma.Integer(data_key = 'repositoryId', required=False)
    name = ma.String(required=True)
    task_description = ma.String(data_key = 'taskDescription', required=True)
    skills = ma.List(ma.String(), required=False)
    task_classification = ma.Enum(TaskTypeClassification, by_value=True, data_key='taskClassification', required=False)
    task_type = ma.Enum(TaskType, by_value=True, data_key='taskType', required=False)
    
