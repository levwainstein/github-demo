from ..schemas.task import TaskSchema
from ..models.quest import Quest, QuestStatus, QuestType, SuccessCriteria
from ..utils.marshmallow import BeehiveSchemaMixin, ma

class QuestSuccessCriteriaSchema(ma.Schema):
    class Meta:
        model = SuccessCriteria

    title = ma.String(required=True)
    description = ma.String(required=True)
    explanation = ma.String(required=False, allow_none=True, allow_blank=True)


class QuestSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Quest

    id = ma.auto_field()
    created = ma.auto_field()
    delegating_user_id = ma.auto_field(data_key='delegatingUserId')
    description = ma.auto_field()
    title = ma.auto_field(data_key='title')
    status = ma.auto_field()
    quest_type = ma.auto_field(data_key='questType')
    links = ma.auto_field(data_key='links')
    tasks = ma.List(ma.Nested(TaskSchema), data_key='tasks')
    project_id = ma.auto_field(required=False, data_key='projectId')
    delegation_time_seconds = ma.auto_field(data_key='delegationTimeSeconds')
    success_criteria = ma.List(ma.Nested(QuestSuccessCriteriaSchema), data_key='successCriteria')

class RatingSchema(ma.Schema):
    user = ma.String(data_key='user')
    objectKey = ma.String(data_key='objectKey')
    subject = ma.String(data_key='subject')
    score = ma.Decimal(places=2, data_key='score', as_string=True)
    text = ma.String(data_key='text')
    created = ma.String()


class QuestResponseSchema(QuestSchema, BeehiveSchemaMixin):
    ratings = ma.List(ma.Nested(RatingSchema), required=False, data_key='ratings')


class ClientQuestResponseSchema(QuestSchema):
    quest = ma.Nested(QuestSchema)
    net_time = ma.Integer(data_key='netTime')
    progress = ma.Integer(required=False)
    iteration = ma.Integer(required=False)
    trello_link = ma.String(required=False, data_key='trelloLink')

class ClientQuestsResponseSchema(QuestSchema, BeehiveSchemaMixin):
    quests = ma.List(ma.Nested(ClientQuestResponseSchema))
    total_count = ma.Integer(data_key='totalCount')
    page = ma.Integer()
    
class CreateQuestRequestSchema(ma.Schema):
    title = ma.String(required=True, data_key='title')
    description = ma.String(required=True, data_key='description', allow_none=True, allow_blank=True)
    user_name = ma.String(required=True, data_key='userName')
    quest_type = ma.Enum(QuestType, data_key='questType')
    links = ma.Dict(keys=ma.String(), values=ma.String(), data_key='links', required=False, allow_none=True, allow_blank=True)
    repository_name = ma.String(required=False, data_key='repositoryName', allow_none=True, allow_blank=True)
    task_ids = ma.List(ma.String(), data_key='taskIds', required=False, allow_none=True, allow_blank=True)
    trello_url = ma.String(required=False, data_key='trelloUrl')


class PartialUpdateQuestRequestSchema(ma.Schema):
    quest_id = ma.String(required=True, data_key='questId')
    user_name = ma.String(required=True, data_key='userName')
    title = ma.String(required=False, allow_none=True, allow_blank=True)
    description = ma.String(required=False, allow_none=True, allow_blank=True)
    status = ma.Enum(QuestStatus)
    links = ma.Dict(keys=ma.String(), values=ma.String(), data_key='links', required=False, allow_none=True, allow_blank=True)
    repository_name = ma.String(required=False, data_key='repositoryName')
    task_ids = ma.List(ma.String(), data_key='taskIds', required=False, allow_none=True, allow_blank=True)


