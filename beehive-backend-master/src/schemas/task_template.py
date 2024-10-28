from ..models.task import TaskType
from ..utils.marshmallow import BeehiveSchemaMixin, ma
from ..models.task_template import TaskTemplate


class TaskTemplateResponseSchema(ma.SQLAlchemySchema, BeehiveSchemaMixin):
    class Meta:
        model = TaskTemplate

    id = ma.auto_field()
    name = ma.auto_field()
    task_description = ma.auto_field(data_key='taskDescription')
    task_type = ma.auto_field(data_key='taskType')


class TaskTemplateRequestSchema(ma.Schema):
    task_type = ma.Enum(TaskType, by_value=False, required=True, data_key='taskType')
