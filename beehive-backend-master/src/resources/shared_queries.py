from datetime import date, timedelta, datetime, timezone
from operator import or_

from sqlalchemy import and_
from flask import current_app

from ..models.tag import TaskTag
from ..models.task import Task, TaskStatus
from ..models.work import Work, WorkStatus
from ..models.work_record import WorkOutcome, WorkRecord
from ..utils.db import db


def get_contributor_stats_specific_project(user, project_id):
    id = user.id
    last_work_record = WorkRecord.query \
        .join(WorkRecord.work) \
        .join(Work.task) \
        .filter(Task.tags.any(TaskTag.tag_id == project_id)) \
        .filter(WorkRecord.user_id == id) \
        .filter(or_(WorkRecord.outcome.notin_([WorkOutcome.SKIPPED]), WorkRecord.outcome.is_(None))) \
        .order_by(WorkRecord.id.desc()).first()
    last_work_record_ts = None if not last_work_record else last_work_record.utc_end_time if last_work_record.utc_end_time else last_work_record.utc_start_time

    last_engagement = WorkRecord.query \
        .join(WorkRecord.work) \
        .join(Work.task) \
        .filter(Task.tags.any(TaskTag.tag_id == project_id)) \
        .filter(WorkRecord.user_id == id) \
        .order_by(WorkRecord.id.desc()).first()
    last_engagement_ts = None if not last_engagement else last_engagement.utc_end_time if last_engagement.utc_end_time else last_engagement.utc_start_time

    reserved_works = Work.query \
        .join(Work.task) \
        .filter(Task.tags.any(TaskTag.tag_id == project_id)) \
        .filter(Work.reserved_worker_id == id) \
        .filter(Work.status == WorkStatus.AVAILABLE) \
        .count()
    
    works_in_review = db.session.query(Work) \
        .join(Work.task) \
        .filter(Task.tags.any(TaskTag.tag_id == project_id)) \
        .filter(Work.reserved_worker_id == id) \
        .filter(or_(Task.status == TaskStatus.SOLVED, Task.status == TaskStatus.INVALID)) \
        .filter(Task.created > current_app.config['CUCKOO_START_DATE']) \
        .count()

    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    last_active = last_engagement_ts and datetime.fromtimestamp(last_engagement_ts.timestamp(), timezone.utc)
    active = None if not last_engagement_ts or last_active < thirty_days_ago else False if last_active < seven_days_ago else True
    return {
        'name': user.name,
        'country': '',
        'active': active,
        'last_work': last_work_record_ts,
        'last_engagement': last_engagement_ts,
        'reserved_works': reserved_works,
        'works_in_review': works_in_review,
        'hourly_rate': user.price_per_hour,
        'skills': [s.name for s in user.skills],
        'projects': [],
    }

def get_contributor_stats(user):
    id = user.id
    last_work_record = WorkRecord.query \
        .filter(WorkRecord.user_id == id) \
        .filter(or_(WorkRecord.outcome.notin_([WorkOutcome.SKIPPED]), WorkRecord.outcome.is_(None))) \
        .order_by(WorkRecord.id.desc()).first()
    last_work_record_ts = None if not last_work_record else last_work_record.utc_end_time if last_work_record.utc_end_time else last_work_record.utc_start_time

    last_engagement = WorkRecord.query \
        .filter(WorkRecord.user_id == id) \
        .order_by(WorkRecord.id.desc()).first()
    last_engagement_ts = None if not last_engagement else last_engagement.utc_end_time if last_engagement.utc_end_time else last_engagement.utc_start_time

    reserved_works = Work.query \
        .filter(Work.reserved_worker_id == id) \
        .filter(Work.status == WorkStatus.AVAILABLE) \
        .count()
    
    works_in_review = db.session.query(Work) \
        .join(Work.task) \
        .filter(Work.reserved_worker_id == id) \
        .filter(or_(Task.status == TaskStatus.SOLVED, Task.status == TaskStatus.INVALID)) \
        .filter(Task.created > current_app.config['CUCKOO_START_DATE']) \
        .count()

    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    last_active = last_engagement_ts and datetime.fromtimestamp(last_engagement_ts.timestamp(), timezone.utc)
    active = None if not last_engagement_ts or last_active < thirty_days_ago else False if last_active < seven_days_ago else True
    return {
        'name': user.name,
        'country': '',
        'active': active,
        'last_work': last_work_record_ts,
        'last_engagement': last_engagement_ts,
        'reserved_works': reserved_works,
        'works_in_review': works_in_review,
        'hourly_rate': user.price_per_hour,
        'skills': [s.name for s in user.skills],
        'projects': [],
    }
