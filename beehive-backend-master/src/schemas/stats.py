from marshmallow import validates_schema
from marshmallow.validate import Range, ValidationError

from .honeycomb import HoneycombSchema
from .task import TaskSchema
from .work import WorkRecordSchema, WorkSchema
from .user import UserSchema
from ..utils.marshmallow import BeehiveSchemaMixin, ma


class GetStatsRequestSchema(ma.Schema):
    page = ma.Integer(required=True, validate=Range(min=0))
    results_per_page = ma.Integer(required=True, data_key='resultsPerPage', validate=Range(min=0))
    filter_list = ma.List(ma.Str(), data_key='filter')

    @validates_schema
    def validate_filter(self, data, **kwargs):
        # make sure each filter is a simple equal equation with two sides
        filters = data.get('filter_list')
        if filters:
            for f in filters:
                if '=' not in f or len(f.split('=')) != 2:
                    raise ValidationError('\'filter\' can only be a list of comparison statements (x=y)')

class TaskStatsSchema(TaskSchema):
    delegating_user_name = ma.String(data_key='delegatingUserName')


class WorkStatsSchema(WorkSchema):
    task = ma.Nested(TaskStatsSchema)
    reserved_worker_id = ma.auto_field(data_key='reservedWorkerId')
    reserved_worker_name = ma.String(data_key='reservedWorkerName')
    prohibited_worker_id = ma.auto_field(data_key='prohibitedWorkerId')
    prohibited_worker_name = ma.String(data_key='prohibitedWorkerName')


class WorkRecordStatsSchema(WorkRecordSchema):
    work = ma.Nested(WorkStatsSchema)
    user_name = ma.String(data_key='userName')
    work_records_contributors_viewed = ma.Integer(data_key='workRecordsContributorsViewed')


class GetActiveWorkResponseSchema(ma.Schema, BeehiveSchemaMixin):
    work = ma.List(ma.Nested(WorkRecordStatsSchema))
    total_count = ma.Integer(data_key='totalCount')
    page = ma.Integer()


class PendingWorkStatsSchema(WorkStatsSchema):
    work_records_count = ma.Integer(data_key='workRecordsCount')
    work_records_total_duration_seconds = ma.Integer(data_key='workRecordsTotalDurationSeconds')
    work_records_contributors_viewed = ma.Integer(data_key='workRecordsContributorsViewed')

class CompletedWorkStatsSchema(PendingWorkStatsSchema):
    worker_id = ma.String(data_key='workerId')
    worker_name = ma.String(data_key='workerName')
    work_records_net_duration_seconds = ma.Integer(data_key='workRecordsNetDurationSeconds')
    work_records_cost = ma.Decimal(data_key='workRecordsCost', as_string=True)
    work_records_upwork_duration_seconds = ma.Integer(data_key='workRecordsUpworkDurationSeconds')
    work_records_upwork_cost = ma.Decimal(data_key='workRecordsUpworkCost', as_string=True)
    work_records_exact_upwork_durations = ma.String(data_key='exactUpworkDurations')
    work_records_rounded_upwork_durations = ma.String(data_key='roundedUpworkDurations')
    work_records_contributors_viewed = ma.Integer(data_key='workRecordsContributorsViewed')

class ReserveWorkRequestSchema(ma.Schema):
    hours_reserved = ma.Integer(data_key='hoursReserved', required=False)

class ReserveWorkResponseSchema(WorkStatsSchema, BeehiveSchemaMixin):
    reserved_until_epoch_ms = ma.auto_field(data_key='reservedUntilEpochMs')

class ProhibitWorkResponseSchema(WorkStatsSchema, BeehiveSchemaMixin):
    pass

class GetPendingWorkResponseSchema(ma.Schema, BeehiveSchemaMixin):
    work = ma.List(ma.Nested(PendingWorkStatsSchema))
    total_count = ma.Integer(data_key='totalCount')
    page = ma.Integer()


class GetCompletedWorkResponseSchema(ma.Schema, BeehiveSchemaMixin):
    work = ma.List(ma.Nested(CompletedWorkStatsSchema))
    total_count = ma.Integer(data_key='totalCount')
    page = ma.Integer()


class GetInvalidTasksResponseSchema(ma.Schema, BeehiveSchemaMixin):
    tasks = ma.List(ma.Nested(TaskStatsSchema))
    total_count = ma.Integer(data_key='totalCount')
    page = ma.Integer()


