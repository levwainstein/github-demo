from statistics import mean
import time
import decimal

from flask import current_app
from flask.views import MethodView

from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import label

from ..logic.cuckoo import CuckooEvent, dispatch_cuckoo_event

from ..models.honeycomb import Honeycomb
from ..models.task import Task, TaskStatus, TaskType
from ..models.work import Work, WorkStatus, WorkType
from ..models.user import User
from ..models.work_record import WorkOutcome, WorkRecord
from ..models.upwork import UpworkDiary, WorkRecordUpworkDiary
from ..schemas.stats import (
    ContributorHistoryResponseSchema,
    GetActiveWorkResponseSchema,
    GetCompletedWorkResponseSchema,
    GetContributorsRequestSchema,
    GetContributorsResponseSchema,
    GetHoneycombsResponseSchema,
    GetInvalidTasksResponseSchema,
    GetPendingWorkResponseSchema,
    GetStatsRequestSchema,
    GetUsersResponseSchema,
    ProhibitWorkResponseSchema,
    ReserveWorkRequestSchema,
    ReserveWorkResponseSchema
)
from ..utils.auth import admin_jwt_required
from ..utils.db import db
from ..utils.errors import abort
from ..utils.marshmallow import parser
from ..utils.misc import camel_case_to_snake_case


class ActiveWork(MethodView):
    @admin_jwt_required
    @parser.use_args(GetStatsRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, page, results_per_page):
        current_app.logger.info('Fetching list of active work records')

        active_work_records = WorkRecord.query.filter_by(active=True) \
            .add_columns( \
                label(
                    'work_records_contributors_viewed',
                    db.func.count(db.distinct(WorkRecord.user_id))
                ) \
            ) \
            .group_by(WorkRecord.id) \
            .options(joinedload(WorkRecord.work).joinedload(Work.task)) \
            .paginate(page=page, per_page=results_per_page, error_out=False)


        # attach work records stats to each work item
        work = []
        for item in active_work_records.items:
            w = item[0]
            w.work_records_contributors_viewed = item.work_records_contributors_viewed
            work.append(w)

        return GetActiveWorkResponseSchema().jsonify({
            'work': work,
            'total_count': active_work_records.total,
            'page': page
        })


class PendingWork(MethodView):
    @admin_jwt_required
    @parser.use_args(GetStatsRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, page, results_per_page):
        current_app.logger.info('Fetching list of pending work items')

        # subquery to count and sum duration of work records
        work_record_stats = WorkRecord.query \
            .with_entities(WorkRecord.work_id) \
            .add_columns(
                label('work_records_count', db.func.count()),
                label(
                    'work_records_total_duration_seconds',
                    db.func.sum(WorkRecord.duration_seconds)
                ),
                label(
                    'work_records_contributors_viewed',
                    db.func.count(db.distinct(WorkRecord.user_id))
                )
            ) \
            .group_by(WorkRecord.work_id) \
            .subquery()

        # query for availble work items
        pending_work = Work.query \
            .outerjoin(work_record_stats, Work.id == work_record_stats.c.work_id) \
            .add_columns(work_record_stats.c.work_records_count, work_record_stats.c.work_records_total_duration_seconds, work_record_stats.c.work_records_contributors_viewed) \
            .options(joinedload(Work.task)) \
            .filter(Work.task_id == Task.id) \
            .filter(Work.status == WorkStatus.AVAILABLE) \
            .filter(Task.status.in_((TaskStatus.PENDING, TaskStatus.IN_PROCESS, TaskStatus.MODIFICATIONS_REQUESTED))) \
            .paginate(page=page, per_page=results_per_page, error_out=False)

        # attach work records stats to each work item
        work = []
        for item in pending_work.items:
            w = item[0]
            w.work_records_count = item.work_records_count
            w.work_records_total_duration_seconds = item.work_records_total_duration_seconds
            w.work_records_contributors_viewed = item.work_records_contributors_viewed
            work.append(w)

        return GetPendingWorkResponseSchema().jsonify({
            'work': work,
            'total_count': pending_work.total,
            'page': page
        })


