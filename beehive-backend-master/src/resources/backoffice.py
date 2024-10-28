from datetime import datetime, timedelta
import time

from flask import current_app
from flask.views import MethodView
from sqlalchemy.orm import joinedload

from ..models.task import Task, TaskStatus
from ..models.work import Work, WorkStatus
from ..models.work_record import WorkRecord
from ..models.user_code import UserCode, UserCodeType
from ..models.diary_log import DiaryLog, ExternalUserRole
from ..models.project import Project
from ..models.user import User
from ..models.skill import Skill, UserSkill
from ..models.tag import Tag, UserTag

from ..schemas import EmptyResponseSchema
from ..schemas.backoffice import (
    UpdateTaskFeedbackRequestSchema,
    UpdateWorkPriorityRequestSchema,
    CreateUserCodeRequestSchema,
    CreateUserCodeResponseSchema,
    TaskWorkResponseSchema,
    BackofficeUserProfileRequestSchema,
    BackofficeUserProfileResponseSchema,
    TagRequestSchema,
    TagResponseSchema,
    SkillRequestSchema,
    DiaryLogRequestSchema
)
from ..utils.auth import inner_auth
from ..utils.db import db
from ..utils.errors import abort
from ..utils.marshmallow import parser


class TaskUpdateFeedback(MethodView):
    @inner_auth
    @parser.use_args(UpdateTaskFeedbackRequestSchema(), as_kwargs=True)
    def put(self, task_id, feedback=None):
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            abort(404)

        if feedback is not None:
            if feedback == '':
                current_app.logger.info(f'Reseting feedback for {task_id}')
                task.feedback = None
            else:
                current_app.logger.info(f'Updating feedback for {task_id} to be {feedback}')
                task.feedback = feedback

                # set task status to invalid
                task.status = TaskStatus.INVALID

        db.session.commit()

        return EmptyResponseSchema().jsonify()

class WorkUpdatePriority(MethodView):
    @parser.use_args(UpdateWorkPriorityRequestSchema(), as_kwargs=True)
    def put(self, work_id, priority):
        work = Work.query.filter_by(id=work_id).first()
        if not work:
            abort(404)
        task = Task.query.filter_by(id=work.task_id).first()
        task.priority = priority
        work.priority = priority
        db.session.commit()

        return EmptyResponseSchema().jsonify()


class UserCodeCreate(MethodView):
    @inner_auth
    @parser.use_args(CreateUserCodeRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, expires=None):
        expires_at = None

        if expires:
            expires_at = datetime.utcnow() + timedelta(days=int(expires.rstrip('d')))

        # create user code
        new_user_code = UserCode(code_type=UserCodeType.REGISTRATION, expires=expires_at)
        db.session.add(new_user_code)
        db.session.commit()

        return CreateUserCodeResponseSchema().jsonify({'code': new_user_code.id})


class BackofficeUserProfile(MethodView):
    @inner_auth
    def get(self, user_id):
        """
        Get tags and skills of an existing user
        """
        user = User.query.filter_by(id=user_id).first()
        if not user:
            abort(404)
 
        return BackofficeUserProfileResponseSchema().jsonify({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'github_user': user.github_user,
            'trello_user': user.trello_user,
            'upwork_user': user.upwork_user,
            'availability_weekly_hours': user.availability_weekly_hours,
            'price_per_hour': user.price_per_hour,
            'tags': user.tags,
            'skills': user.skills
        })

    @inner_auth
    @parser.use_args(BackofficeUserProfileRequestSchema(), as_kwargs=True)
    def put(self, user_id, tags=None, skills=None):
        """
        Update an existing user profile by backoffice client
        """
        user = User.query.filter_by(id=user_id).first()
        if not user:
            abort(404)
        
        if tags:            
            for tag in tags:
                # create tag if does not exist
                existing_tag = Tag.query.filter_by(name=tag).first()
                if not existing_tag:
                    existing_tag = Tag(name=tag)
                    db.session.add(existing_tag)
                    current_app.logger.info(f'Created new tag "{tag}"')

                existing_user_tag = UserTag.query.filter_by(user_id=user_id, tag_id=existing_tag.id).first()
                if not existing_user_tag:
                    existing_user_tag = UserTag(user_id=user_id, tag_id=existing_tag.id)
                    db.session.add(existing_user_tag)
                    current_app.logger.info(f'Added tag "{tag}" to user {user_id}')
                else:
                    current_app.logger.info(f'User {user_id} already tagged "{tag}"')

        if skills:
            for skill in skills:
                # create skill if does not exist
                existing_skill = Skill.query.filter_by(name=skill).first()
                if not existing_skill:
                    existing_skill = Skill(name=skill)
                    db.session.add(existing_skill)
                    current_app.logger.info(f'Created new skill "{skill}"')
                
                existing_user_skill = UserSkill.query.filter_by(user_id=user_id, skill_id=existing_skill.id).first()
                if not existing_user_skill:
                    existing_user_skill = UserSkill(user_id=user_id, skill_id=existing_skill.id)
                    db.session.add(existing_user_skill)
                    current_app.logger.info(f'Added skill "{skill}" to user {user_id}')
                else:
                    current_app.logger.info(f'User {user_id} already skilled "{skill}"')
        
        db.session.commit()
        db.session.refresh(user)
        return BackofficeUserProfileResponseSchema().jsonify({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'github_user': user.github_user,
            'trello_user': user.trello_user,
            'upwork_user': user.upwork_user,
            'availability_weekly_hours': user.availability_weekly_hours,
            'price_per_hour': user.price_per_hour,
            'tags': user.tags,
            'skills': user.skills
        })

    @inner_auth
    @parser.use_args(BackofficeUserProfileRequestSchema(), as_kwargs=True)
    def delete(self, user_id, tags=None, skills=None):
        """
        Removes tags or skills from an existing user
        """
        user = User.query.filter_by(id=user_id).first()
        if not user:
            abort(404)

        if tags:            
            for tag in tags:
                existing_tag = Tag.query.filter_by(name=tag).first()
                if not existing_tag:
                    abort(404)

                user_tags = UserTag.query.filter_by(tag_id=existing_tag.id, user_id=user_id).all()
                for user_tag in user_tags:
                    db.session.delete(user_tag)

        if skills:
            for skill in skills:
                existing_skill = Skill.query.filter_by(name=skill).first()
                if not existing_skill:
                    abort(404)

                user_skills = UserSkill.query.filter_by(skill_id=existing_skill.id, user_id=user_id).all()
                for user_skill in user_skills:
                    db.session.delete(user_skill)

        db.session.commit()
        db.session.refresh(user)
        return BackofficeUserProfileResponseSchema().jsonify({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'github_user': user.github_user,
            'trello_user': user.trello_user,
            'upwork_user': user.upwork_user,
            'availability_weekly_hours': user.availability_weekly_hours,
            'price_per_hour': user.price_per_hour,
            'tags': user.tags,
            'skills': user.skills
        })



