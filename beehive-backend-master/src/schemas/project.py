from marshmallow import validates_schema
from marshmallow.validate import Range, ValidationError

from ..utils.marshmallow import ma

class ProjectRequestSchema(ma.Schema):
    project_id = ma.Integer()
    page = ma.Integer(required=False, validate=Range(min=0))
    results_per_page = ma.Integer(required=False, data_key='resultsPerPage', validate=Range(min=0))

class ProjectResponseSchema(ma.Schema):
    project_id = ma.String(data_key='id')
    project_name = ma.String(data_key='projectName')
    date = ma.String(required=False)

class ListProjectsResponseSchema(ma.Schema):
    projects = ma.List(ma.Nested(ProjectResponseSchema))

class ProjectQueueRequestSchema(ma.Schema):
    project_id = ma.Integer()

class TaskTrelloLinkResponseSchema(ma.Schema):
    task_id = ma.String(data_key='taskId')
    short_link = ma.String(data_key='shortLink')

class ProjectQueueResponseSchema(ma.Schema):
    pending = ma.Integer(required=False)
    in_review = ma.Integer(required=False, data_key='inReview')
    in_progress = ma.Integer(required=False, data_key='inProgress')
    pending_trello_links = ma.List(ma.Nested(TaskTrelloLinkResponseSchema), data_key='pendingTrelloLinks')
    in_progress_trello_links = ma.List(ma.Nested(TaskTrelloLinkResponseSchema), data_key='inProgressTrelloLinks')
    in_review_trello_links = ma.List(ma.Nested(TaskTrelloLinkResponseSchema), data_key='inReviewTrelloLinks')

class ProjectDailyActivityResponseSchema(ma.Schema):
    date = ma.String()
    work_items_solved = ma.Integer(data_key='workItemsSolved')
    tasks_completed = ma.Integer(data_key='tasksCompleted')
    tasks_delegated = ma.Integer(data_key='tasksDelegated')
    work_items_reviewed = ma.Integer(data_key='workItemsReviewed')
    work_items_solved_links = ma.List(ma.Nested(TaskTrelloLinkResponseSchema), data_key='workItemsSolvedLinks')
    tasks_completed_links = ma.List(ma.Nested(TaskTrelloLinkResponseSchema), data_key='tasksCompletedLinks')
    tasks_delegated_links = ma.List(ma.Nested(TaskTrelloLinkResponseSchema), data_key='tasksDelegatedLinks')
    work_items_reviewed_links = ma.List(ma.Nested(TaskTrelloLinkResponseSchema), data_key='workItemsReviewedLinks')

class ProjectActivityResponseSchema(ma.Schema):
    activities = ma.List(ma.Nested(ProjectDailyActivityResponseSchema))

class ProjectContributorResponseSchema(ma.Schema):
    name = ma.String()
    country = ma.String()
    active = ma.Boolean(required=False)
    last_work = ma.String(data_key='lastWork')
    last_engagement = ma.String(data_key='lastEngagement')
    reserved_works = ma.Integer(data_key='reservedWorks')
    works_in_review = ma.Integer(data_key='worksInReview')
    hourly_rate = ma.Decimal(data_key='hourlyRate', places=2, as_string=True)
    skills = ma.List(ma.String())

class ProjectContributorsResponseSchema(ma.Schema):
    contributors = ma.List(ma.Nested(ProjectContributorResponseSchema))

class ProjectBudgetBrokenSchema(ma.Schema):
    name = ma.String()
    amount = ma.Integer()
    hours = ma.Decimal(places=2, as_string=True)

class ProjectBudgetSchema(ma.Schema):
    date = ma.String()
    budget = ma.List(ma.Nested(ProjectBudgetBrokenSchema))

class ProjectBudgetReviewSchema(ma.Schema):
    budgetReviews = ma.List(ma.Nested(ProjectBudgetSchema))

class ProjectDelayedTaskResponseSchema(ma.Schema):
    id = ma.String()
    created_at = ma.String(data_key='createdAt')
    updated_at = ma.String(data_key='updatedAt')
    task_name = ma.String(data_key='taskName')
    skills = ma.List(ma.String())
    status = ma.String()
    billable_time = ma.Integer(data_key='billableTime')
    priority = ma.String()
    link = ma.Nested(TaskTrelloLinkResponseSchema, required=False)

class ProjectDelayedTasksResponseSchema(ma.Schema):
    delayedTasks = ma.List(ma.Nested(ProjectDelayedTaskResponseSchema))