class CompletedWork(MethodView):
    @admin_jwt_required
    @parser.use_args(GetStatsRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, page, results_per_page, filter_list=None):
        current_app.logger.info('Fetching list of pending work items')

        filters = {}

        # built filters dict
        if filter_list:
            for f in filter_list:
                col, val = f.split('=')
                col = camel_case_to_snake_case(col)

                if col not in ('delegator_id', ):
                    current_app.logger.error(f'completed work stats endpoint got bad filter column: {col}')
                    abort(400, code='invalid_filter_field')

                filters[col] = val

        # subquery to count and sum duration of work records
        work_record_stats = WorkRecord.query \
            .with_entities(WorkRecord.work_id) \
            .add_columns(
                label('work_records_count', db.func.count()),
                label(
                    'work_records_total_duration_seconds',
                    db.func.sum(WorkRecord.duration_seconds)
                ),
                label(
                    'work_records_contributors_viewed',
                    db.func.count(db.distinct(WorkRecord.user_id))
                )
            ) \
            .group_by(WorkRecord.work_id) \
            .subquery()
        
        # subquery to get worker ids for completed work
        latest_work_records = WorkRecord.query \
            .with_entities(WorkRecord.work_id) \
            .add_columns(
                label('last_record', db.func.max(WorkRecord.id))
            ) \
            .group_by(WorkRecord.work_id) \
            .subquery()
        completed_work_worker_ids = WorkRecord.query \
            .join(latest_work_records, WorkRecord.id == latest_work_records.c.last_record) \
            .add_columns(
                label('worker_id', WorkRecord.user_id),
                label('worker_name', WorkRecord.user_name)
            ) \
            .subquery()

        # subquery to sum net duration and costs of work records
        upwork_diary_stats = WorkRecordUpworkDiary.query \
            .outerjoin(WorkRecord, WorkRecord.id == WorkRecordUpworkDiary.work_record_id) \
            .outerjoin(UpworkDiary, UpworkDiary.id == WorkRecordUpworkDiary.upwork_diary_id) \
            .with_entities(
                WorkRecord.work_id, 
                db.func.group_concat(
                    UpworkDiary.duration_string.op('separator')(db.text('"\n"'))
                ).label('work_records_exact_upwork_durations'),
                db.func.group_concat(
                    UpworkDiary.upwork_duration_string.op('separator')(db.text('"\n"'))
                ).label('work_records_rounded_upwork_durations')
            ) \
            .add_columns(
                label(
                    'work_records_net_duration_seconds',
                    db.func.sum(WorkRecordUpworkDiary.net_duration_seconds)
                ),                
                label(
                    'work_records_cost',
                    db.func.sum(WorkRecordUpworkDiary.cost)
                ),
                label(
                    'work_records_upwork_duration_seconds',
                    db.func.sum(WorkRecordUpworkDiary.upwork_duration_seconds)
                ),                
                label(
                    'work_records_upwork_cost',
                    db.func.sum(WorkRecordUpworkDiary.upwork_cost)
                )
            ) \
            .group_by(WorkRecord.work_id) \
            .subquery()

        # query for completed work items
        completed_work_query = Work.query \
            .outerjoin(work_record_stats, Work.id == work_record_stats.c.work_id) \
            .outerjoin(completed_work_worker_ids, Work.id == completed_work_worker_ids.c.work_id) \
            .outerjoin(upwork_diary_stats, Work.id == upwork_diary_stats.c.work_id) \
            .add_columns(
                work_record_stats.c.work_records_count, 
                work_record_stats.c.work_records_total_duration_seconds, 
                work_record_stats.c.work_records_contributors_viewed,
                completed_work_worker_ids.c.worker_id, 
                completed_work_worker_ids.c.worker_name, 
                upwork_diary_stats.c.work_records_net_duration_seconds, 
                upwork_diary_stats.c.work_records_cost, 
                upwork_diary_stats.c.work_records_upwork_duration_seconds, 
                upwork_diary_stats.c.work_records_upwork_cost,
                upwork_diary_stats.c.work_records_exact_upwork_durations,
                upwork_diary_stats.c.work_records_rounded_upwork_durations) \
            .options(joinedload(Work.task)) \
            .filter(Work.task_id == Task.id) \
            .filter(Work.status == WorkStatus.COMPLETE)

        if 'delegator_id' in filters:
            completed_work_query = completed_work_query \
                .filter(Task.delegating_user_id == filters['delegator_id'])

        completed_work = completed_work_query \
            .order_by(Work.id.desc()) \
            .paginate(page=page, per_page=results_per_page, error_out=False)
        
        # attach work records stats and worker id to each work item
        work = []
        for item in completed_work.items:
            w = item[0]
            w.work_records_count = item.work_records_count
            w.work_records_total_duration_seconds = item.work_records_total_duration_seconds
            w.work_records_contributors_viewed = item.work_records_contributors_viewed
            w.worker_id = item.worker_id
            w.worker_name = item.worker_name
            w.work_records_net_duration_seconds = item.work_records_net_duration_seconds
            w.work_records_cost = item.work_records_cost
            w.work_records_upwork_duration_seconds = item.work_records_upwork_duration_seconds
            w.work_records_upwork_cost = item.work_records_upwork_cost
            w.work_records_exact_upwork_durations = item.work_records_exact_upwork_durations
            w.work_records_rounded_upwork_durations = item.work_records_rounded_upwork_durations

            work.append(w)

        return GetCompletedWorkResponseSchema().jsonify({
            'work': work,
            'total_count': completed_work.total,
            'page': page
        })


