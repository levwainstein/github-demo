from flask import current_app
import json

from .base import BaseWorkMapper

from ...models.work import Work, WorkStatus, WorkType
from ...models.task import ReviewStatus
from .code_review import CodeReviewMapper


class CodeModificationMapper(BaseWorkMapper):
    def __init__(self, original_work_type, remaining_modifications_count):
        self.original_work_type = original_work_type
        self.remaining_modifications_count = remaining_modifications_count

    def map_work(self, completed_work, completed_work_record):
        if completed_work.work_type != WorkType.REVIEW_TASK:
            current_app.logger.error(f'work id {completed_work.id} chained CodeModificationMapper but has type {str(completed_work.work_type)}')
            return None

        if completed_work.status != WorkStatus.COMPLETE:
            current_app.logger.error(f'work id {completed_work.id} chained CodeModificationMapper but has status {str(completed_work.status)}')
            return None

        if completed_work.task.review_status == ReviewStatus.ADEQUATE:
            return None

        # handle the case where the solution is not good enough and needs to be resolved from scratch,
        # or more modifications are needed and then we do another review
        if completed_work.task.review_status == ReviewStatus.INADEQUATE:
            description = completed_work.task.description
            work_input = {'code': completed_work.task.original_code, 'context': json.loads(completed_work.task.context)}
        else:
            description = f'Modifications requested: {completed_work.task.review_feedback}\n\nOriginal task description: {completed_work.task.description}'
            work_input = {'code': completed_work.task.solution_code, 'context': completed_work.work_input['context']}

        if self.remaining_modifications_count > 0:
            chain = [
                CodeReviewMapper(), 
                CodeModificationMapper(self.original_work_type, self.remaining_modifications_count - 1)
            ] + completed_work.chain[1:]

            # update task that this is the last review (for extension view)
            if self.remaining_modifications_count == 1:
                completed_work.task.review_completed = True

            # create the new work item
            coding_work = Work(
                completed_work.task_id,
                WorkStatus.AVAILABLE,
                self.original_work_type,
                description,
                work_input,
                chain,
                priority=completed_work.priority,
                tags=completed_work.tags,
                skills=completed_work.skills
            )

            return [coding_work]
        
        return []

    def get_init_params(self):
        return [
            self.original_work_type,
            self.remaining_modifications_count
        ]
