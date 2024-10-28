from flask import current_app

from .base import BaseWorkMapper

from ...models.work import Work, WorkStatus, WorkType


class CodeReviewMapper(BaseWorkMapper):
    def map_work(self, completed_work, completed_work_record):
        if completed_work.work_type not in (WorkType.CREATE_FUNCTION, WorkType.UPDATE_FUNCTION, WorkType.OPEN_TASK):
            current_app.logger.error(f'work id {completed_work.id} chained CodeReviewMapper but has type {str(completed_work.work_type)}')
            return None

        if completed_work.status != WorkStatus.COMPLETE:
            current_app.logger.error(f'work id {completed_work.id} chained CodeReviewMapper but has status {str(completed_work.status)}')
            return None

        if not completed_work_record.solution_code:
            current_app.logger.error(f'work id {completed_work.id} chained CodeReviewMapper but work record has no solution code')
            return None

        # create a copy of the completed work context and add installed packages to it
        new_context = completed_work.work_input['context']

        if completed_work_record.installed_packages:
            if 'requirements' not in new_context or new_context['requirements'] is None:
                new_context['requirements'] = []

            new_context['requirements'] = new_context['requirements'] + completed_work_record.installed_packages

        # create a new work item of type 'review'
        review_work = Work(
            completed_work.task_id,
            WorkStatus.AVAILABLE,
            WorkType.REVIEW_TASK,
            f'Please review the solution for the following task:\n{completed_work.task.description}',
            {'code': completed_work_record.solution_code, 'context': new_context},
            deflated_chain=completed_work.chain[1:],
            priority=completed_work.priority,
            tags=completed_work.tags,
            skills=completed_work.skills
        )

        return [review_work]

    def get_init_params(self):
        return []
