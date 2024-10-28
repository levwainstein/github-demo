from datetime import date, timedelta, timezone
import time

from flask import current_app, redirect
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy.sql import label, or_, and_

from ..logic.robobee import get_pr_info
from ..logic.beehave import beehave_review_pr, run_beehave_pr_github_bot
from ..logic.work_mappers.base import inflate_mapper
from ..logic.cuckoo import CuckooEvent, dispatch_cuckoo_event
from ..logic.praesepe import RatingSubject, get_rating_items, get_rating_subjects, get_praesepe_authorization_code
from ..models.task import ReviewStatus, Task, TaskStatus
from ..models.task_context import TaskContext
from ..models.quest import QuestStatus
from ..models.work import Work, WorkStatus, WorkType
from ..models.work_record import WorkOutcome, WorkRecord
from ..models.beehave_review import BeehaveReview
from ..models.skill import UserSkill, WorkSkill
from ..models.tag import Tag, WorkTag
from ..models.user import User
from ..models.repository import Repository
from ..models.project import Project, ProjectDelegator
from ..schemas import EmptyResponseSchema
from ..schemas.work import (
    WorkRecordResponseSchema,
    GetAvailableWorkRequestSchema,
    GetAvailableWorkResponseSchema,
    WorkSolutionReviewRequestSchema,
    WorkSolutionReviewResponseSchema,
    WorkStartRequestSchema,
    WorkStartResponseSchema,
    WorkSkippedRequestSchema,
    WorkCheckpointRequestSchema,
    WorkFinishRequestSchema,
    WorkAnalyzeRequestSchema,
    WorkAnalyzeResponseSchema,
    WorkHistoryResponseSchema
)
from ..utils.auth import activated_jwt_required
from ..utils.db import db
from ..utils.email import send_task_feedback_email, send_task_solved_email
from ..utils.errors import abort
from ..utils.marshmallow import parser
from ..utils.metrics import work_finish_summary
from ..utils.grpc_client import grpc_client


# Keep track of the work a user is performing
class WorkRecordCRUD(MethodView):
    @activated_jwt_required
    def get(self, work_id):
        user_id = get_jwt_identity()
        

        work_records_query = WorkRecord.query \
            .filter_by(user_id=user_id) \
            .options(joinedload(WorkRecord.work).joinedload(Work.task)) \
            .order_by(WorkRecord.start_time_epoch_ms.desc())
        
        if work_id:
            work_records_query = work_records_query.filter_by(work_id=work_id)

        return WorkRecordResponseSchema(many=True).jsonify(work_records_query.all())

class WorkHistory(MethodView):
    @activated_jwt_required
    def get(self):
        user_id = get_jwt_identity()
        n_days_ago = date.today() - timedelta(days=30)
        
        work_records_query = WorkRecord.query \
            .filter_by(user_id=user_id) \
            .options(joinedload(WorkRecord.work).joinedload(Work.task)) \
            .filter(Work.id == WorkRecord.work_id, Task.id == Work.task_id) \
            .filter(Work.status == WorkStatus.COMPLETE) \
            .filter(Task.status == TaskStatus.ACCEPTED) \
            .filter(WorkRecord.created > n_days_ago) \
            .order_by(WorkRecord.start_time_epoch_ms.desc())
        
        records = work_records_query.all()
        ratings = []
        if len(records) > 0:
            ratings = get_rating_items(user_id, [r.rating_object_key for r in records]) or []

        results = [{
            'project': next(iter([x for x in record.work.task.tags if x.name.startswith('project:')]), None),
            'created': record.work.created,
            'name': record.work.task.func_name,
            'duration': record.duration_seconds,
            'description': record.work.description,
            'rating_object_key': record.rating_object_key,
            'ratings': [r for r in ratings if r['objectKey'] == record.rating_object_key]
        } for record in records]

        return WorkHistoryResponseSchema(many=True).jsonify(results)