class TagCRUD(MethodView):
    @inner_auth
    def get(self):
        """
        Get all tags available
        """

        current_app.logger.info(f'Getting tags')

        tags = Tag.query.all()

        return TagResponseSchema(many=True).jsonify(tags)

    @inner_auth
    @parser.use_args(TagRequestSchema(), as_kwargs=True)
    def post(self, tag_name):
        """
        Create a new tag
        """
        current_app.logger.info(f'Got request to add tag "{tag_name}"')

        existing_tag = Tag.query.filter_by(name=tag_name).first()
        if existing_tag:
            abort(400, code='tag_already_exists')

        # create tag
        new_tag = Tag(tag_name)
        db.session.add(new_tag)
        db.session.commit()

        return EmptyResponseSchema().jsonify()

    @inner_auth
    @parser.use_args(TagRequestSchema(), as_kwargs=True)
    def delete(self, tag_name):
        """
        Deletes a tag
        """
        
        current_app.logger.info(f'Got request to delete tag "{tag_name}"')
        
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            abort(404)

        db.session.delete(tag)
        db.session.commit()

        return EmptyResponseSchema().jsonify()



class SkillCRUD(MethodView):
    @inner_auth
    @parser.use_args(SkillRequestSchema(), as_kwargs=True)
    def post(self, skill_name):
        """
        Create a new skill
        """
        current_app.logger.info(f'Got request to add skill "{skill_name}"')

        existing_skill = Skill.query.filter_by(name=skill_name).first()
        if existing_skill:
            abort(400, code='skill_already_exists')

        # create skill
        new_skill = Skill(skill_name)
        db.session.add(new_skill)
        db.session.commit()

        return EmptyResponseSchema().jsonify()

    @inner_auth
    @parser.use_args(SkillRequestSchema(), as_kwargs=True)
    def delete(self, skill_name):
        """
        Deletes a skill
        """
        
        current_app.logger.info(f'Got request to delete skill "{skill_name}"')
        
        skill = Skill.query.filter_by(name=skill_name).first()
        if not skill:
            abort(404)

        db.session.delete(skill)
        db.session.commit()

        return EmptyResponseSchema().jsonify()


class ManualDiaryLog(MethodView):
    @inner_auth
    @parser.use_args(DiaryLogRequestSchema(), as_kwargs=True)
    def post(self, user_email, project, date, hours, text=None):
        """
        Create a new manual time diary log
        This endpoint is called from DiaryLogEntry Google App script: https://script.google.com/u/0/home/projects/10BwwL9392Srli93Y8LJlXmTdqNRKyEf9aKLsrPdA8VwUbPweiwqGrTxJ/edit
        Triggered by submitting the manual time log Google form: https://forms.gle/gtEVgEjMxGgs7Qez5 
        """
        current_app.logger.info(f'Got request to record manual diary log for "{user_email}" on project "{project}"')

        def to_beehive_project_name(name):
            name = name.lower().replace(' ', '_')
            match name:
                case 'blue_zones' | 'Blue Zones':
                    return 'bluezones'
                case 'c_light_technologies' | 'C Light Technologies':
                    return 'c_light_tech'
                case _:
                    return name

        project_name = to_beehive_project_name(project)
        p = Project.query.filter(Project.name == project_name).first()
        if not p:
            current_app.logger.error(f'project with name {project_name} not found')
        
        external_user_role = ExternalUserRole.query.filter(ExternalUserRole.email == user_email).first()
        if not external_user_role:
            current_app.logger.error(f'External user with email {user_email} not found')
            abort(404)
    
        # create diary log
        diary_log = DiaryLog(external_user_role.id, project_name, date, hours, text)
        db.session.add(diary_log)
        db.session.commit()

        return EmptyResponseSchema().jsonify()


# used only for testing. if work items per task is ever needed for client this can
# be moved accordingly
class TaskWork(MethodView):
    @inner_auth
    def get(self, task_id):
        task = Task.query.filter_by(id=task_id) \
            .options(joinedload(Task.works)) \
            .first()
        if not task:
            abort(404)

        return TaskWorkResponseSchema(many=True).jsonify(task.works)