class InvalidTasks(MethodView):
    @admin_jwt_required
    @parser.use_args(GetStatsRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, page, results_per_page):
        current_app.logger.info('Fetching list of invalid tasks')

        invalid_task_records = Task.query \
            .filter(Task.status.in_((TaskStatus.INVALID, TaskStatus.PENDING_CLASS_PARAMS, TaskStatus.PENDING_PACKAGE, TaskStatus.CANCELLED))) \
            .filter(Task.feedback is not None) \
            .order_by(Task.updated.desc()) \
            .paginate(page=page, per_page=results_per_page, error_out=False)

        return GetInvalidTasksResponseSchema().jsonify({
            'tasks': invalid_task_records.items,
            'total_count': invalid_task_records.total,
            'page': page
        })


class ActiveUsers(MethodView):
    @admin_jwt_required
    @parser.use_args(GetStatsRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, page, results_per_page):     
        current_app.logger.info('Fetching list of active users')

        users = User.query.filter_by(activated=True) \
            .order_by(User.email.desc()) \
            .paginate(page=page, per_page=results_per_page, error_out=False)

        user_records = []
        for user in users.items:
            user_records.append({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'github_user': user.github_user,
                'trello_user': user.trello_user,
                'upwork_user': user.upwork_user,
                'admin': user.admin,
                'availability_weekly_hours': user.availability_weekly_hours,
                'price_per_hour': user.price_per_hour,
                'tags': user.tags,
                'skills': user.skills
            })

        return GetUsersResponseSchema().jsonify({
            'users': user_records,
            'total_count': users.total,
            'page': page
        })


class Honeycombs(MethodView):
    @admin_jwt_required
    @parser.use_args(GetStatsRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, page, results_per_page):
        current_app.logger.info('Fetching list of honeycombs')

        honeycomb_records = Honeycomb.query \
            .options(
                joinedload(Honeycomb.honeycomb_dependencies)
            ) \
            .order_by(Honeycomb.id.desc()) \
            .paginate(page=page, per_page=results_per_page, error_out=False)

        # attach honeycomb dependecy stats to each honeycomb
        honeycombs = []
        for honeycomb in honeycomb_records.items:
            honeycomb_dependencies = honeycomb.get_dependencies(
                recursive=False
            )
            honeycomb.honeycomb_dependency_names = [
                dependency.name for dependency in honeycomb_dependencies
            ]
            honeycombs.append(honeycomb)

        return GetHoneycombsResponseSchema().jsonify({
            'honeycombs': honeycombs,
            'total_count': honeycomb_records.total,
            'page': page
        })


