import time

from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import and_, or_



from ..jobs.task import prepare_cuckoo_task
from ..logic.work_mappers import code_qa
from ..models.task import Task, TaskStatus, TaskType
from ..models.user import User
from ..models.work import Work, WorkStatus, WorkType
from ..models.work_record import WorkRecord, WorkOutcome
from ..models.repository import Repository
from ..models.tag import Tag
from ..models.skill import Skill
from ..schemas import EmptyResponseSchema
from ..schemas.task import (
    CreateCuckooTaskRequestSchema,
    PartialUpdateCuckooTaskRequestSchema,
    TaskResponseSchema,
    NotifyContributorsRequestSchema
)

from ..utils.auth import activated_jwt_required, admin_jwt_required, inner_auth
from ..utils.db import db
from ..utils.email import send_contributor_task_modifications_email, send_contributors_notification_email, send_contributor_task_cancelled_email, send_contributors_task_update_email
from ..utils.errors import abort
from ..utils.marshmallow import parser
from ..utils.slack_bot import notify_new_task_description


class TaskCRUD(MethodView):
    # get all delegator's tasks
    @activated_jwt_required
    def get(self, task_id):
        user_id = get_jwt_identity()

        current_app.logger.info(f'Getting tasks for user {user_id}')

        tasks = Task.query.filter(
            Task.delegating_user_id == user_id
        )

        if task_id:
            tasks = tasks.filter_by(id=task_id)
            task = tasks.first()

            # abort with status 404 if specific task was requested and it doesn't exist
            if not task:
                abort(404)

            return TaskResponseSchema().jsonify(task)
        else:
            return TaskResponseSchema(many=True).jsonify(tasks.all())

    # deletes task
    @activated_jwt_required
    def delete(self, task_id):
        user_id = get_jwt_identity()

        task = Task.query.filter_by(id=task_id, delegating_user_id=user_id).first()
        if not task:
            abort(404)

        db.session.delete(task)
        db.session.commit()

        current_app.logger.info(f'Deleted task ID {task_id}\n')

        return EmptyResponseSchema().jsonify()


