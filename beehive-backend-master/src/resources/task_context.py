from flask import current_app
from flask.views import MethodView

from ..models.task_context import TaskContext
from ..schemas.task_context import (
    TaskContextRequestSchema,
    TaskContextResponseSchema
)
from ..schemas import EmptyResponseSchema
from ..utils.auth import activated_jwt_required
from ..utils.marshmallow import parser
from ..utils.errors import abort
from ..utils.db import db


class TaskContextCRUD(MethodView):
    @activated_jwt_required
    def get(self, task_id):
        current_app.logger.info(f'Getting task context for task id {task_id}')

        contexts = TaskContext.query.filter_by(task_id=task_id).all()

        return TaskContextResponseSchema(many=True).jsonify(contexts)

    @activated_jwt_required
    @parser.use_args(TaskContextRequestSchema(), as_kwargs=True)
    def put(self, task_id, id, file, entity, potential_use):
        current_app.logger.info(f'Updating task {task_id} context with id {id}')

        context = TaskContext.query.filter_by(id=id).first()
        if not context:
            abort(404)

        context.file = file
        context.entity = entity
        context.potential_use = potential_use
        db.session.commit()

        return EmptyResponseSchema().jsonify()

    @activated_jwt_required
    @parser.use_args(TaskContextRequestSchema(), as_kwargs=True)
    def post(self, task_id, file, entity, potential_use):
        current_app.logger.info(f'Creating a task context for task {task_id} with values file:{file} entity:{entity} potential_use:{potential_use}')

        context = TaskContext(
            file=file,
            entity=entity,
            potential_use=potential_use,
            task_id=task_id
        )
        db.session.add(context)
        db.session.commit()

        return TaskContextResponseSchema(many=False).jsonify(context)

    @activated_jwt_required
    def delete(self, task_id, id):
        current_app.logger.info(f'Deleting a task context with id {id} for task {task_id}')

        context = TaskContext.query.filter_by(id=id).first()
        if not context:
            abort(404)

        db.session.delete(context)
        db.session.commit()

        return EmptyResponseSchema().jsonify()