# these two next views should actually exist in `backoffice.py` once we refractor it to include dashboard actions
# currently put in stats as it is admin authenticated (unlike backoffice views that require the inner services header)
class WorkReservation(MethodView):
    @admin_jwt_required
    @parser.use_args(ReserveWorkRequestSchema(), as_kwargs=True)
    def post(self, work_id, user_id, hours_reserved=72):
        work = Work.query.filter_by(id=work_id) \
            .options( \
                joinedload(Work.task)
            ) \
            .first()
        if not work:
            current_app.logger.error(f'work {work_id} is not found')
            abort(404)

        user = User.query.filter_by(id=user_id).first()
        if not user:
            current_app.logger.error(f'user {user_id} is not found')
            abort(404)

        if work.reserved_worker_id:
            current_app.logger.error(f'work {work_id} is already resolved for user {work.reserved_worker_id} \
                until {time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(work.reserved_until_epoch_ms / 1000.0))}')
            abort(400, code='work_already_reserved')

        # reserve work for the worker for amount of days specified in request
        work.reserved_worker_id = user_id
        work.reserved_until_epoch_ms = int(time.time() * 1000) + hours_reserved * 60 * 60 * 1000

        db.session.commit()

        if work.task.task_type in (TaskType.CUCKOO_CODING, ):
            current_app.logger.info('notifying cuckoo service about reserved work')
            
            res = dispatch_cuckoo_event(
                work.task.id, 
                {
                    'eventType': CuckooEvent.WORK_RESERVED.name,
                    'reservedUntil': time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(work.reserved_until_epoch_ms / 1000.0)),
                    'user': user_id
                }
            )
            if not res:
                current_app.logger.error(f'error while notifying cuckoo about reserved work {work_id} for user {user_id}')

        return ReserveWorkResponseSchema().jsonify(work)

    @admin_jwt_required
    def delete(self, work_id, user_id):
        work = Work.query \
            .filter(Work.reserved_worker_id == user_id) \
            .filter(Work.reserved_until_epoch_ms >= int(time.time() * 1000)) \
            .filter(Work.status == WorkStatus.AVAILABLE) \
            .join(Task, and_(
                Work.task_id == Task.id,
                Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROCESS, TaskStatus.MODIFICATIONS_REQUESTED]))
            ) \
            .first()
        if not work:
            current_app.logger.error(f'work {work_id} is not found')
            abort(404)
        
        if work.reserved_worker_id != user_id:
            current_app.logger.error(f'work {work_id} is not reserved for this user {work.reserved_worker_id}')
            abort(400, code='work_not_reserved')

        work.reserved_worker_id = None
        work.reserved_until_epoch_ms = None

        db.session.commit()

        if work.task.task_type in (TaskType.CUCKOO_CODING, ):
            current_app.logger.info('notifying cuckoo service about dismissed work')
            
            res = dispatch_cuckoo_event(
                work.task.id, 
                {
                    'eventType': CuckooEvent.WORK_DISMISSED.name,
                    'user': user_id
                }
            )
            if not res:
                current_app.logger.error(f'error while notifying cuckoo about dismissed work {work_id} from user {user_id}')

        return ReserveWorkResponseSchema().jsonify(work)

