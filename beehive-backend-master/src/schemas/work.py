from datetime import timedelta

from marshmallow.validate import OneOf, Range
import pytz

from ..schemas.task_context import TaskContextRequestSchema
from ..models.work import Work
from ..models.work_record import WorkRecord
from ..models.task import ReviewStatus
from ..models.task_classification import TaskTypeClassification
from ..schemas.task import RatingSchema, TaskSchema
from ..schemas.beehave import BeehaveReviewSchema
from ..utils.marshmallow import BeehiveSchemaMixin, ma, TimeEpochMs


class WorkSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Work

    id = ma.auto_field()
    created = ma.auto_field()
    task_id = ma.auto_field(data_key='taskId')
    status = ma.auto_field()
    work_type = ma.auto_field(data_key='workType')
    priority = ma.auto_field(data_key='priority')
    description = ma.auto_field()
    work_input = ma.auto_field(data_key='workInput')
    tags = ma.List(ma.String(), data_key='tags')
    skills = ma.List(ma.String(), data_key='skills')
    context = ma.List(ma.Nested(TaskContextRequestSchema), required=False)
    title = ma.String(data_key='title', required=False)
    repo_name = ma.String(data_key='repoName', required=False)
    repo_url = ma.String(data_key='repoUrl', required=False)


class WorkRecordSchema(ma.SQLAlchemySchema):
    class Meta:
        model = WorkRecord

    id = ma.auto_field()
    user_id = ma.auto_field(data_key='userId')
    work_id = ma.auto_field(data_key='workId')
    active = ma.auto_field()
    start_time_epoch_ms = ma.auto_field(data_key='startTimeEpochMs')
    tz_name = ma.auto_field(data_key='tzName')
    duration_seconds = ma.auto_field(data_key='durationSeconds')
    solution_rating = ma.auto_field(data_key='solutionRating')
    solution_feedback = ma.auto_field(data_key='solutionFeedback')
    solution_url = ma.auto_field(data_key='solutionUrl')
    latest_beehave_review = ma.Method('get_latest_beehave_review', data_key='latestBeehaveReview')

    def get_latest_beehave_review(self, obj):
        if not obj.beehave_reviews:
            return None
        
        return sorted(obj.beehave_reviews, key=lambda r: r.created)[-1].review_content


class WorkWithTaskSchema(WorkSchema):
    task = ma.Nested(TaskSchema)

class WorkWithBranchSchema(WorkSchema):
    branch_name = ma.String(data_key='branchName', required=False)

class WorkWithRatingSchema(WorkWithBranchSchema):
    rating_subjects = ma.List(ma.String(), data_key='ratingSubjects')
    rating_authorization_code = ma.String(data_key='ratingAuthorizationCode')

class ClassifiedWork(WorkWithRatingSchema):
    task_type = ma.Enum(TaskTypeClassification, by_value=True, data_key='taskType')

class WorkRecordResponseSchema(WorkRecordSchema, BeehiveSchemaMixin):
    work = ma.Nested(WorkWithTaskSchema)

class WorkRecordWithRatingSchema(WorkRecordSchema):
    rating_subjects = ma.List(ma.String(), data_key='ratingSubjects')
    rating_authorization_code = ma.String(data_key='ratingAuthorizationCode')

class GetAvailableWorkRequestSchema(ma.Schema):
    specific_work_id = ma.Integer(data_key='specificWorkId')
    current_work_id = ma.Integer(data_key='currentWorkId')


class GetAvailableWorkResponseSchema(ma.Schema, BeehiveSchemaMixin):
    work = ma.Nested(ClassifiedWork)
    work_record = ma.Nested(WorkRecordWithRatingSchema, data_key='workRecord')


class WorkStartRequestSchema(ma.Schema):
    work_id = ma.Integer(required=True, data_key='workId')
    start_time_epoch_ms = ma.Integer(
        required=True,
        data_key='startTimeEpochMs',
        # no more than 5 minutes in the past and max at the end of 2049
        validate=TimeEpochMs(past_delta=timedelta(minutes=5), max=2524607999000)
    )
    tz_name = ma.String(required=True, data_key='tzName', validate=OneOf(pytz.all_timezones))

class WorkStartResponseSchema(ma.Schema, BeehiveSchemaMixin):
    work_record = ma.Nested(WorkRecordWithRatingSchema, data_key='workRecord')

class WorkSkippedRequestSchema(ma.Schema):
    work_id = ma.Integer(required=True, data_key='workId')
    start_time_epoch_ms = ma.Integer(
        required=True,
        data_key='startTimeEpochMs',
        # no more than 5 minutes in the past and max at the end of 2049
        validate=TimeEpochMs(past_delta=timedelta(minutes=5), max=2524607999000)
    )
    tz_name = ma.String(required=True, data_key='tzName', validate=OneOf(pytz.all_timezones))

class WorkCheckpointRequestSchema(ma.Schema):
    work_id = ma.Integer(required=True, data_key='workId')
    # allow only positive duration
    duration_seconds = ma.Integer(required=True, data_key='durationSeconds', validate=Range(min=0))
    installed_packages = ma.List(ma.String(), data_key='installedPackages')

class WorkAnalyzeRequestSchema(ma.Schema):
    work_id = ma.Integer(required=True, data_key='workId')
    solution_url = ma.String(data_key='solutionUrl')

class WorkFinishRequestSchema(ma.Schema):
    work_id = ma.Integer(required=True, data_key='workId')
    # allow only positive duration
    duration_seconds = ma.Integer(required=True, data_key='durationSeconds', validate=Range(min=0))
    feedback = ma.String()
    review_status = ma.Enum(ReviewStatus, by_value=True, data_key='reviewStatus')
    review_feedback = ma.String(data_key='reviewFeedback')
    solution_url = ma.String(data_key='solutionUrl', required=False)


class WorkSolutionReviewRequestSchema(ma.Schema):
    work_record_id = ma.Integer(required=True, data_key='workRecordId')

class WorkSolutionReviewResponseSchema(BeehiveSchemaMixin, ma.Schema):
    solution_url = ma.String(data_key='solutionUrl', required=True)


class WorkAnalyzeResponseSchema(BeehaveReviewSchema, BeehiveSchemaMixin):
    pass


class WorkHistoryResponseSchema(ma.Schema, BeehiveSchemaMixin):
    project = ma.String()
    created = ma.String()
    name = ma.String()
    duration = ma.String()
    description = ma.String()
    ratings = ma.List(ma.Nested(RatingSchema))
