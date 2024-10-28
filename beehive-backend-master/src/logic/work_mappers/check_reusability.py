from flask import current_app


from .base import BaseWorkMapper

from ...models.work import Work, WorkStatus, WorkType
from ...models.task import ReviewStatus, TaskType


class CheckReusabilityMapper(BaseWorkMapper):
    def __init__(self, modification_completed=False):
        self.modification_completed = modification_completed

    def map_work(self, completed_work, completed_work_record):
        if completed_work.work_type not in (WorkType.CHECK_REUSABILITY, WorkType.OPEN_TASK):
            current_app.logger.error(f'work id {completed_work.id} chained CheckReusabilityMapper but has type {str(completed_work.work_type)}')
            return None

        if completed_work.status != WorkStatus.COMPLETE:
            current_app.logger.error(f'work id {completed_work.id} chained CheckReusabilityMapper but has status {str(completed_work.status)}')
            return None

        if not completed_work.task.review_status:
            current_app.logger.error(f'work id {completed_work.id} chained CheckReusabilityMapper but work record has no review status')
            return None

        # create a copy of the completed work context and add installed packages to it
        new_context = completed_work.work_input['context']

        if completed_work_record.installed_packages:
            if 'requirements' not in new_context or new_context['requirements'] is None:
                new_context['requirements'] = []

            new_context['requirements'] = new_context['requirements'] + completed_work_record.installed_packages

        # if there is a new solution, we take that, otherwise we take the original code.
        # this is necessary since if the contributors requests modification, we do a modification of the original code
        code = completed_work_record.solution_code if completed_work_record.solution_code else completed_work.task.original_code

        if completed_work.task.review_status == ReviewStatus.ADEQUATE or self.modification_completed:
            # code is an adequate honeycomb or already went through modifications -> proceed to a documentation task
            chain = completed_work.chain[1:]
            
            # create the new work item
            documentation_work = Work(
                completed_work.task_id,
                WorkStatus.AVAILABLE,
                WorkType.OPEN_TASK,
                'Please adjust the code below to:\n* Include a well written docstring (use Google stylesheet as demonstrated in [this example](https://realpython.com/documenting-python-code/#google-docstrings-example)).\n* Make sure the code is written nicely and neatly.\n* If needed please add comments.\n\nIf the code satisfies all these bullets, you may submit it as is.\n',
                {'code': code, 'context': new_context},
                chain,
                priority=completed_work.priority,
                tags=completed_work.tags,
                skills=completed_work.skills
            )

            return [documentation_work]
        elif completed_work.task.review_status == ReviewStatus.REQUIRES_MODIFICATION:
            # code can be a honeycomb after modifications -> perform modification and then do a documentation task
            chain = [CheckReusabilityMapper(modification_completed=True)] + completed_work.chain[1:]

            # create the new work item
            coding_work = Work(
                completed_work.task_id,
                WorkStatus.AVAILABLE,
                WorkType.OPEN_TASK,
                completed_work.task.review_feedback,
                {'code': code, 'context': new_context},
                chain,
                priority=completed_work.priority,
                tags=completed_work.tags,
                skills=completed_work.skills
            )

            return [coding_work]
        else:
            return []


    def get_init_params(self):
        return [self.modification_completed]
