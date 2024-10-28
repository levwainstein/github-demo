from flask import current_app
from flask.views import MethodView

from sqlalchemy import and_
from sqlalchemy.sql import label
from sqlalchemy.orm import aliased
from flask_jwt_extended import get_jwt_identity


from ..jobs.task import prepare_cuckoo_task
from ..models.project import Project, ProjectDelegator
from ..models.user import User
from ..models.repository import Repository
from ..models.skill import Skill, TaskTemplateSkill
from ..models.task_template import TaskTemplate
from ..models.task_context import TaskContext
from ..models.quest import Quest, QuestStatus, QuestType, SuccessCriteria
from ..schemas import EmptyResponseSchema
from ..utils.slack_bot import notify_new_task_description
from ..utils.errors import abort

from ..logic.cuckoo import CuckooEvent, dispatch_cuckoo_event
from ..models.tag import Tag
from ..models.task_classification import TaskClassification, TaskTypeClassification
from ..logic.work_mappers import code_qa
from ..models.task import Task, TaskStatus, TaskType
from ..schemas.delegation import (
    DelegateQuestRequestSchema,
    DelegateQuestResponseSchema,
    DelegateTaskRequestSchema,
    DelegateTaskSchema,
    DelegationTemplateResponseSchema,
    DelegationTemplatesResponseSchema,
    DelegatorRepositoriesResponseSchema,
    UpsertTemplateRequestSchema,
)
from ..utils.auth import activated_jwt_required
from ..utils.db import db
from ..utils.marshmallow import parser

class DelegationTemplateCRUD(MethodView):
    @activated_jwt_required
    @parser.use_args(UpsertTemplateRequestSchema(), as_kwargs=True)
    def post(self, repository_id, name, task_description, skills = [], task_classification=None, task_type=TaskType.UPDATE_FUNCTION):
        template = TaskTemplate(
            name=name, 
            task_description=task_description, 
            repository_id=repository_id, 
            task_type=task_type,
            task_classification=task_classification,
            skills=[Skill.get_or_create(s) for s in skills or []],
        )
        db.session.add(template)
        db.session.commit()

        return DelegationTemplateResponseSchema().jsonify(template)
    
    @activated_jwt_required
    @parser.use_args(UpsertTemplateRequestSchema(), as_kwargs=True)
    def put(self, template_id, name, task_description, repository_id, skills = None, task_classification=None):
        template = TaskTemplate.query.filter_by(id=template_id).first()
        if not template:
            abort(404)
        if template.name != name:
            template.name = name
        if template.task_description != task_description:
            template.task_description = task_description
        if template.task_classification != task_classification:
            template.task_classification = task_classification
        if template.repository_id != repository_id:
            template.repository_id = repository_id

        if skills != None:
            template_skills = TaskTemplateSkill.query.filter_by(task_template_id=template_id).all()
            for ts in template_skills:
                db.session.delete(ts)
            sk =  [Skill.get_or_create(s) for s in skills or []]
            db.session.commit()
            for s in sk:
                template_skill = TaskTemplateSkill(task_template_id=template_id, skill_id=s.id)
                db.session.add(template_skill)
        db.session.commit()

        return EmptyResponseSchema().jsonify()
    
    @activated_jwt_required
    def delete(self, template_id):
        template = TaskTemplate.query.filter_by(id=template_id).first()
        if not template:
            abort(404)

        db.session.delete(template)
        db.session.commit()

        current_app.logger.info(f'Deleted template ID {template_id}\n')

        return EmptyResponseSchema().jsonify()


class DelegatorRepositories(MethodView):
    @activated_jwt_required
    def get(self):
        user_id = get_jwt_identity()
        repos = Repository.query \
            .join(ProjectDelegator, Repository.project_id == ProjectDelegator.project_id ) \
            .filter(ProjectDelegator.user_id == user_id ) \
            .all()
        
        return DelegatorRepositoriesResponseSchema().jsonify({
            'repositories': repos
        })
    
class DelegationTemplates(MethodView):
    @activated_jwt_required
    def get(self):
        user_id = get_jwt_identity()

        repo_templates = TaskTemplate.query \
            .join(Repository, Repository.id == TaskTemplate.repository_id ) \
            .join(ProjectDelegator, Repository.project_id == ProjectDelegator.project_id ) \
            .filter(ProjectDelegator.user_id == user_id ) \
            .all()

        return DelegationTemplatesResponseSchema().jsonify({
            'templates': repo_templates
        })
    
