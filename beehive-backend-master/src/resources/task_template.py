from flask import current_app
from flask.views import MethodView

from ..models.task_template import TaskTemplate
from ..schemas.task_template import (
    TaskTemplateRequestSchema,
    TaskTemplateResponseSchema
)
from ..utils.auth import activated_jwt_required
from ..utils.marshmallow import parser


class TaskTemplateCRUD(MethodView):
    # get all templates of a certain type
    @activated_jwt_required
    @parser.use_args(TaskTemplateRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, task_type):
        current_app.logger.info(f'Getting task templates for task_type {task_type}')

        templates = TaskTemplate.query.filter_by(task_type=task_type).all()

        return TaskTemplateResponseSchema(many=True).jsonify(templates)