class AvailableWork(MethodView):
    # get a single available task to work on
    @activated_jwt_required
    @parser.use_args(GetAvailableWorkRequestSchema(), as_kwargs=True, location='querystring')
    def get(self, specific_work_id=None, current_work_id=None):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()

        if not user:
            current_app.logger.error('User not found')
            abort(404)
        current_app.logger.info('Getting a new task')
        work = None
        in_process_work = WorkRecord.query.filter_by(user_id=user_id, active=True) \
            .options(joinedload(WorkRecord.work).joinedload(Work.task).joinedload(Task.task_classifications)) \
            .first()

        if in_process_work:
            current_app.logger.info('Found worker in-process work item')
            work = in_process_work.work

            # for in process qa work records add rating which is different than the work description one
            # rated object derived from work input and not current work record
            if work.work_type in [WorkType.CUCKOO_QA]:
                in_process_work.rating_subjects = get_rating_subjects(in_process_work.work)

                # fetch rating authorization code for available work item
                in_process_work.rating_authorization_code = get_praesepe_authorization_code(
                    target_user_id=work.work_input['user_id'],
                    object_key=f'wr-{work.work_input["work_record_id"]}',
                    subjects=in_process_work.rating_subjects

                    ## TODO: change back to user param required once we support user groups
                    # enabling non delegators to rate solution required removing this additional security
                    # user_id=in_process_work.work.task.delegating_user_id
                )

        # if no in-process work record was found and a specific work item was
        # requested look for it
        if not work and specific_work_id:
            specific_work = Work.query \
                .filter(Work.id == specific_work_id) \
                .filter(Work.status == WorkStatus.AVAILABLE) \
                .join(Task, and_(
                    Work.task_id == Task.id,
                    Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROCESS, TaskStatus.MODIFICATIONS_REQUESTED]))
                ) \
                .first()

            if specific_work:
                current_app.logger.info('Found specific work item for worker')
                work = specific_work

        # if no in-process work record or specific work item were found look
        # for a reserved work item
        if not work:
            reserved_work = Work.query \
                .filter(Work.reserved_worker_id == user_id) \
                .filter(Work.status == WorkStatus.AVAILABLE) \
                .join(Task, and_(
                    Work.task_id == Task.id,
                    Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROCESS, TaskStatus.MODIFICATIONS_REQUESTED]))
                ) \
                .order_by(db.func.power((100 - Task.priority), 2) * \
                    db.func.random()) \
                .first()
            if reserved_work:
                current_app.logger.info('Found worker reserved work item')
                work = reserved_work

        # if a reserved work item was not found either look for any availbale
        # work item
        if not work:
            # this is a sort-of normalized column of the sum of work time already
            # invested in a task by the worker in minutes, or 0.1 if the worker
            # has never worked on this task. this does encourage tasks on which
            # the worker has worked for less than 6 seconds to appear more, but
            # once the worker works on a task for a longer period its chance
            # of being selected declines up to a maximum of 10 minutes
            normalized_duration_col = label(
                'work_duration_seconds',
                db.func.coalesce(
                    db.func.least(
                        db.func.sum(WorkRecord.duration_seconds) / 60,
                        10
                    ),
                    0.1
                )
            )

            # using contains_eager to trick sqlalchemy
            # to think we loaded all items for the relationship Work.task
            available_work_query = Work.query \
                .outerjoin(WorkRecord, Work.id == WorkRecord.work_id) \
                .join(Task, and_(
                    Work.task_id == Task.id,
                    Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROCESS, TaskStatus.MODIFICATIONS_REQUESTED]))
                ) \
                .join(Work.tags, isouter=True) \
                .options(contains_eager(Work.task)) \
                .add_columns(normalized_duration_col) \
                .filter(Work.status == WorkStatus.AVAILABLE) \
                .filter(or_(
                    Work.reserved_until_epoch_ms == None,
                )) \

            # make sure work is not the current one
            if current_work_id:
                available_work_query = available_work_query \
                    .filter(Work.id != current_work_id)

            # filter work by tags if user is tagged
            available_work_query = available_work_query \
                .filter(or_(
                    ~Work.tags.any(),
                    Work.tags.any(WorkTag.tag_id.in_(t.id for t in user.tags))
                ))

            # filter work if it's prohibited for this worker
            available_work_query = available_work_query \
                .filter(or_(
                    Work.prohibited_worker_id == None,
                    Work.prohibited_worker_id != user_id
                )
            )

            # columns and subquery to count matching work-user skills
            work_skill_matches_col = label(
                'matching_skills_count',
                db.func.count()
            )
            skill_matches = WorkSkill.query \
                .join(
                    UserSkill, WorkSkill.skill_id == UserSkill.skill_id
                ) \
                .filter(UserSkill.user_id == user_id) \
                .with_entities(WorkSkill.work_id) \
                .add_columns(work_skill_matches_col) \
                .group_by(WorkSkill.work_id) \
                .subquery()

            # max out at 5 matched skills
            work_skill_matches_coalesced_col = label(
                'matching_skills_coalesced_count',
                db.func.least(
                    db.func.coalesce(skill_matches.c.matching_skills_count, 0),
                    5
                )
            )

            available_work_query = available_work_query \
                .outerjoin(skill_matches, Work.id == skill_matches.c.work_id) \
                .add_columns(work_skill_matches_coalesced_col)

            available_work_query = available_work_query \
                .group_by(Work.id, Task.id, Tag.id) \
                .order_by(
                    # deduct the matched skills count from 6 so that its order is reversed and
                    # so the result is never 0 (which would mean max-matched-skill work items
                    # will always "win" since they will have a multiplication by 0). raise the
                    # result to a power of 1.5 to increase the distance between the different
                    # match amounts. multiply by the normalized duration col and a random
                    # value to produce a random order which favours more skills matched and
                    # less time previously worked
                    db.func.power((101 - Task.priority), 2) * \
                    db.func.power(6 - work_skill_matches_coalesced_col, 1.5) * \
                    normalized_duration_col * \
                    db.func.random()
                )
            work = available_work_query.first()

            if work:
                current_app.logger.info('Found new work item for worker')
                work = work.Work  # multiple results since we added columns to the query

        if not work:
            current_app.logger.info('No work found')
            # no work is available
            abort(404)

        # for available work rating subjects will always be only rating the description
        work.rating_subjects = [RatingSubject.WORK_DESCRIPTION.name.lower()]

        # fetch rating authorization code for available work item
        work.rating_authorization_code = get_praesepe_authorization_code(
            target_user_id=work.task.delegating_user_id,
            object_key=work.rating_object_key,
            subjects=work.rating_subjects

            ## TODO: change back to user param required once we support user groups
            # enabling non delegators to rate solution required removing this additional security
            # user_id=user_id
        )

        # add relevant task classifications
        if work.task and work.task.task_classifications:
            type_classifications = [t.task_type for t in work.task.task_classifications if t.task_type]
            if type_classifications:
                work.task_type = type_classifications[0]

        # add new field title from task
        work.title = None
        if work.task and work.task.title:
            work.title = work.task.title

        # add related repo and branch
        if work.task and work.task.repository:
            work.repo_url = work.task.repository.url
            work.repo_name = work.task.repository.name
            
        github_user = user.github_user if user.github_user else '<your_github_user>'
        work.branch_name = f'external/{github_user}/{work.title.lower().replace(" ", "-")}' if work.title else None
        if work.work_input and work.work_input.get('solution_url', None):
            pr_info = get_pr_info(work.work_input['solution_url'], grpc_client)
            work.branch_name = pr_info.head.ref if pr_info else f'external/{github_user}/{work.title.lower().replace(" ", "-")}' if work.title else None


        context_items = TaskContext.query \
                .filter(TaskContext.task_id == work.task_id) \
                .all()
        work.context = context_items

        if in_process_work:
            return GetAvailableWorkResponseSchema().jsonify({'work': work, 'work_record': in_process_work})
        else:
            return GetAvailableWorkResponseSchema().jsonify({'work': work})