class CuckooTaskCRUD(MethodView):
    # create (delegate) new task from cuckoo service
    @inner_auth
    @parser.use_args(CreateCuckooTaskRequestSchema(), as_kwargs=True)
    def post(self, description, user_name, title=None, priority=2, tags=None, skills=None, repository_name=None, feature=None, chain_review=False, max_chain_iterations=None, chain_description=None, quest_id=None):
        user = User.query.filter_by(trello_user=user_name).first()
        if not user:
            abort(404)

        current_app.logger.info(f'Delegating cuckoo task {description}')

        advanced_options = {}
        if chain_review:
            advanced_options['chainReview'] = chain_review
            advanced_options['maxChainIterations'] = max_chain_iterations or code_qa.DEFAULT_QA_ITERATIONS
            advanced_options['chainDescription'] = chain_description or code_qa.DEFAULT_QA_DESCRIPTION_PREFIX
        if feature:
            advanced_options['feature'] = feature

        # get repoid and add to task
        repo = Repository.query.filter_by(name=repository_name).first()
        repo_id = None
        if repo:
            repo_id = repo.id

        # Create the task and get a task ID
        task = Task.from_cuckoo(
            delegating_user_id=user.id,
            description=description,
            title=title,
            status=TaskStatus.NEW,
            task_type=TaskType.CUCKOO_CODING,
            priority=priority,
            tags=[Tag.get_or_create(t) for t in tags or []],
            skills=[Skill.get_or_create(s) for s in skills or []],
            advanced_options=advanced_options,
            repository_id=repo_id,
            quest_id=quest_id
        )
        db.session.add(task)

        db.session.commit()

        # schedule job to prepare the work item
        prepare_cuckoo_task.queue(
            task.id
        )

        # notify new description
        notify_new_task_description(task)

        return TaskResponseSchema().jsonify(task)

    # partial-update a task
    @inner_auth
    @parser.use_args(PartialUpdateCuckooTaskRequestSchema(), as_kwargs=True)
    def put(
        self, task_id, user_name,
        description=None, status=None, tags=None, skills=None, repository_name=None, quest_id=None
    ):

        task = Task.query.filter_by(id=task_id).first()
        if not task:
            current_app.logger.error(f'task {task_id} is not found')
            abort(404)

        # do not allow updating tasks which are in process (except for cancelling a task)
        if task.status == TaskStatus.IN_PROCESS and status != TaskStatus.CANCELLED:
            abort(400, code='task_in_process')

        if description or (description == ''):
            current_app.logger.info(f'Updating description for {task_id} to be {description}')

            # set task work items description to the new value
            for work in task.works:
                if work.description == task.description:
                    work.description = description

            task.description = description

            # notify new task description
            notify_new_task_description(task)

            # email relevant contributors with the description update
            work_record_last_feedback = db.session.query(WorkRecord) \
                .join(WorkRecord.work) \
                .join(Work.task) \
                .filter(WorkRecord.outcome == WorkOutcome.FEEDBACK, Task.id == task_id) \
                .order_by(WorkRecord.id.desc()) \
                .first()
            
            available_work_for_task = Work.query \
                .filter(Work.task_id == task_id, Work.status == WorkStatus.AVAILABLE) \
                .order_by(Work.id.desc()) \
                .first()

            if work_record_last_feedback and available_work_for_task:
                send_contributors_task_update_email(work_record_last_feedback.user_id, available_work_for_task)

        if tags:
            task.tags = [Tag.get_or_create(t) for t in tags]
            for work in task.works:
                work.tags = task.tags

        if skills:
            task.skills = [Skill.get_or_create(s) for s in skills]
            for work in task.works:
                work.skills = task.skills

        if repository_name:
            repo = Repository.query.filter_by(name=repository_name).first()
            if repo:
                task.repository_id = repo.id            

        if quest_id == '':
            task.quest_id = None

        if status:
            current_app.logger.info(f'Updating task status {task_id} to {status}')

            if status == TaskStatus.MODIFICATIONS_REQUESTED:

                # get latest work record
                latest_work_record = db.session.query(WorkRecord) \
                    .join(WorkRecord.work) \
                    .join(Work.task) \
                    .filter(Task.id == task_id) \
                    .filter(or_(WorkRecord.outcome.notin_([WorkOutcome.SKIPPED]), WorkRecord.outcome.is_(None))) \
                    .order_by(WorkRecord.id.desc()) \
                    .first()

                if not latest_work_record:
                    current_app.logger.error(f'failed to query latest work record for task {task_id}')
                    abort(404)
    
                # update latest review total duration
                if not latest_work_record.review_start_time_epoch_ms:
                    current_app.logger.error(f'cannot update review duration for work record {latest_work_record.id} with no start time')
                    # NOTE: temporary comment to not abort flow for tasks that do not have start time (e.g before deploy) 
                    # abort(422, code='not_reviewed', description=f'cannot update review duration for work record {latest_work_record.id} with no start time')
                else:
                    now_epoch_ms = int(time.time() * 1000)
                    latest_work_record.review_duration_seconds = (now_epoch_ms - latest_work_record.review_start_time_epoch_ms) / 1000
                    db.session.add(latest_work_record)

                # if task was solved create a new cuckoo task reserved to contributor
                if ((latest_work_record.solution_url or (latest_work_record.work.work_input and latest_work_record.work.work_input['solution_url'])) and
                        (latest_work_record.work.task.status in [TaskStatus.SOLVED, TaskStatus.ACCEPTED])):

                    # if latest work record solved was not rated - abort
                    latest_work_record_ratings = latest_work_record.get_ratings()
                    if not latest_work_record_ratings:
                        current_app.logger.error(f'cannot set task status {status} to unrated work record {latest_work_record.id}')
                        abort(422, code='not_rated', description=f'work record {latest_work_record.id} not rated')

                    subsequent_work_type = WorkType.CUCKOO_ITERATION
                    solution_url = latest_work_record.solution_url or latest_work_record.work.work_input['solution_url']
                    subsequent_work_input = {'solution_url': solution_url}
                    subsequent_description = f'Please change code according to PR review: \
                        [{solution_url}]({solution_url}) \
                            \nWhen done submit the same PR url again. \
                            \n\n ## Original task:\n{task.description}'
                    
                    if latest_work_record.work.work_type == WorkType.CUCKOO_QA and 'user_id' in latest_work_record.work.work_input:
                        subsequent_reserved_worker_id = latest_work_record.work.work_input['user_id']
                    else:
                        subsequent_reserved_worker_id = latest_work_record.user_id
                
                # if task got feedback create a normal cuckoo task reserved to contributor
                elif latest_work_record.feedback and latest_work_record.work.task.status == TaskStatus.INVALID:
                    subsequent_work_type = WorkType.CUCKOO_CODING
                    subsequent_description = description
                    subsequent_reserved_worker_id = latest_work_record.user_id
                    subsequent_work_input = latest_work_record.work.work_input

                else:
                    current_app.logger.error(f'inconsistent state of modifications requested for task {task_id} of status {latest_work_record.work.task.status}')
                    abort(404)

                chain = []
                if task.advanced_options and task.advanced_options.get('chainReview', False):
                    chain = [
                        code_qa.CodeQAMapper(
                            chain_work_description=task.advanced_options.get('chainDescription'),
                            remaining_chain_count=task.advanced_options.get('maxChainIterations')
                        )
                    ]

                # create new iteration coding task reserved to this contributor for 4 hours
                subsequent_work = Work.from_cuckoo(
                    task_id,
                    WorkStatus.AVAILABLE,
                    subsequent_work_type,
                    subsequent_description,
                    tags=task.tags,
                    skills=task.skills,
                    chain=chain,
                    work_input=subsequent_work_input
                )
                # reserve for worker that solved the coding work for 4 hours
                subsequent_work.reserved_worker_id = subsequent_reserved_worker_id
                subsequent_work.reserved_until_epoch_ms = int(time.time() * 1000) + 4 * 60 * 60 * 1000
                db.session.add(subsequent_work)
                
                db.session.commit() # for updating work relationships
                send_contributor_task_modifications_email(subsequent_work.reserved_worker_id, subsequent_work)
                    
            elif status == TaskStatus.CANCELLED:

                # if the task is currently in progress, mark it as inactive and send an email to contributor
                if task.status == TaskStatus.IN_PROCESS:
                    # get latest work record
                    latest_work_record = db.session.query(WorkRecord) \
                        .join(WorkRecord.work) \
                        .join(Work.task) \
                        .filter(Task.id == task_id, WorkRecord.active == True) \
                        .order_by(WorkRecord.id.desc()) \
                        .first()

                    # maybe chain is in process but no work record is being actively worked on
                    if latest_work_record:
                        latest_work_record.active = False
                        now_epoch_ms = int(time.time() * 1000)
                        latest_work_record.duration_seconds = (now_epoch_ms - latest_work_record.start_time_epoch_ms) / 1000
                        latest_work_record.outcome = WorkOutcome.TASK_CANCELLED
                        send_contributor_task_cancelled_email(latest_work_record.user_id, task)

                for work in task.works:
                    if work.status == WorkStatus.AVAILABLE:
                        work.status = WorkStatus.UNAVAILABLE

            elif status == TaskStatus.ACCEPTED:

                # if the task has work records that have been solved but not rated - abort
                solved_coding_work_records = db.session.query(WorkRecord) \
                    .join(WorkRecord.work) \
                    .join(Work.task) \
                    .filter( \
                        Task.id == task_id, \
                        WorkRecord.outcome == WorkOutcome.SOLVED, \
                        Work.work_type.in_([WorkType.CUCKOO_CODING, WorkType.CUCKOO_ITERATION]) \
                    ) \
                    .order_by(WorkRecord.id.desc()) \
                    .all()
                
                latest_qa_work_record = db.session.query(WorkRecord) \
                    .join(WorkRecord.work) \
                    .join(Work.task) \
                    .filter( \
                        Task.id == task_id, \
                        WorkRecord.outcome == WorkOutcome.SOLVED, \
                        Work.work_type == WorkType.CUCKOO_QA \
                    ) \
                    .order_by(WorkRecord.id.desc()) \
                    .first()

                unrated_work_records = []
                task.ratings = []
                if solved_coding_work_records:
                    for wr in solved_coding_work_records:
                        wr_ratings = wr.get_ratings()
                        if wr_ratings:
                            task.ratings.extend(wr_ratings)
                        else:
                            unrated_work_records.extend([wr])
                if latest_qa_work_record:
                    latest_qa_work_record_ratings = latest_qa_work_record.get_ratings()
                    if latest_qa_work_record_ratings:
                        task.ratings.extend(latest_qa_work_record_ratings)
                    else:
                        unrated_work_records.extend([latest_qa_work_record])

                if unrated_work_records:
                    current_app.logger.error(f'cannot set task status {status} to unrated work records {[wr.id for wr in unrated_work_records]}')
                    abort(422, code='not_rated', description=f'work record {[str(wr.id) + " " + str(wr.work.work_type) for wr in unrated_work_records]} not rated')

                # if work record has review start, update the review duration
                latest_coding_work_record = solved_coding_work_records[0]
                if latest_qa_work_record and latest_qa_work_record.review_start_time_epoch_ms:
                    now_epoch_ms = int(time.time() * 1000)
                    latest_qa_work_record.review_duration_seconds = (now_epoch_ms - latest_qa_work_record.review_start_time_epoch_ms) / 1000
                    db.session.add(latest_qa_work_record)
                if latest_coding_work_record and latest_coding_work_record.review_start_time_epoch_ms:
                    now_epoch_ms = int(time.time() * 1000)
                    latest_coding_work_record.review_duration_seconds = (now_epoch_ms - latest_coding_work_record.review_start_time_epoch_ms) / 1000
                    db.session.add(latest_coding_work_record)

            task.status = status

        db.session.commit()

        return TaskResponseSchema().jsonify(task)


class NotifyContributors(MethodView):
    @admin_jwt_required
    @parser.use_args(NotifyContributorsRequestSchema(), as_kwargs=True)
    def post(self, tasks=[], num_of_contributors=1):
        # cap number of notified contributors
        num_of_contributors = min(num_of_contributors, 10)

        users = User.query.filter_by(notifications=True).order_by(db.func.rand()).limit(num_of_contributors).all()
        if not users:
            abort(404)

        # get all the work associated with the tasks
        work = db.session.query(Work).filter(Work.task_id.in_(tasks)).all()

        send_contributors_notification_email(users, work)

        return EmptyResponseSchema().jsonify()
