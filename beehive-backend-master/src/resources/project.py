from datetime import date, timedelta, datetime
from flask import current_app
from flask.views import MethodView

from sqlalchemy.sql import label


from ..logic.cuckoo import get_trello_card_link
from ..logic.project import parse_links
from ..models.diary_log import DiaryLog, ExternalUserRole, UserRole
from ..models.project import Project
from ..models.tag import Tag, TaskTag
from ..models.task import Task, TaskStatus, TaskType
from ..models.upwork import WorkRecordUpworkDiary
from ..models.user import User
from ..models.work import Work, WorkStatus, WorkType
from ..models.work_record import WorkRecord
from ..resources.shared_queries import get_contributor_stats_specific_project
from ..schemas.project import (
    ListProjectsResponseSchema,
    ProjectActivityResponseSchema,
    ProjectBudgetReviewSchema,
    ProjectContributorsResponseSchema,
    ProjectDelayedTasksResponseSchema,
    ProjectQueueRequestSchema,
    ProjectQueueResponseSchema,
    ProjectRequestSchema
)
from ..utils.auth import admin_jwt_required
from ..utils.db import db
from ..utils.marshmallow import parser


class ListProjects(MethodView):
    @admin_jwt_required
    def get(self):
        current_app.logger.info('Listing Projects')

        projects = Tag.query \
            .filter(Tag.name.contains('project:')) \
            .outerjoin(TaskTag, Tag.id == TaskTag.tag_id) \
            .outerjoin(Task, TaskTag.task_id == Task.id) \
            .group_by(Tag.id) \
            .order_by(Tag.id) \
            .with_entities(Tag.id, Tag.name, label('min_created', db.func.min(Task.created))) \
            .all()
        projects = [{'project_id': p[0], 'project_name': p[1][8:], 'date': p[2] } for p in projects]
        # TODO: use task fetched to query cuckoo for the trello board id

        return ListProjectsResponseSchema().jsonify({
            'projects': projects
        })

class ProjectQueue(MethodView):
    @admin_jwt_required
    @parser.use_args(ProjectQueueRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, project_id):
        current_app.logger.info('Fetching ProjectQueue')
        
        query = db.session.query(Work.task_id, db.func.max(Work.created).label('max')) \
            .group_by(Work.task_id) \
            .subquery()    
        
        works = db.session.query(query.columns.task_id, Work.created, Work.status, Work.work_type) \
            .join(Work, Work.created == query.columns.max and Work.task_id == query.columns.task_id) \
            .subquery()    

        tasks = db.session.query(Task.status, works.columns.status, Task.id, Task.task_type, works.columns.work_type, Task.created, works.columns.created) \
            .join(works, works.columns.task_id == Task.id) \
            .filter(Task.tags.any(TaskTag.tag_id == project_id)) \
            .filter(Task.created > current_app.config['CUCKOO_START_DATE']) \
            .all()

        pending = [t for t in tasks if t[0] in ([TaskStatus.PENDING, TaskStatus.MODIFICATIONS_REQUESTED])  and t[1] != WorkStatus.UNAVAILABLE]
        in_review = [t for t in tasks if (t[0] in [TaskStatus.SOLVED] and t[1] != WorkStatus.UNAVAILABLE) or (t[0] in [TaskStatus.INVALID])]
        in_progress = [t for t in tasks if t[0] in ([TaskStatus.IN_PROCESS])]

        trello_links = get_trello_card_link([t[2] for t in tasks])
        pending_trello_links = [l for l in trello_links if l['task_id'] in [t[2] for t in pending]]
        in_progress_trello_links = [l for l in trello_links if l['task_id'] in [t[2] for t in in_progress]]
        in_review_trello_links = [l for l in trello_links if l['task_id'] in [t[2] for t in in_review]]

        return ProjectQueueResponseSchema().jsonify({
            'pending': len(pending), 
            'in_review': len(in_review), 
            'in_progress': len(in_progress),
            'pending_trello_links': pending_trello_links, 
            'in_progress_trello_links': in_progress_trello_links,
            'in_review_trello_links': in_review_trello_links
        })

