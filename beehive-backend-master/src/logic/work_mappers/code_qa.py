import time
from flask import current_app

from .base import BaseWorkMapper

from ...models.work import Work, WorkStatus, WorkType
from ...models.task import ReviewStatus
from ...models.skill import Skill


QA_SKILL = 'qa_tasks'

DEFAULT_QA_DESCRIPTION_PREFIX = '1. Run locally the PR, review it and compare it to the requirements below.\n' \
    '2. Identify any functionality or design gaps.\n' \
    '\t2.a. For design gaps, pay special attention to font types and sizes, margins, colors, and how well they match the Figma below.\n' \
    '\t2.b. For functionality gaps, make sure the code runs smoothly without bugs or glitches.\n' \
    '3. Take a screenshot or video recording of the issues. If you take a screenshot, please highlight the gaps in red. If you do a video, please use the mouse cursor to highlight specific issues and if you can also narrate what the issue is.\n' \
    '4. Upload the file to the PR conversation.\n' \
    '5. Write a comment in the conversation that lists:\n' \
    '\t5.a. An enumerated list of each of the issues you found.\n' \
    '\t5.b. The total time you spent on setup time, QA time, annotation, and feedback time. By the way, if you find any issues that are not directly related to the PR, please let us know via Upwork about them.\n' \
    '6. Share the link and a brief summary of the issues in the feedback report.\n' \
    'Note: DO NOT open a new PR - your goal is to use the existing PR below.\n'

DEFAULT_QA_ITERATIONS = 3

class CodeQAMapper(BaseWorkMapper):
    """
    This mapper is used both for creating a chain of qa work for coding tasks that require it 
    and for adding sequential coding work after qa work has been done
    """

    def __init__(self, chain_work_description, remaining_chain_count):
        self.chain_work_description = chain_work_description
        self.remaining_chain_count = remaining_chain_count

    def map_work(self, completed_work, completed_work_record):
        if completed_work.work_type not in (WorkType.CUCKOO_CODING, WorkType.CUCKOO_ITERATION, WorkType.CUCKOO_QA):
            current_app.logger.error(f'work id {completed_work.id} chained CommunityQAMapper but has type {str(completed_work.work_type)}')
            return None

        if completed_work.status != WorkStatus.COMPLETE:
            current_app.logger.error(f'work id {completed_work.id} chained CommunityQAMapper but has status {str(completed_work.status)}')
            return None

        # Chain has completed by count depletion
        if self.remaining_chain_count == 0:
            return []

        # QA rated original solution as adequate
        if completed_work.work_type == WorkType.CUCKOO_QA and completed_work.task.review_status == ReviewStatus.ADEQUATE:
            return []

        # QA rated original solution as not good enough and needs to be coded again
        if completed_work.work_type == WorkType.CUCKOO_QA and completed_work.task.review_status == ReviewStatus.INADEQUATE:

            # create new coding task with qa chain that is reserved for original contributor for limited time with initiated qa chain
            description = f'Please see QA remarks {completed_work.task.review_feedback or "in pull request"}\n\n**Pull request: [{completed_work.work_input["solution_url"]}]({completed_work.work_input["solution_url"]})**\n\n---\n\n**Original Task:**\n{completed_work.task.description}'
            chain = [
                CodeQAMapper(
                    chain_work_description=self.chain_work_description,
                    remaining_chain_count=self.remaining_chain_count
                )
            ] + completed_work.chain[1:]
            
            qa_skill = Skill.get_or_create(QA_SKILL)
            completed_work_skills_without_qa = completed_work.skills
            if qa_skill in completed_work.skills:
                completed_work_skills_without_qa.remove(qa_skill)

            subsequent_work = Work(
                completed_work.task_id,
                WorkStatus.AVAILABLE,
                WorkType.CUCKOO_CODING,
                description,
                work_input=completed_work.work_input,
                chain=chain,
                priority=completed_work.priority,
                tags=completed_work.tags,
                skills=completed_work_skills_without_qa
            )
            subsequent_work.reserved_worker_id = completed_work.work_input['user_id']
            subsequent_work.reserved_until_epoch_ms = int(time.time() * 1000) + 4 * 60 * 60 * 1000
            
            return [subsequent_work]
        
        # if the work solved was not QA work, but regular coding work instantiate qa chain
        if completed_work.work_type in (WorkType.CUCKOO_CODING, WorkType.CUCKOO_ITERATION):
            description = f'{self.chain_work_description}\n\n---\n\n**Original Task:**\n{completed_work.task.description}'
            work_input = {'solution_url': completed_work_record.solution_url, 'user_id': completed_work_record.user_id, 'work_record_id': completed_work_record.id}

            chain = [
                CodeQAMapper(
                    self.chain_work_description,
                    self.remaining_chain_count - 1
                )
            ] + completed_work.chain[1:]

            # update task that this is the last review (for extension view)
            if self.remaining_chain_count == 1:
                completed_work.task.review_completed = True

            qa_skill = Skill.get_or_create(QA_SKILL)
            completed_work_skills_with_qa = completed_work.skills
            if qa_skill not in completed_work.skills:
                completed_work_skills_with_qa = completed_work_skills_with_qa + [qa_skill]

            # create the new work item
            qa_work = Work(
                completed_work.task_id,
                WorkStatus.AVAILABLE,
                WorkType.CUCKOO_QA,
                description,
                work_input,
                chain,
                priority=completed_work.priority,
                tags=completed_work.tags,
                skills=completed_work_skills_with_qa
            )
            qa_work.prohibited_worker_id = completed_work_record.user_id

            return [qa_work]

        return []
    
    def get_init_params(self):
        return [
            self.chain_work_description,
            self.remaining_chain_count
        ]
