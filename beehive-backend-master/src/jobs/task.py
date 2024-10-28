from flask import current_app

from ..logic.work_mappers.code_qa import CodeQAMapper
from ..logic.pollinator import get_task_type_classification
from ..models.task import Task, TaskStatus, TaskType
from ..models.work import Work, WorkStatus
from ..utils.db import db
from ..utils.metrics import (
    task_prepare_cuckoo_duration,
    task_prepare_cuckoo_exception,
    task_prepare_cuckoo_success
)
from ..utils.rq import rq


@rq.job('high', timeout=900, result_ttl=3600)
@task_prepare_cuckoo_exception.count_exceptions()
@task_prepare_cuckoo_duration.time()
def prepare_cuckoo_task(task_id):
    current_app.logger.info(f'preparing cuckoo task {task_id}')

    # find task
    task = Task.query.filter_by(id=task_id, status=TaskStatus.NEW).first()
    if not task:
        raise Exception('task not found')

    # task is ready to be worked on
    task.status = TaskStatus.PENDING

    chain = []
    if task.advanced_options and task.advanced_options.get('chainReview', False):
        chain = [
            CodeQAMapper(
                chain_work_description=task.advanced_options.get('chainDescription'),
                remaining_chain_count=task.advanced_options.get('maxChainIterations')
            )
        ]

    work = Work.from_cuckoo(
        task.id,
        WorkStatus.AVAILABLE,
        task.task_type,
        task.description,
        priority=task.priority,
        tags=task.tags,
        skills=task.skills,
        chain=chain
    )
    db.session.add(work)

    # get task type classification label (exclude follow up tasks)
    if task.task_type == TaskType.CUCKOO_CODING:
        try:
            get_task_type_classification(task.id, task.description, task.skills)
        except Exception as e:
            current_app.logger.error(f'error while trying to get task type classification: {str(e)}')


    db.session.commit()

    # increase task prepare cuckoo success counter
    task_prepare_cuckoo_success.inc()