class WorkStart(MethodView):
    # start working on a task (accept task)
    @activated_jwt_required
    @parser.use_args(WorkStartRequestSchema(), as_kwargs=True)
    def post(self, work_id, start_time_epoch_ms, tz_name):
        user_id = get_jwt_identity()

        work = Work.query.filter_by(id=work_id, status=WorkStatus.AVAILABLE) \
            .options(joinedload(Work.task)) \
            .first()
        if not work:
            abort(404)

        # make sure the worker is only working on a single task at a time
        if WorkRecord.query.filter_by(user_id=user_id, active=True).first():
            abort(400, code='worker_occupied')

        current_app.logger.info(f'starting work of {user_id} on {work_id}')

        work_record = WorkRecord(user_id, work_id, True, start_time_epoch_ms, tz_name)
        db.session.add(work_record)

        # notify cuckoo service that work has started
        if work.work_type in (WorkType.CUCKOO_CODING, WorkType.CUCKOO_ITERATION, WorkType.CUCKOO_QA):

            github_user = None
            user = User.query.filter_by(id=user_id).first()
            if user:
                github_user = user.github_user

            # first work in task
            first_chain_work = True if work.task.status in (TaskStatus.PENDING, TaskStatus.NEW, TaskStatus.MODIFICATIONS_REQUESTED) else False
            payload = {
                'eventType': CuckooEvent.WORK_ACCEPTED.name,
                'startTime': time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(start_time_epoch_ms/1000.0)),
                'user': user_id,
                'githubUser': github_user,
                'workType': work.work_type.name,
                'firstChainWork': first_chain_work
            }

            res = dispatch_cuckoo_event(
                work.task_id,
                payload
            )
            if not res:
                abort(500, code='cuckoo_notification_failed')

            if work.task.quest_id:
                work.task.quest.status = QuestStatus.IN_PROCESS

        # set work status to unavailable and task status to in-process
        work.status = WorkStatus.UNAVAILABLE
        work.task.status = TaskStatus.IN_PROCESS

        db.session.commit()

        # on chain link start, rating should happen on frontend instead of cuckoo
        if work.work_type in [WorkType.CUCKOO_QA]:
            # rated object derived from work input and not current work record
            rating_subjects = get_rating_subjects(work)
            work_record.rating_subjects = rating_subjects
            work_record.rating_authorization_code = get_praesepe_authorization_code(
                target_user_id=work.work_input['user_id'],
                object_key=f'wr-{work.work_input["work_record_id"]}',
                subjects=rating_subjects
                
                ## TODO: change back to user param required once we support user groups
                # enabling non delegators to rate solution required removing this additional security

                # user_id=work_record.user_id
            )

        return WorkStartResponseSchema().jsonify({'work_record': work_record})

