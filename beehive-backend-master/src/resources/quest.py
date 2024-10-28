
from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.orm import joinedload

from ..models.repository import Repository
from ..models.task import Task
from ..models.project import Project
from ..models.quest import Quest, QuestStatus
from ..models.user import User
from ..schemas import EmptyResponseSchema
from ..schemas.quest import (
    CreateQuestRequestSchema,
    PartialUpdateQuestRequestSchema,
    QuestResponseSchema
)

from ..utils.auth import activated_jwt_required, inner_auth
from ..utils.db import db
from ..utils.errors import abort
from ..utils.marshmallow import parser


class QuestCRUD(MethodView):
    # get all delegator's quests
    @activated_jwt_required
    def get(self, quest_id):
        user_id = get_jwt_identity()

        current_app.logger.info(f'Getting quests for user {user_id}')

        quests = Quest.query.filter(
            Quest.delegating_user_id == user_id
        ).options(joinedload(Quest.success_criteria))

        if quest_id:
            quests = quests.filter_by(id=quest_id)
            quest = quests.first()

            # abort with status 404 if specific quest was requested and it doesn't exist
            if not quest:
                abort(404)

            return QuestResponseSchema().jsonify(quest)
        else:
            return QuestResponseSchema(many=True).jsonify(quests.all())

    # deletes quest
    @activated_jwt_required
    def delete(self, quest_id):
        user_id = get_jwt_identity()

        quest = Quest.query.filter_by(id=quest_id, delegating_user_id=user_id).first()
        if not quest:
            abort(404)

        db.session.delete(quest)
        db.session.commit()

        current_app.logger.info(f'Deleted quest ID {quest_id}\n')

        return EmptyResponseSchema().jsonify()


    # create new quest from cuckoo service
    @inner_auth
    @parser.use_args(CreateQuestRequestSchema(), as_kwargs=True)
    def post(self, title, description, user_name, quest_type, links=None, repository_name=None, task_ids=None, trello_url=None):
        user = User.query.filter_by(trello_user=user_name).first()
        if not user:
            abort(404)

        project_id = None
        if repository_name:
            repo = Repository.query.filter_by(name=repository_name).first()
            if repo:
                project_id = repo.project_id
        elif trello_url:
            project = Project.query.filter_by(trello_link=trello_url).first()
            if project:
                project_id = project.id
        if not project_id:
            abort(404, code='unknown_project')

        current_app.logger.info(f'Creating quest {description}')

        # Create the quest and get a quest ID
        quest = Quest(
            delegating_user_id=user.id,
            description=description,
            title=title,
            status=QuestStatus.NEW,
            quest_type=quest_type,
            links=links,
            project_id=project_id
        )
        db.session.add(quest)
        db.session.commit()

        if task_ids:
            for task_id in task_ids:
                task = Task.query.filter_by(id=task_id).first()
                if task:
                    task.quest_id = quest.id
                    db.session.add(task)
                else:
                    current_app.logger.error(f'Cannot find task {task_id} to update quest information')
            db.session.commit()

        return QuestResponseSchema().jsonify(quest)

    # partial-update a quest
    @inner_auth
    @parser.use_args(PartialUpdateQuestRequestSchema(), as_kwargs=True)
    def put(
        self, quest_id, user_name,
        description=None, title=None, status=None, links=None, repository_name=None, task_ids=None
    ):

        quest = Quest.query.filter_by(id=quest_id).first()
        if not quest:
            current_app.logger.error(f'quest {quest_id} is not found')
            abort(404)

        if description:
            quest.description = description

        if title:
            quest.title = title

        if task_ids and len(task_ids) > 0:
            for task_id in task_ids:
                task = Task.query.filter_by(id=task_id).first()
                if not task:
                    current_app.logger.error(f'task {task_id} is not found')
                    abort(404)

                task.quest_id = quest_id

        if links:
            quest.links = links

        if repository_name:
            repo = Repository.query.filter_by(name=repository_name).first()
            if repo:
                quest.project_id = repo.project_id

        if status:
            current_app.logger.info(f'Updating quest status {quest_id} to {status}')
            quest.status = status

        db.session.commit()

        return QuestResponseSchema().jsonify(quest)

