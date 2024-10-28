from flask.views import MethodView
from flask import current_app
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.sql import label
import json
import ast

from ..models.user import User
from ..utils.errors import abort
from ..logic.cuckoo import get_card, get_trello_card_link
from ..models.diary_log import DiaryLog, ExternalUserRole, UserRole
from ..models.project import Project, ProjectDelegator
from ..models.quest import Quest
from ..models.repository import Repository
from ..models.task import Task
from ..models.upwork import WorkRecordUpworkDiary
from ..models.work import Work
from ..models.work_record import WorkRecord
from ..schemas.quest import ClientQuestsResponseSchema
from ..schemas.project import (
    ProjectBudgetReviewSchema,
    ProjectRequestSchema
)
from ..schemas.client import ClientRepositoriesResponseSchema
from ..utils.auth import activated_jwt_required
from ..utils.db import db
from ..utils.marshmallow import parser


class ListClientRepositories(MethodView):
    @activated_jwt_required
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if not user:
            raise Exception('user not found')
        
        repos = None
        if user.admin:
            repos = Repository.query \
                .join(Project, Repository.project_id == Project.id ) \
                .all()
        else:
            repos = Repository.query \
                .join(ProjectDelegator, Repository.project_id == ProjectDelegator.project_id ) \
                .join(Project, Repository.project_id == Project.id ) \
                .filter(ProjectDelegator.user_id == user_id ) \
                .all()
        
        
        return ClientRepositoriesResponseSchema(many=True).jsonify(repos)

class ProjectWorkTimeReview(MethodView):
    @activated_jwt_required
    @parser.use_args(ProjectRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, project_id):
        
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if not user:
            raise Exception('user not found')
        
        if not user.admin:
            project = ProjectDelegator.query \
                .filter(ProjectDelegator.user_id == user_id) \
                .filter(ProjectDelegator.project_id == project_id) \
                .first()
            if not project:
                abort(401)
        
        
        
        
        contributors = db.session.query( \
                label('year', db.func.year(WorkRecord.created)), \
                label('month', db.func.month(WorkRecord.created)), \
                label('time', db.func.sum(WorkRecordUpworkDiary.upwork_duration_seconds)/60/60) \
            ) \
            .join(WorkRecord, WorkRecordUpworkDiary.work_record_id == WorkRecord.id) \
            .join(WorkRecord.work) \
            .join(Work.task) \
            .outerjoin(Task.repository) \
            .filter(Repository.project_id == project_id) \
            .group_by(db.func.year(WorkRecord.created), db.func.month(WorkRecord.created)) \
            .order_by(db.func.year(WorkRecord.created), db.func.month(WorkRecord.created)) \
            .all()

        date_range = [(c[0],c[1]) for c in contributors]

        project_name = Project.query.filter_by(id=project_id).one().name
        external = db.session.query(
                label('year', db.func.year(DiaryLog.date)), \
                label('month', db.func.month(DiaryLog.date)), \
                label('time', db.func.sum(DiaryLog.duration_hours)) \
            ) \
            .join(DiaryLog.user_role) \
            .filter(DiaryLog.project == project_name) \
            .add_column(ExternalUserRole.role) \
            .group_by(db.func.year(DiaryLog.date), db.func.month(DiaryLog.date), ExternalUserRole.role) \
            .order_by(db.func.year(DiaryLog.date), db.func.month(DiaryLog.date)) \
            .all()


        date_range.extend(x for x in [(y[0],y[1]) for y in external] if x not in date_range)
        budget_reviews = []
        for (year,month) in date_range:
            period_budget = {
                'date': f'{year}-{int(month):02d}',
                'budget': []
            }
            contributors_period_budget = [item for item in contributors if item[0] == year and item[1] == month]
            for cpb in contributors_period_budget:
                period_budget['budget'].append({'name': UserRole.CONTRIBUTOR.name, 'amount': cpb[2]})
            external_period_budget = [item for item in external if item[0] == year and item[1] == month]
            for epb in external_period_budget:
                period_budget['budget'].append({'name': epb[3].name, 'amount': epb[2]})

            budget_reviews.append(period_budget)

        return ProjectBudgetReviewSchema().jsonify({
            'budgetReviews': budget_reviews
        })

class ProjectQuests(MethodView):
    @activated_jwt_required
    @parser.use_args(ProjectRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, project_id, page, results_per_page):
        
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if not user:
            raise Exception('user not found')
        
        if not user.admin:
            project = ProjectDelegator.query \
                .filter(ProjectDelegator.user_id == user_id) \
                .filter(ProjectDelegator.project_id == project_id) \
                .first()
            if not project:
                abort(401)
        
        quests = Quest.query \
            .filter(Quest.project_id == project_id) \
            .order_by(Quest.created.desc()) \
            .paginate(page=page, per_page=results_per_page, error_out=False)
                    
        client_quests = []
        for quest in quests:
            net_time = db.session.query(db.func.sum(WorkRecordUpworkDiary.net_duration_seconds)) \
            .join(WorkRecord, WorkRecordUpworkDiary.work_record_id == WorkRecord.id) \
            .join(WorkRecord.work) \
            .join(Work.task) \
            .filter(Task.quest_id == quest.id) \
            .scalar()

            iteration = None
            progress = None
            trello_link = None
            trello_card = get_card(quest.id)
            
            # the following extracts the checklists json from the card object then 
            # assigns the iteration as the length of lists
            # it also calculates the progress of the last checklist between 0 - 100
            # in addition the link to the trello card is assugned to the client quest
            if trello_card:
                if trello_card.get('shortLink'):
                    trello_link = f'https://trello.com/c/{trello_card["shortLink"]}'
                check_lists = trello_card['checklists']
                try:
                    if check_lists and len(check_lists) > 2:
                        lists = ast.literal_eval(json.loads(f'"{check_lists}"'))
                        iteration = len(lists)
                        last_checklist = lists[-1]
                        denominator = len(last_checklist['checkItems'])
                        numerator = len([item for item in last_checklist['checkItems'] if item['state'] == 'complete'])
                        progress = 0 if not denominator else (numerator / denominator) * 100
                except Exception as ex:
                    current_app.logger.error(f'failed to parse checklists "{check_lists}": {str(ex)}')

            client_quest = {
                'quest': quest,
                'net_time': net_time,
                'iteration': iteration,
                'progress': progress,
                'trello_link': trello_link
            }

            client_quests.append(client_quest)

        return ClientQuestsResponseSchema().jsonify({
            'quests': client_quests,
            'page': page,
            'total_count': quests.total
        })