class WorkSkipped(MethodView):
    # start working on a task (accept task)
    @activated_jwt_required
    @parser.use_args(WorkSkippedRequestSchema(), as_kwargs=True)
    def post(self, work_id, start_time_epoch_ms, tz_name):
        user_id = get_jwt_identity()

        work = Work.query.filter_by(id=work_id, status=WorkStatus.AVAILABLE) \
            .options(joinedload(Work.task)) \
            .first()
        if not work:
            abort(404)

        work_record = WorkRecord(user_id, work_id, False, start_time_epoch_ms, tz_name, WorkOutcome.SKIPPED)
        db.session.add(work_record)
        db.session.commit()

        return EmptyResponseSchema().jsonify()


class WorkCheckpoint(MethodView):
    # save current code and duration even though the worker hasn't finished working
    # on the task yet
    @activated_jwt_required
    @parser.use_args(WorkCheckpointRequestSchema(), as_kwargs=True)
    def post(self, work_id, duration_seconds):
        user_id = get_jwt_identity()

        work = Work.query \
            .filter_by(id=work_id) \
            .options(joinedload(Work.task)) \
            .first()
        if not work:
            abort(404)

        work_record = WorkRecord.query.filter_by(
            user_id=user_id, work_id=work_id, active=True
        ).first()
        if not work_record:
            abort(404)

        # update work record values
        work_record.duration_seconds = duration_seconds

        db.session.commit()

        return EmptyResponseSchema().jsonify()


