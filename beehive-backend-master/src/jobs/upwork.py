from flask import current_app
from datetime import datetime, timedelta
from sqlalchemy.sql import label

from ..utils.db import db
from ..utils.metrics import find_net_duration_work_records_exception, find_net_duration_work_records_success, find_net_duration_work_records_duration, find_net_duration_cuckoo_accepted_tasks_exception, find_net_duration_cuckoo_accepted_tasks_success, find_net_duration_cuckoo_accepted_tasks_duration
from ..utils.rq import rq
from ..utils.upwork import save_upwork_diaries, update_work_records_net_duration

from ..models.work import Work
from ..models.task import Task, TaskStatus, TaskType
from ..models.work_record import WorkRecord
from ..models.upwork import WorkRecordUpworkDiary

from ..logic.cuckoo import CuckooEvent, dispatch_cuckoo_event

@rq.job('low', timeout=900, result_ttl=3600)
@find_net_duration_work_records_exception.count_exceptions()
@find_net_duration_work_records_duration.time()
def find_net_duration_work_records():

    ## iterate over last week because some upwork users update their time manually once a week 
    for i in range(1,8):
        # process one days upwork diaries
        # if a row already exists it updates it only if the end timestamp has changed
        day = (datetime.utcnow() - timedelta(i))
        day_upwork_records = save_upwork_diaries(day)
        if day_upwork_records:
            update_work_records_net_duration(day_upwork_records)

    # increase get daily upwork diary success counter
    find_net_duration_work_records_success.inc()


@rq.job('low', timeout=900, result_ttl=3600)
@find_net_duration_cuckoo_accepted_tasks_exception.count_exceptions()
@find_net_duration_cuckoo_accepted_tasks_duration.time()
def find_net_duration_cuckoo_accepted_tasks():
    # fetch tasks that were completed before the last 24 hours and in the current week
    yesterday = (datetime.utcnow() - timedelta(days=1)).date()
    last_week = datetime.utcnow() - timedelta(days=7)
    completed_cuckoo_tasks = Task.query \
        .filter(
            Task.status == TaskStatus.ACCEPTED,
            Task.task_type.in_([TaskType.CUCKOO_CODING]),
            db.func.date(Task.updated).between(last_week, yesterday),
            Task.total_net_duration_seconds.is_(None)
        ) \
        .subquery()

    work_record_upwork_diaries = WorkRecordUpworkDiary.query \
        .join(WorkRecord, WorkRecordUpworkDiary.work_record_id == WorkRecord.id) \
        .join(Work, WorkRecord.work_id == Work.id) \
        .join(completed_cuckoo_tasks, Work.task_id == completed_cuckoo_tasks.c.id) \
        .with_entities(Work.task_id) \
        .add_columns(
            label(
                'work_records_upwork_duration_seconds',
                db.func.sum(WorkRecordUpworkDiary.upwork_duration_seconds)
            )
        ) \
        .group_by(Work.task_id) \
        .all()

    current_app.logger.info(f'found {len(work_record_upwork_diaries)} tasks to update cuckoo net time')

    for item in work_record_upwork_diaries:
        task_id = item[0]
        work_records_upwork_duration_seconds = item[1]
        if work_records_upwork_duration_seconds:
            res = dispatch_cuckoo_event(
                task_id,
                {
                    'eventType': CuckooEvent.NET_DURATION_UPDATED.name,
                    'netDurationSeconds': str(work_records_upwork_duration_seconds),
                }
            )
            if not res:
                current_app.logger.error(f'error while notifying cuckoo about task {task_id} net duration {work_records_upwork_duration_seconds}')

        task = Task.query.filter_by(id=task_id).first()
        task.total_net_duration_seconds = work_records_upwork_duration_seconds
        db.session.commit()

    # increase update cuckoo net duration completed tasks success counter
    find_net_duration_cuckoo_accepted_tasks_success.inc()