class DelegateTask(MethodView):
    # create (delegate) new task from the structured delegation flow
    @activated_jwt_required
    @parser.use_args(DelegateTaskRequestSchema(), as_kwargs=True)
    def post(self, description, title, repository_id, task_classification=None, type=TaskType.CUCKOO_CODING, priority=2, tags=None, skills=None, feature=None, chain_review=False, max_chain_iterations=None, chain_description=None, delegation_time_seconds=None, context=None):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if not user:
            abort(404)

        repository = Repository.query \
            .filter(Repository.id == repository_id) \
            .first()
        if not repository:
            abort(404)

        project_tag = 'project:' + repository.project.name
        task_tags = (tags or []) + [project_tag]

        advanced_options = {}
        if chain_review:
            advanced_options['chainReview'] = chain_review
            advanced_options['maxChainIterations'] = max_chain_iterations or code_qa.DEFAULT_QA_ITERATIONS
            advanced_options['chainDescription'] = chain_description or code_qa.DEFAULT_QA_DESCRIPTION_PREFIX
        if feature:
            advanced_options['feature'] = feature

        current_app.logger.info(f'Structurally delegating a task {description}')

        # adjust description to include the repo and branch that would be created
        # TODO: remove this after supporting the new delegation flow where the repo/branch details are available on the side
        adjusted_description = description
        adjusted_description += '\n\n---\n\n'
        if repository:
            adjusted_description += f'**Github repo:** [{repository.name}]({repository.url}) (an invite will be sent if you accept the task)\n\n'
        branch_name = f'external/<your_github_user>/{title.lower().replace(" ", "-")}'
        adjusted_description += f'**Github branch for this task:** `{branch_name}`'
        adjusted_description += '\n\n---\n\n'

        # Begin a transaction
        with db.session.begin_nested():
            # Create the task and get a task ID
            task = Task.from_delegation(
                delegating_user_id=user_id,
                description=adjusted_description,
                title=title,
                status=TaskStatus.NEW,
                task_type=type,
                priority=priority,
                delegation_time_seconds=delegation_time_seconds,
                tags=[Tag.get_or_create(t) for t in task_tags or []],
                skills=[Skill.get_or_create(s) for s in skills or []],
                advanced_options=advanced_options,
                repository_id=repository_id
                
            )
            db.session.add(task)
            db.session.flush()
            if task_classification != None:
                task_classification_enum = TaskTypeClassification(task_classification)
                task_classification = TaskClassification(task.id, task_classification_enum)
                db.session.add(task_classification)
                db.session.flush()

            if context != None:
                [TaskContext.create(c['file'], c['entity'], c['potential_use'], task.id) for c in context or []]
                db.session.flush()

            # schedule job to prepare the work item
            prepare_cuckoo_task.queue(
                task.id
            )

            # notify new description
            notify_new_task_description(task)

            # notify cuckoo that a task was created to create the corresponding trello card
            payload = {
                'eventType': CuckooEvent.TASK_DELEGATED.name,
                'githubUser': user.github_user,
                'trelloUser': user.trello_user,
                'githubRepositoryUrl': repository.url,
                'name': title,
                'description': description,
                'labels': skills,
                'taskId': task.id
            }
            res = dispatch_cuckoo_event(
                task.id,
                payload
            )
            if not res:
                current_app.logger.error('error notifying cuckoo')
                db.session.rollback()
                abort(500, code='cuckoo_notification_failed')
            
            db.session.commit() # Commit the nested transaction

        return DelegateTaskSchema().jsonify(task)
    
class DelegateQuest(MethodView):
    # create (delegate) new quest from the structured delegation flow
    @activated_jwt_required
    @parser.use_args(DelegateQuestRequestSchema(), as_kwargs=True)
    def post(self, description, title, project_id, quest_type=QuestType.FEATURE, success_criteria=None, links=None, delegation_time_seconds=None):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if not user:
            abort(404)

        project = Project.query \
            .filter(Project.id == project_id) \
            .first()
        if not project:
            abort(404)

        current_app.logger.info(f'Structurally delegating a quest {description}')

        # Begin a transaction
        with db.session.begin_nested():
            # Create the quest and get a quest ID
            quest = Quest(
                delegating_user_id=user_id,
                description=description,
                title=title,
                status=QuestStatus.NEW,
                quest_type=quest_type,
                links=links,
                project_id=project_id,
                delegation_time_seconds=delegation_time_seconds
            )
            db.session.add(quest)
            db.session.flush()   # Flush to get the quest.id

            if success_criteria and len(success_criteria) > 0:
                for sc in success_criteria:
                    criter = SuccessCriteria(quest.id, sc.get('description'), sc.get('title'), sc.get('explanation', None))
                    db.session.add(criter)
            db.session.flush()

            # notify cuckoo that a quest was created to create the corresponding trello card
            payload = {
                'eventType': CuckooEvent.QUEST_DELEGATED.name,
                'questId': quest.id,
                'githubUser': user.github_user,
                'trelloUser': user.trello_user,
                'trelloLink': project.trello_link,
                'name': title,
                'description': description,
                'links': links,
                'successCriteria': success_criteria
            }

            res = dispatch_cuckoo_event(
                quest.id,
                payload
            )
            if not res:
                current_app.logger.error('error notifying cuckoo')
                db.session.rollback()
                abort(500, code='cuckoo_notification_failed')

            db.session.commit()  # Commit the nested transaction

        return DelegateQuestResponseSchema().jsonify(quest)