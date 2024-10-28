import time

from flask import current_app
from sqlalchemy.orm import joinedload


from ..logic.cuckoo import CuckooEvent, dispatch_cuckoo_event
from ..models.user import User
from ..models.task import Task, TaskStatus, TaskType
from ..models.work import Work, WorkStatus
from ..models.work_record import WorkRecord
from ..utils.db import db
from ..utils.metrics import find_deserted_work_exception, find_past_reserved_work_exception, find_pre_deserted_work_exception
from ..utils.rq import rq
from ..utils.email import send_contributor_work_deserted_email, send_work_deserted_email, send_contributor_work_pre_deserted_email


# NOTE: when scheduled using the `cron` function result_ttl is overridden with
# -1, so results are never removed from redis. this is rq's method of handling
# long-queued jobs - https://github.com/rq/rq-scheduler/blob/c79288c1046e5e4e79a46cba2bb6dc035250ff84/rq_scheduler/scheduler.py#L258
@rq.job('low', timeout=900, result_ttl=3600)
@find_deserted_work_exception.count_exceptions()
def find_deserted_work():
    now_epoch_ms = int(time.time() * 1000)

    # min start time is 10 hours ago
    min_start_time_epoch_ms = now_epoch_ms - 10 * 60 * 60 * 1000

    # find all deserted work
    deserted_work = WorkRecord.query \
        .filter_by(active=True) \
        .filter(WorkRecord.start_time_epoch_ms < min_start_time_epoch_ms) \
        .options(joinedload(WorkRecord.work).joinedload(Work.task)) \
        .filter(Task.status == TaskStatus.IN_PROCESS) \
        .all()

    for deserted in deserted_work:
        deserted_seconds = (now_epoch_ms - deserted.start_time_epoch_ms) / 1000
        current_app.logger.info(f'found work {deserted.work.id} deserted by user {deserted.user_id} for {deserted_seconds / 60 / 60} hours')

        # cancel work and task
        deserted.active = False
        deserted.duration_seconds = deserted_seconds
        deserted.work.status = WorkStatus.AVAILABLE

        # if the task has no completed work set its status back to pending
        task_completed_work = Work.query \
            .filter_by(task_id=deserted.work.task_id, status=WorkStatus.COMPLETE) \
            .all()
        if not task_completed_work:
            deserted.work.task.status = TaskStatus.PENDING

        success = True
        contributor = deserted.user

        if deserted.work.task.task_type in (TaskType.CUCKOO_CODING, ):
            current_app.logger.info('notifying cuckoo service about deserted work')
            
            github_user = contributor.github_user

            res = dispatch_cuckoo_event(
                deserted.work.task.id, 
                {
                    'eventType': CuckooEvent.WORK_DESERTED.name,
                    'workDurationMinutes': deserted_seconds / 60,
                    'user': deserted.user_id,
                    'githubUser': github_user
                }
            )
            if not res:
                success = False
                db.session.rollback()
                current_app.logger.error(f'error while notifying cuckoo about deserted work {deserted.work.id} deserted by user {deserted.user_id}')

        if success:
            send_work_deserted_email(deserted.work.task.delegating_user_id, deserted)
            send_contributor_work_deserted_email(contributor, deserted.work)

            db.session.commit()


@rq.job('low', timeout=900, result_ttl=3600)
@find_pre_deserted_work_exception.count_exceptions()
def find_pre_deserted_work():
    now_epoch_ms = int(time.time() * 1000)

    # min start time is 10-8 hours ago
    min_start_time_epoch_ms = now_epoch_ms - 8 * 60 * 60 * 1000

    # find all works that will be deserted in 2 hours
    pre_deserted_work = WorkRecord.query \
        .filter_by(active=True) \
        .filter(WorkRecord.start_time_epoch_ms < min_start_time_epoch_ms) \
        .options(joinedload(WorkRecord.work).joinedload(Work.task)) \
        .filter(Task.status == TaskStatus.IN_PROCESS) \
        .all()

    for pre_deserted in pre_deserted_work:
        send_contributor_work_pre_deserted_email(pre_deserted.user, pre_deserted.work)



@rq.job('low', timeout=900, result_ttl=3600)
@find_past_reserved_work_exception.count_exceptions()
def find_past_reserved_work():
    now_epoch_ms = int(time.time() * 1000)

    # find all reserved work that should be released back to queue
    past_reserveded_work = Work.query \
        .filter(Work.status == WorkStatus.AVAILABLE) \
        .filter(Work.reserved_worker_id != None) \
        .filter(Work.reserved_until_epoch_ms < now_epoch_ms) \
        .options(joinedload(Work.task)) \
        .filter(Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROCESS, TaskStatus.MODIFICATIONS_REQUESTED])) \
        .all()

    for past_reserved in past_reserveded_work:
        past_reservation_minutes = (now_epoch_ms - past_reserved.reserved_until_epoch_ms) / 1000 / 60
        current_app.logger.info(f'found work {past_reserved.id} reserved to user {past_reserved.reserved_worker_id} overdue {past_reservation_minutes} minutes')

        # cancel reservation
        past_reserved.reserved_worker_id = None
        past_reserved.reserved_until_epoch_ms = None

        if past_reserved.task.task_type in (TaskType.CUCKOO_CODING, ):
            current_app.logger.info('notifying cuckoo service about dismissed work')
            
            res = dispatch_cuckoo_event(
                past_reserved.task.id, 
                {
                    'eventType': CuckooEvent.WORK_DISMISSED.name,
                    'user': past_reserved.reserved_worker_id
                }
            )
            if not res:
                current_app.logger.error(f'error while notifying cuckoo about dismissed work {past_reserved.id} from user {past_reserved.reserved_worker_id}')

        db.session.commit()