class Contributors(MethodView):
    @admin_jwt_required
    @parser.use_args(GetContributorsRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, page, results_per_page, filter_list=None):
        current_app.logger.info('Fetching list of pending work items')

        users = User.query.filter_by(activated=True) \
            .order_by(User.utc_last_engagement.desc()) \
            .paginate(page=page, per_page=results_per_page, error_out=False)

        records = []
        for user in users.items:

            active_work = 'none'
            active_work_record = WorkRecord.query.filter_by(active=True) \
                .filter(WorkRecord.user_id == user.id) \
                .order_by(WorkRecord.id.desc()).first()

            if active_work_record != None:
                active_work = active_work_record.work_id

            number_of_reserved_works = Work.query \
                .with_entities(Work.task_id) \
                .filter(Work.reserved_worker_id == user.id) \
                .filter(Work.status == WorkStatus.AVAILABLE) \
                .join(Task, and_(
                    Work.task_id == Task.id,
                    Task.status.in_([TaskStatus.PENDING, TaskStatus.MODIFICATIONS_REQUESTED, TaskStatus.IN_PROCESS]))
                ).count()

            number_of_works_in_review = WorkRecord.query \
                .with_entities(WorkRecord.work_id) \
                .filter(WorkRecord.user_id == user.id) \
                .join(Work, Work.id == WorkRecord.work_id,) \
                .filter(Work.work_type.in_([WorkType.REVIEW_TASK, WorkType.CUCKOO_ITERATION])) \
                .with_entities(Work.task_id) \
                .join(Task, and_(
                    Work.task_id == Task.id,
                    Task.status.in_([TaskStatus.IN_PROCESS]))
                ).count()

            number_of_completed_works = WorkRecord.query \
                .with_entities(WorkRecord.work_id) \
                .filter(WorkRecord.user_id == user.id) \
                .join(Work, Work.id == WorkRecord.work_id,) \
                .filter(Work.status == WorkStatus.COMPLETE) \
                .count()

            number_of_total_works = WorkRecord.query \
                .with_entities(WorkRecord.work_id) \
                .join(Work, Work.id == WorkRecord.work_id,) \
                .filter(WorkRecord.user_id == user.id) \
                .count()
                

            # this is how we look at cancelled records currently
            number_of_cancelled_works = Work.query \
                .with_entities(Work.task_id) \
                .filter(Work.reserved_worker_id == user.id) \
                .join(Task, and_(
                    Work.task_id == Task.id,
                    Task.status.in_([TaskStatus.CANCELLED]))
                ).count()
            
            number_of_skipped_works = WorkRecord.query \
                .filter(and_(WorkRecord.user_id == user.id, WorkRecord.outcome == WorkOutcome.SKIPPED)) \
                .count()

            
            skipped_total_works_ratio = f"{(number_of_skipped_works / number_of_total_works):.2f}" if number_of_total_works > 0 else '-'
            
            time_since_last_engagement = 0
            last_engagement = WorkRecord.query \
                .filter(WorkRecord.user_id == user.id) \
                .order_by(WorkRecord.id.desc()).first()
            now_in_millisec = time.time() * 1000
            if last_engagement != None:
                time_since_last_engagement = (now_in_millisec - last_engagement.start_time_epoch_ms - (last_engagement.duration_seconds if (last_engagement.duration_seconds != None and last_engagement.duration_seconds < 999999999) else 0)*1000)
                time_since_last_engagement = time_since_last_engagement / 1000

            time_since_last_work = 0
            last_work_record = WorkRecord.query \
                .filter(WorkRecord.user_id == user.id) \
                .filter(or_(WorkRecord.outcome.notin_([WorkOutcome.SKIPPED]), WorkRecord.outcome.is_(None))) \
                .order_by(WorkRecord.id.desc()).first()

            work_record_stats = WorkRecord.query \
                .with_entities(WorkRecord.work_id) \
                .join(Work, WorkRecord.work_id == Work.id) \
                .filter(WorkRecord.user_id == user.id) \
                .filter(and_(WorkRecord.duration_seconds != None, WorkRecord.duration_seconds < 999999999)) \
                .add_columns(
                    label(
                        'work_records_total_duration_seconds',
                        db.func.sum(WorkRecord.duration_seconds)
                    )
                ) \
                .group_by(WorkRecord.work_id).all()

            work_record_upwork_diary_stats = WorkRecordUpworkDiary.query \
                .join(WorkRecord, WorkRecordUpworkDiary.work_record_id == WorkRecord.id) \
                .filter(WorkRecord.user_id == user.id) \
                .filter(WorkRecordUpworkDiary.net_duration_seconds != None) \
                .add_columns(
                    label(
                        'work_records_net_duration_seconds',
                        db.func.sum(WorkRecordUpworkDiary.net_duration_seconds)
                    ),
                    label(
                        'work_records_cost',
                        db.func.sum(WorkRecordUpworkDiary.cost)
                    )
                ) \
                .group_by(WorkRecordUpworkDiary.id, WorkRecord.work_id).all()

            average_work_price = None
            average_gross_work_duration_seconds = None
            average_net_work_duration_seconds = None
            if work_record_stats:
                average_gross_work_duration_seconds = sum(x.work_records_total_duration_seconds for x in work_record_stats) / len(work_record_stats)
            if work_record_upwork_diary_stats:
                average_net_work_duration_seconds = sum(x.work_records_net_duration_seconds or 0 for x in work_record_upwork_diary_stats) / len(work_record_upwork_diary_stats)
                average_work_price = sum(x.work_records_cost or 0 for x in work_record_upwork_diary_stats)  / len(work_record_upwork_diary_stats)

            if last_work_record != None:
                time_since_last_work = (now_in_millisec - last_work_record.start_time_epoch_ms - (last_work_record.duration_seconds if (last_work_record.duration_seconds != None and last_work_record.duration_seconds < 999999999) else 0)*1000)
                time_since_last_work = time_since_last_work / 1000

            first_work_record = WorkRecord.query \
                .filter(WorkRecord.user_id == user.id) \
                .order_by(WorkRecord.id.asc()).first()
            average_billable = 'none'
            billable_hours_availability_ratio = '0.00'
            if len(work_record_stats) > 0 and first_work_record != None and last_work_record != None:
                weeks = ((last_work_record.utc_end_time or last_work_record.utc_start_time) - first_work_record.utc_start_time).days / 7 
                average_billable_per_week = sum(x.work_records_net_duration_seconds or 0 for x in work_record_upwork_diary_stats) / max(decimal.Decimal(weeks), 1)
                average_billable_per_week_hours = average_billable_per_week / 60 / 60
                average_billable = f"{average_billable_per_week_hours:.2f}"
                if user.availability_weekly_hours:
                    billable_hours_availability_ratio = f"{(average_billable_per_week_hours / user.availability_weekly_hours * 100):.2f}"


            average_iterations_per_work = 0
            iterations = WorkRecord.query.with_entities(WorkRecord.work_id).filter(WorkRecord.user_id == user.id).add_columns(label('correspondences',db.func.count())).group_by(WorkRecord.work_id)
            average_iterations_per_work = WorkRecord.query.with_entities(label('avg', db.func.avg(iterations.subquery().columns.correspondences))).scalar()

            records.append({
                'id': user.id,
                'name': user.name,
                'active_work': active_work,
                'number_of_reserved_works': number_of_reserved_works,
                'number_of_works_in_review': number_of_works_in_review,
                'number_of_completed_works': number_of_completed_works,
                'number_of_total_works': number_of_total_works,
                'number_of_cancelled_works': number_of_cancelled_works,
                'number_of_skipped_works': number_of_skipped_works,
                'skipped_total_works_ratio': skipped_total_works_ratio,
                'time_since_last_engagement': time_since_last_engagement,
                'time_since_last_work': time_since_last_work,
                'billable_hours_availability_ratio': billable_hours_availability_ratio,
                'average_billable': average_billable,
                'weekly_availability': user.availability_weekly_hours,
                'average_gross_work_duration': average_gross_work_duration_seconds,
                'average_net_work_duration': average_net_work_duration_seconds,
                'average_work_price': average_work_price,
                'average_iterations_per_work': average_iterations_per_work,
                'hourly_rate': f"${user.price_per_hour}" if user.price_per_hour != None else 'none',
                  
            })


        return GetContributorsResponseSchema().jsonify({
            'data': records,
            'total_count': users.total,
            'page': page
        })
        