class ProjectActivity(MethodView):
    @admin_jwt_required
    @parser.use_args(ProjectRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, project_id):
        current_app.logger.info('Fetching ProjectActivity') 
        n = 100
        n_days_ago = date.today() - timedelta(days=n)

        tasks_delegated = db.session.query(db.func.date_format(Task.created, '%Y-%m-%d'), db.func.count(), db.func.group_concat(Task.id)) \
            .filter(Task.tags.any(TaskTag.tag_id == project_id)) \
            .filter(Task.created > n_days_ago) \
            .group_by(db.func.date_format(Task.created, '%Y-%m-%d')) \
            .all()

        tasks_solved = db.session.query(db.func.date_format(Task.updated, '%Y-%m-%d'), db.func.count(), db.func.group_concat(Task.id)) \
            .filter(Task.tags.any(TaskTag.tag_id == project_id)) \
            .filter(Task.status.in_([TaskStatus.ACCEPTED])) \
            .filter(Task.updated > n_days_ago) \
            .group_by(db.func.date_format(Task.updated, '%Y-%m-%d')) \
            .all()
        
        # work items that their status were updated to completed. the work.updated represents the time that it was solved
        work_completed = db.session.query(db.func.date_format(Work.updated, '%Y-%m-%d'), db.func.count(), db.func.group_concat(Work.task_id)) \
            .join(Work.task) \
            .filter(Work.status == WorkStatus.COMPLETE) \
            .filter(Task.tags.any(TaskTag.tag_id == project_id)) \
            .filter(Work.updated > n_days_ago) \
            .group_by(db.func.date_format(Work.updated, '%Y-%m-%d')) \
            .all()
        
        # work items the were created when a tech lead drags back from in review to beehive tasks
        work_reviewed = db.session.query(db.func.date_format(Work.updated, '%Y-%m-%d'), db.func.count(), db.func.group_concat(Work.task_id)) \
            .join(Work.task) \
            .filter(Work.work_type.in_([WorkType.REVIEW_TASK, WorkType.CUCKOO_ITERATION])) \
            .filter(Work.status == WorkStatus.COMPLETE) \
            .filter(Task.tags.any(TaskTag.tag_id == project_id)) \
            .filter(Work.updated > n_days_ago) \
            .group_by(db.func.date_format(Work.updated, '%Y-%m-%d')) \
            .all()
        
        tasks_delegated_task_ids = [(t[0], t[2]) for t in tasks_delegated]
        tasks_solved_task_ids = [(t[0], t[2]) for t in tasks_solved]
        work_completed_task_ids = [(t[0], t[2]) for t in work_completed]
        work_reviewed_task_ids = [(t[0], t[2]) for t in work_reviewed]
        
        flatten_links = map(lambda result: (result[0], result[1].split(',')), tasks_delegated_task_ids + tasks_solved_task_ids + work_completed_task_ids + work_reviewed_task_ids)
        all_ids = [item for sublist in [r[1] for r in flatten_links] for item in sublist]
        all_links = get_trello_card_link(all_ids)

        tasks_delegated_task_links_parsed = parse_links(tasks_delegated_task_ids, all_links)
        tasks_solved_task_links_parsed = parse_links(tasks_solved_task_ids, all_links)
        work_completed_task_links_parsed = parse_links(work_completed_task_ids, all_links)
        work_reviewed_task_links_parsed = parse_links(work_reviewed_task_ids, all_links)

        tasks_delegated_count = [(t[0], t[1]) for t in tasks_delegated]
        tasks_solved_count = [(t[0], t[1]) for t in tasks_solved]
        work_reviewed_count = [(t[0], t[1]) for t in work_reviewed]
        work_completed_count = [(t[0], t[1]) for t in work_completed]

        activities = []
        for day in [str(date.today() - timedelta(days = day)) for day in range(n)]:
            activities.append({
                "date": day,
                "tasks_delegated": dict(tasks_delegated_count).get(day, 0),
                "tasks_completed": dict(tasks_solved_count).get(day, 0),
                "work_items_solved": dict(work_completed_count).get(day, 0),
                "work_items_reviewed": dict(work_reviewed_count).get(day, 0) + dict(tasks_solved_count).get(day, 0),
                "tasks_delegated_links": dict(tasks_delegated_task_links_parsed).get(day, []),
                "tasks_completed_links": dict(tasks_solved_task_links_parsed).get(day, []),
                "work_items_solved_links": dict(work_completed_task_links_parsed).get(day, []),
                "work_items_reviewed_links": dict(work_reviewed_task_links_parsed).get(day, []) + dict(tasks_solved_task_links_parsed).get(day, [])
            })

        return ProjectActivityResponseSchema().jsonify({
            'activities': activities
        })

class ProjectContributors(MethodView):
    @admin_jwt_required
    @parser.use_args(ProjectRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, project_id):

        current_app.logger.info('Fetching ProjectContributors')
        contributors = []
        users = db.session.query(User) \
                .outerjoin(WorkRecord, User.id == WorkRecord.user_id) \
                .join(WorkRecord.work) \
                .join(Work.task) \
                .filter(Task.tags.any(TaskTag.tag_id == project_id)) \
                .all()
        for user in users:
            contributors.append(get_contributor_stats_specific_project(user, project_id))

        return ProjectContributorsResponseSchema().jsonify({
            'contributors': contributors
        })