class WorkFinish(MethodView):
    # finish working on a task by either posting a solution, cancelling work, requesting a package,
    # posting a feedback to it, posting a PR url or submitting a review
    @activated_jwt_required
    @parser.use_args(WorkFinishRequestSchema(), as_kwargs=True)
    def post(self, work_id, duration_seconds, 
        feedback=None,
        review_status=None, review_feedback=None, force_submit_reason=None, solution_url=None):
        
        user_id = get_jwt_identity()

        work = Work.query \
            .filter_by(id=work_id) \
            .options(joinedload(Work.task)) \
            .first()
        if not work:
            abort(404)

        work_record = WorkRecord.query.filter_by(
            user_id=user_id, work_id=work_id, active=True
        ).first()
        if not work_record:
            abort(404)

        # update task, work and work record values
        work_record.duration_seconds = duration_seconds
        work_record.active = False

        work_output = None

        if feedback:
            # we send the latest code with the feedback to display it to the delegator
            work.task.status = TaskStatus.INVALID
            work_record.feedback = feedback
            work.task.feedback = feedback

            # email delegating user
            send_task_feedback_email(work.task)

            work_output = 'feedback'
            work_record.outcome = WorkOutcome.FEEDBACK
        elif work.work_type in (WorkType.REVIEW_TASK, WorkType.CHECK_REUSABILITY) and (review_status or review_feedback):
            work.status = WorkStatus.COMPLETE
            work.task.review_status = review_status
            work.task.review_feedback = review_feedback

            work_output = 'solve'
            work_record.outcome = WorkOutcome.SOLVED
        elif work.work_type in (WorkType.CUCKOO_CODING, WorkType.CUCKOO_ITERATION) and solution_url:
            work.status = WorkStatus.COMPLETE
            work_record.solution_url = solution_url
            work_record.outcome = WorkOutcome.SOLVED
            
            if work.chain:
                work_output = 'solve_chain_link_code'
            else:
                work_output = 'solve'
            work_record.outcome = WorkOutcome.SOLVED

        elif work.work_type == WorkType.CUCKOO_QA and (review_feedback or review_status):
            work.status = WorkStatus.COMPLETE
            work_record.solution_url = solution_url

            work.task.review_status = review_status
            work.task.review_feedback = review_feedback

            work_output = 'solve_chain_link_qa'
            work_record.outcome = WorkOutcome.SOLVED
        else:
            work.status = WorkStatus.AVAILABLE
            work.task.status = TaskStatus.PENDING

            work_output = 'cancel'
            work_record.outcome = WorkOutcome.CANCELLED

        # if work was complete check if there is more work down the chain. otherwise
        # task is complete
        if work.status == WorkStatus.COMPLETE:
            new_work = None

            if work.chain and len(work.chain) > 0:
                work_mapper = inflate_mapper(work.chain[0])

                # map the work that was just completed to new work items
                new_work = work_mapper.map_work(work, work_record)

            if new_work and len(new_work) > 0:
                # save new work items to db
                for w in new_work:
                    db.session.add(w)
            else:
                work.task.status = TaskStatus.SOLVED

                # email delegating user
                send_task_solved_email(work.task)

        # record metric with output
        work_finish_summary.labels(output=work_output).observe(duration_seconds)

        # notify cuckoo service that work has ended / cancelled / got feedback
        if work.work_type in (WorkType.CUCKOO_CODING, WorkType.CUCKOO_ITERATION, WorkType.CUCKOO_QA):

            # commit again so orms are updated
            db.session.commit()

            payload = None

            github_user = None
            user = User.query.filter_by(id=user_id).first()
            if user:
                github_user = user.github_user

            match work_output:
                case 'feedback':
                    payload = {
                        'eventType': CuckooEvent.WORK_NEW_FEEDBACK.name,
                        'feedback': feedback,
                        'user': user_id,                        
                        'githubUser': github_user
                    }
                case 'solve':
                    # rating for the work record just solved
                    rating_subjects = get_rating_subjects(work_record.work)
                    rating_authorization_code = get_praesepe_authorization_code(
                        target_user_id=work_record.user_id,
                        object_key=work_record.rating_object_key,
                        subjects=rating_subjects

                        ## TODO: change back to user param required once we support user groups
                        # enabling non delegators to rate solution required removing this additional security

                        # user_id=work.task.delegating_user_id
                    )
                    rating_url = f'{current_app.config["FRONTEND_BASE_URL"]}/rate?subjects={",".join(rating_subjects)}&code={rating_authorization_code}'

                    payload = {
                        'eventType': CuckooEvent.WORK_SOLVED.name,
                        'solutionReviewUrl': work_record.solution_review_url,
                        'solutionUrl': work_record.solution_url,
                        'workDurationMinutes': work_record.duration_seconds / 60,
                        'user': user_id,
                        'ratingUrl': rating_url,
                        'githubUser': github_user,
                        'workType': work_record.work.work_type.name
                    }
                case 'finish_review':
                    rating_subjects = get_rating_subjects(work_record.work)
                    rating_authorization_code = get_praesepe_authorization_code(
                        target_user_id=work_record.user_id,
                        object_key=work_record.rating_object_key,
                        subjects=rating_subjects
        
                        ## TODO: change back to user param required once we support user groups
                        # enabling non delegators to rate solution required removing this additional security

                        # user_id=work.task.delegating_user_id
                    )
                    rating_url = f'{current_app.config["FRONTEND_BASE_URL"]}/rate?subjects={",".join(rating_subjects)}&code={rating_authorization_code}'

                    payload = {
                        'eventType': CuckooEvent.WORK_SOLVED.name,
                        'solutionReviewUrl': work_record.solution_review_url,
                        'solutionUrl': work_record.solution_url,
                        'workDurationMinutes': work_record.duration_seconds / 60,
                        'user': user_id,  
                        'ratingUrl': rating_url,
                        'githubUser': github_user,
                        'workType': work_record.work.work_type.name
                    }
                case 'solve_chain_link_code':
                    payload = {
                        'eventType': CuckooEvent.WORK_SOLVED.name,
                        'solutionReviewUrl': work_record.solution_review_url,
                        'solutionUrl': work_record.solution_url,
                        'workDurationMinutes': work_record.duration_seconds / 60,
                        'workType': work_record.work.work_type.name,
                        'user': user_id,  
                        'githubUser': github_user,
                        'lastChainWork': False
                    }
                case 'solve_chain_link_qa':

                    outcome = None
                    rating_url = None
                    last_chain_work = False
                    if work_record.work.task.status in [TaskStatus.SOLVED]:

                        last_chain_work = True
                        if review_status == ReviewStatus.ADEQUATE:
                            outcome = f'user {work_record.user_id} marked solution adequate'
                        else:
                            outcome = 'qa iterations count has been exhausted, however the original code did not pass QA'

                        # rated object derived from work input and not current work record
                        qa_rating_subjects = [RatingSubject.WORK_REVIEW_QA_FUNCTIONALITY.name.lower(), RatingSubject.WORK_REVIEW_CODE_QUALITY.name.lower()]
                        qa_rating_authorization_code = get_praesepe_authorization_code(
                            target_user_id=work_record.user_id,
                            object_key=work_record.rating_object_key,
                            subjects=qa_rating_subjects
                            
                            ## TODO: change back to user param required once we support user groups
                            # enabling non delegators to rate solution required removing this additional security

                            # user_id=work.task.delegating_user_id
                        )
                        coding_rating_subjects = [RatingSubject.WORK_SOLUTION_CODE_QUALITY.name.lower()]
                        coding_rating_authorization_code = get_praesepe_authorization_code(
                            target_user_id=work_record.work.work_input['user_id'],
                            object_key=f'wr-{work_record.work.work_input["work_record_id"]}',
                            subjects=coding_rating_subjects
                            
                            ## TODO: change back to user param required once we support user groups
                            # enabling non delegators to rate solution required removing this additional security

                            # user_id=work.task.delegating_user_id
                        )
                        rating_url = f'{current_app.config["FRONTEND_BASE_URL"]}/rate?subjects={",".join(qa_rating_subjects)}~{",".join(coding_rating_subjects)}&code={qa_rating_authorization_code}~{coding_rating_authorization_code}'
                        
                    payload = {
                        'eventType': CuckooEvent.WORK_SOLVED.name,
                        'workDurationMinutes': work_record.duration_seconds / 60,
                        'workType': work_record.work.work_type.name,
                        'user': user_id,  
                        'githubUser': github_user,
                        'lastChainWork': last_chain_work,
                        'outcome': outcome, 
                        'ratingUrl': rating_url
                    }

                    if last_chain_work:
                        payload['solutionReviewUrl'] = work_record.solution_review_url

                case 'cancel':
                    payload = {
                        'eventType': CuckooEvent.WORK_CANCELED.name,
                        'workDurationMinutes': work_record.duration_seconds / 60,
                        'user': user_id,
                        'githubUser': github_user
                    }

            if payload:
                res = dispatch_cuckoo_event(
                    work.task_id, payload)
                if not res:
                    abort(500, code='cuckoo_notification_failed')

        db.session.commit()

        # trigger task for pollinator to add review in github
        if work_output in ['solve', 'solve_chain_link_code'] and solution_url:
            run_beehave_pr_github_bot(solution_url, work_record.work.description)
        
        return EmptyResponseSchema().jsonify()