class WorkProhibition(MethodView):
    @admin_jwt_required
    def get(self, work_id, user_id):
        work = Work.query.filter_by(id=work_id) \
            .options( \
                joinedload(Work.task)
            ) \
            .first()
        if not work:
            current_app.logger.error(f'work {work_id} is not found')
            abort(404)

        user = User.query.filter_by(id=user_id).first()
        if not user:
            current_app.logger.error(f'user {user_id} is not found')
            abort(404)

        if work.prohibited_worker_id:
            current_app.logger.error(f'work {work_id} is already prohibited for user {work.prohibited_worker_id}')
            abort(400, code='work_already_prohibited')

        # prohibit work for this worker
        work.prohibited_worker_id = user_id
        db.session.commit()

        if work.task.task_type in (TaskType.CUCKOO_CODING, ):
            current_app.logger.info('notifying cuckoo service about prohibited work')
            
            res = dispatch_cuckoo_event(
                work.task.id, 
                {
                    'eventType': CuckooEvent.WORK_PROHIBITED.name,
                    'user': user_id
                }
            )
            if not res:
                current_app.logger.error(f'error while notifying cuckoo about prohibited work {work_id} for user {user_id}')

        return ProhibitWorkResponseSchema().jsonify(work)

    @admin_jwt_required
    def delete(self, work_id, user_id):
        work = Work.query \
            .filter(Work.prohibited_worker_id == user_id) \
            .filter(Work.status == WorkStatus.AVAILABLE) \
            .join(Task, and_(
                Work.task_id == Task.id,
                Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROCESS, TaskStatus.MODIFICATIONS_REQUESTED]))
            ) \
            .first()
        if not work:
            abort(404)
        
        if work.prohibited_worker_id != user_id:
            current_app.logger.error(f'work {work_id} is not currently prohibited for this user {work.prohibited_worker_id}')
            abort(400, code='work_not_reserved')

        work.prohibited_worker_id = None

        db.session.commit()

        if work.task.task_type in (TaskType.CUCKOO_CODING, ):
            current_app.logger.info('notifying cuckoo service about unprohibited work')
            
            res = dispatch_cuckoo_event(
                work.task.id, 
                {
                    'eventType': CuckooEvent.WORK_UNPROHIBITED.name,
                    'user': user_id
                }
            )
            if not res:
                current_app.logger.error(f'error while notifying cuckoo about unprohibited work {work_id} from user {user_id}')

        return ProhibitWorkResponseSchema().jsonify(work)