class GetUsersResponseSchema(ma.Schema, BeehiveSchemaMixin):
    users = ma.List(ma.Nested(UserSchema))
    total_count = ma.Integer(data_key='totalCount')
    page = ma.Integer()


class HoneycombStatsSchema(HoneycombSchema):
    package_dependency_names = ma.List(ma.String(), data_key='packageDependencyNames')
    honeycomb_dependency_names = ma.List(ma.String(), data_key='honeycombDependencyNames')


class GetHoneycombsResponseSchema(ma.Schema, BeehiveSchemaMixin):
    honeycombs = ma.List(ma.Nested(HoneycombStatsSchema))
    total_count = ma.Integer(data_key='totalCount')
    page = ma.Integer()

class ContributorSchema(ma.Schema):
    id = ma.String()
    name = ma.String()
    active_work = ma.String(data_key='activeWork')
    number_of_reserved_works = ma.String(data_key='numberOfReservedWorks')
    number_of_works_in_review = ma.String(data_key='numberOfWorksInReview')
    number_of_completed_works = ma.String(data_key='numberOfCompletedWorks')
    number_of_total_works = ma.String(data_key='numberOfTotalWorks')
    number_of_cancelled_works = ma.String(data_key='numberOfCancelledWorks')
    number_of_skipped_works = ma.String(data_key='numberOfSkippedWorks')
    skipped_total_works_ratio = ma.String(data_key='skippedTotalWorksRatio')
    time_since_last_engagement = ma.Integer(data_key='timeSinceLastEngagement')
    time_since_last_work = ma.Integer(data_key='timeSinceLastWork')
    billable_hours_availability_ratio = ma.String(data_key='billableHoursAvailabilityRatio')
    average_billable = ma.String(data_key='averageBillable')
    weekly_availability = ma.String(data_key='weeklyAvailability')
    average_gross_work_duration = ma.Integer(data_key='averageGrossWorkDuration')
    average_net_work_duration = ma.Integer(data_key='averageNetWorkDuration')
    average_work_price = ma.Decimal(data_key='averageWorkPrice', places=2, as_string=True)
    average_iterations_per_work = ma.String(data_key='averageIterationsPerWork')
    hourly_rate = ma.String(data_key='hourlyRate')



class GetContributorsRequestSchema(ma.Schema):
    page = ma.Integer(required=True, validate=Range(min=0))
    results_per_page = ma.Integer(required=True, data_key='resultsPerPage', validate=Range(min=0))
    filter_list = ma.List(ma.Str(), data_key='filter')

    @validates_schema
    def validate_filter(self, data, **kwargs):
        # make sure each filter is a simple equal equation with two sides
        filters = data.get('filter_list')
        if filters:
            for f in filters:
                if '=' not in f or len(f.split('=')) != 2:
                    raise ValidationError('\'filter\' can only be a list of comparison statements (x=y)')

class GetContributorsResponseSchema(ma.Schema, BeehiveSchemaMixin):
    data = ma.List(ma.Nested(ContributorSchema))
    total_count = ma.Integer(data_key='totalCount')
    page = ma.Integer()

class RatingSchema(ma.Schema):
    id = ma.String(required=True, data_key='id')
    user = ma.String(required=True, data_key='user')
    object_key = ma.String(required=True, data_key='objectKey')
    subject = ma.String(required=True, data_key='subject')
    score = ma.Decimal(places=1, required=True, data_key='score', as_string=True)
    text = ma.String(required=False, data_key='text')

class WorkRecordRatingSchema(WorkRecordSchema):
    work = ma.Nested(WorkStatsSchema)
    user_name = ma.String(data_key='userName')
    outcome = ma.Integer(data_key='outcome')
    iterations_per_task = ma.Integer(data_key='iterationsPerTask')
    utc_start_time = ma.String(data_key='utcStartTime')
    utc_end_time = ma.String(data_key='utcEndTime')
    ratings = ma.List(ma.Nested(RatingSchema))
    average_rating = ma.String(data_key='averageRating')
    average_iterations_per_task = ma.String(data_key='averageIterationsPerTask')

class ContributorHistoryResponseSchema(ma.Schema, BeehiveSchemaMixin):
    work = ma.List(ma.Nested(WorkRecordRatingSchema))
    total_count = ma.Integer(data_key='totalCount')
    page = ma.Integer()