class ProjectBudgetReview(MethodView):
    @admin_jwt_required
    @parser.use_args(ProjectQueueRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, project_id):
        current_app.logger.info('Fetching ProjectBudget')

        contributors = db.session.query( \
                label('year', db.func.year(WorkRecord.created)), \
                label('month', db.func.month(WorkRecord.created)), \
                label('cost', db.func.sum(WorkRecordUpworkDiary.upwork_cost)), \
                label('hours', db.func.sum(WorkRecordUpworkDiary.upwork_duration_seconds/3600)) \
            ) \
            .join(WorkRecord, WorkRecordUpworkDiary.work_record_id == WorkRecord.id) \
            .join(WorkRecord.work) \
            .join(Work.task) \
            .filter(Task.tags.any(TaskTag.tag_id == project_id)) \
            .group_by(db.func.year(WorkRecord.created), db.func.month(WorkRecord.created)) \
            .order_by(db.func.year(WorkRecord.created), db.func.month(WorkRecord.created)) \
            .all()

        date_range = [(c[0],c[1]) for c in contributors]

        tag_name = Tag.query.filter_by(id=project_id).one().name.replace('project:','')
        external = db.session.query(
                label('year', db.func.year(DiaryLog.date)), \
                label('month', db.func.month(DiaryLog.date)), \
                label('cost', db.func.sum(DiaryLog.cost)), \
                label('hours', db.func.sum(DiaryLog.duration_hours)) \
            ) \
            .join(DiaryLog.user_role) \
            .filter(DiaryLog.project == tag_name) \
            .add_column(ExternalUserRole.role) \
            .group_by(db.func.year(DiaryLog.date), db.func.month(DiaryLog.date), ExternalUserRole.role) \
            .order_by(db.func.year(DiaryLog.date), db.func.month(DiaryLog.date)) \
            .all()

        date_range.extend(x for x in [(y[0],y[1]) for y in external] if x not in date_range)

        budget_reviews = []
        for (year,month) in date_range:
            period_budget = {
                'date': f'{year}-{month}',
                'budget': []
            }
            contributors_period_budget = [item for item in contributors if item[0] == year and item[1] == month]
            for cpb in contributors_period_budget:
                period_budget['budget'].append({'name': UserRole.CONTRIBUTOR.name, 'amount': cpb[2], 'hours': cpb[3]})
            external_period_budget = [item for item in external if item[0] == year and item[1] == month]
            for epb in external_period_budget:
                period_budget['budget'].append({'name': epb[4].name, 'amount': epb[2], 'hours': epb[3]})

            budget_reviews.append(period_budget)

        return ProjectBudgetReviewSchema().jsonify({
            'budgetReviews': budget_reviews
        })

class ProjectDelayedTasks(MethodView):
    @admin_jwt_required
    @parser.use_args(ProjectRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, project_id):

        current_app.logger.info('Fetching ProjectDelayedTasks')

        tasks_billable = db.session.query(Task.id.label('task_id'), db.func.sum(WorkRecordUpworkDiary.net_duration_seconds).label('billable')) \
                .outerjoin(Work, Work.task_id == Task.id) \
                .outerjoin(WorkRecord, WorkRecord.work_id == Work.id) \
                .outerjoin(WorkRecordUpworkDiary, WorkRecordUpworkDiary.work_record_id == WorkRecord.id) \
                .group_by(Task.id) \
                .subquery()      

        query = db.session.query(Work.task_id, db.func.max(Work.created).label('max')) \
            .group_by(Work.task_id) \
            .subquery()    
        
        works = db.session.query(query.columns.task_id, Work.status) \
            .join(Work, Work.created == query.columns.max and Work.task_id == query.columns.task_id) \
            .subquery()
        
        results = db.session.query(Task, works.columns.status, tasks_billable.columns.billable) \
            .join(works, works.columns.task_id == Task.id) \
            .join(tasks_billable, tasks_billable.columns.task_id == Task.id) \
            .filter(Task.tags.any(TaskTag.tag_id == project_id)) \
            .filter(Task.created >  current_app.config['CUCKOO_START_DATE']) \
            .all()
        
        tasks = []
        in_progress = [t for t in results if t[0].status in ([TaskStatus.IN_PROCESS]) and t[0].created < datetime.utcnow() - timedelta(hours=48)]
        tasks.extend(in_progress)
        pending = [t for t in results if t[0].status in ([TaskStatus.PENDING, TaskStatus.MODIFICATIONS_REQUESTED]) and t[1] == WorkStatus.AVAILABLE and t[0].created < datetime.utcnow() - timedelta(hours=24)]
        tasks.extend(pending)
        in_review = [t for t in results if t[0].status in ([TaskStatus.INVALID, TaskStatus.SOLVED]) and t[0].created < datetime.utcnow() - timedelta(hours=24)]
        tasks.extend(in_review)
        backlog = [t for t in results if t[0].status in ([TaskStatus.NEW]) and t[1] == WorkStatus.AVAILABLE and t[0].created < datetime.utcnow() - timedelta(hours=48)]
        tasks.extend(backlog)

        trello_links = get_trello_card_link([t[0].id for t in tasks])
        delayedTasks = [{
                'id': t[0].id,
                'created_at': t[0].created,
                'updated_at': t[0].updated,
                'task_name': t[0].description,
                'skills': t[0].skills,
                'status': t[0].status,
                'billable_time': t[2],
                'priority': t[0].priority,
                'link': next(iter([l for l in trello_links if l['task_id'] == t[0].id]), None)
                } for t in tasks]
        return ProjectDelayedTasksResponseSchema().jsonify({
            'delayedTasks': delayedTasks
        })