class ContributorHistory(MethodView):
    @admin_jwt_required
    @parser.use_args(GetStatsRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, user_id, page, results_per_page):
        """
        Get work record and history of an existing user
        """

        current_app.logger.info('Fetching contributor history')

        user = User.query.filter_by(id=user_id).first()
        if not user:
            abort(404)

        # subquery for this users iteration on task
        iterations_per_task = WorkRecord.query \
            .filter(WorkRecord.user_id == user.id) \
            .filter(or_(WorkRecord.outcome.notin_([WorkOutcome.SKIPPED, WorkOutcome.CANCELLED]), WorkRecord.outcome.is_(None))) \
            .join(WorkRecord.work) \
            .with_entities(Work.task_id) \
            .add_columns(
                label('iterations', db.func.count(WorkRecord.id))
            ) \
            .group_by(Work.task_id) \
            .subquery()

        user_work_records = WorkRecord.query \
            .filter_by(user_id=user_id) \
            .filter(or_(WorkRecord.outcome.notin_([WorkOutcome.SKIPPED, WorkOutcome.CANCELLED]), WorkRecord.outcome.is_(None))) \
            .join(Work, WorkRecord.work_id == Work.id) \
            .outerjoin(iterations_per_task, Work.task_id == iterations_per_task.c.task_id) \
            .add_columns(iterations_per_task.c.iterations) \
            .order_by(WorkRecord.id.desc()) \
            .paginate(page=page, per_page=results_per_page, error_out=False)

        # attach rating stats to each work item
        work = []
        for item in user_work_records.items:
            w = item[0]
            w.ratings = w.get_ratings()
            w.iterations_per_task = item[1]
            work.append(w)

        # compute averages
        ratings = [w.ratings for w in work if w is not None and w.ratings is not None]
        scores = [decimal.Decimal(r.get('score')) for wr in ratings for r in wr]
        avg_rating = mean(scores) if scores else -1
        iterations = [decimal.Decimal(w.iterations_per_task) for w in work]
        avg_iterations = mean(iterations) if iterations else -1

        for w in work:
            w.average_rating = 'Average rating for all work: %.2f' % avg_rating
            w.average_iterations_per_task = 'Average iterations for all tasks: %.2f' % avg_iterations

        return ContributorHistoryResponseSchema().jsonify({
            'work': work,
            'total_count': user_work_records.total,
            'page': page
        })