class WorkAnalyze(MethodView):
    @activated_jwt_required
    @parser.use_args(WorkAnalyzeRequestSchema(), as_kwargs=True)
    def post(self, work_id, solution_url):
        user_id = get_jwt_identity()

        work = Work.query \
            .filter_by(id=work_id) \
            .options(joinedload(Work.task)) \
            .first()
        if not work:
            abort(404)

        work_record = WorkRecord.query.filter_by(
            user_id=user_id, work_id=work_id, active=True
        ).first()

        if not work_record:
            abort(404)

        previous_pr_sha = None
        if work_record.beehave_reviews:
            previous_pr_sha = sorted(work_record.beehave_reviews, key=lambda r: r.created)[-1].last_commit_sha

        review_status_code, review_result = beehave_review_pr(solution_url, work_record.work.description, previous_pr_sha=previous_pr_sha)
        if review_status_code != 200:
            abort(review_status_code)

        new_beehave_review = BeehaveReview(
            work_record_id = work_record.id,
            review_content = review_result['data']['output'],
            last_commit_sha = review_result['data']['output']['last_commit_sha']
        )

        db.session.add(new_beehave_review)
        db.session.commit()

        return WorkAnalyzeResponseSchema().jsonify(new_beehave_review)

class WorkSolutionReview(MethodView):
    @activated_jwt_required
    @parser.use_args(WorkSolutionReviewRequestSchema(), as_kwargs=True)
    def post(self, work_record_id):
        user_id = get_jwt_identity()

        # verify user has permissions to review this work
        user_permitted_repos = Repository.query \
            .join(ProjectDelegator, Repository.project_id == ProjectDelegator.project_id ) \
            .join(Project, Repository.project_id == Project.id ) \
            .filter(ProjectDelegator.user_id == user_id ) \
            .all()
        if len(user_permitted_repos) == 0:
            abort(401)

        # get relevant work record that is being reviewed
        completed_work_record = WorkRecord.query \
            .filter_by(
                id=work_record_id, active=False
            ) \
            .options(joinedload(WorkRecord.work).joinedload(Work.task)) \
            .first()

        if not completed_work_record:
            abort(404)

        completed_work_repo = completed_work_record.work.task.repository
        if completed_work_repo and completed_work_repo not in user_permitted_repos:
            abort(400, code='user_has_no_auth_for_repo')

        # not all tasks have repository defined (ones originated from cuckoo)
        # so also need to cross check project via tags
        if not completed_work_repo:
            user_permitted_projects = [r.project.name for r in user_permitted_repos]
            user = User.query.filter_by(id=user_id).first()
            user_project_tags = [t.name.replace('project:','') for t in user.tags]

            work_project_tags = [t.name.replace('project:','') for t in completed_work_record.work.tags]
            
            if not set(work_project_tags) <= set(user_permitted_projects + user_project_tags):
                abort(400, code='user_has_no_auth_for_repo')

        # update work record on start review
        completed_work_record.review_start_time_epoch_ms = int(time.time() * 1000)
        completed_work_record.review_tz_name = timezone.utc
        completed_work_record.review_user_id = user_id
        
        db.session.add(completed_work_record)
        db.session.commit()

        # Redirect to solution url
        redirect_url = completed_work_record.solution_url or completed_work_record.work.work_input['solution_url']
        if not redirect_url:
            abort(500, code='work_record_solution_url_not_found')

        return WorkSolutionReviewResponseSchema().jsonify({'solution_url': redirect_url})

        