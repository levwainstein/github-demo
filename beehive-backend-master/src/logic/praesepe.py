import enum

from flask import current_app
import requests

from ..models.task import TaskStatus
from ..models.work import WorkStatus, WorkType


class RatingSubject(enum.Enum):
    WORK_DESCRIPTION = 1
    WORK_SOLUTION_MATCH_REQUIREMENTS = 2
    WORK_SOLUTION_CODE_QUALITY = 3
    WORK_REVIEW_QA_FUNCTIONALITY = 4
    WORK_REVIEW_CODE_QUALITY = 5

def get_praesepe_authorization_code(target_user_id, object_key, subjects, user_id=None):
    params = {
        'targetUser': target_user_id,
        'objectKey': object_key,
        'subjects': subjects
    }

    if user_id:
        params['user'] = user_id

    res = requests.post(
        url=f'{current_app.config["PRAESEPE_BASE_URL"]}/api/v1/auth',
        headers={'X-PRAESEPE-AUTH': current_app.config['PRAESEPE_AUTH_TOKEN']},
        json=params
    )

    if res.status_code != 200:
        current_app.logger.error(f'Error while retrieving praesepe authorization key {res.text}')
        return None

    authorization_code = res.json()['data']['code']
    return authorization_code


def get_rating_subjects(work):
    if work.work_type in [WorkType.CUCKOO_QA]:
        # rating for delegator for last qa iteration
        if work.task.status == TaskStatus.SOLVED:
            return [RatingSubject.WORK_REVIEW_CODE_QUALITY.name.lower(), RatingSubject.WORK_REVIEW_QA_FUNCTIONALITY.name.lower()]
        # rating for qa contributor to rate coding contributor
        elif work.status == WorkStatus.UNAVAILABLE:
            return [RatingSubject.WORK_SOLUTION_MATCH_REQUIREMENTS.name.lower()]
        # rating for available qa work
        elif work.status == WorkStatus.AVAILABLE:
            return [RatingSubject.WORK_DESCRIPTION.name.lower()]

    # rating for work that hasn't been solved
    if work.status in [WorkStatus.AVAILABLE, WorkStatus.UNAVAILABLE]:
        return [RatingSubject.WORK_DESCRIPTION.name.lower()]

    # rating for delegator to rate coding work
    if work.status == WorkStatus.COMPLETE:
        return [RatingSubject.WORK_SOLUTION_CODE_QUALITY.name.lower(), RatingSubject.WORK_SOLUTION_MATCH_REQUIREMENTS.name.lower()]


def get_rating_items(target_user, object_keys, user=None):
    params = {
        'targetUser': target_user,
        'objectKeys': object_keys
    }

    if user:
        params['user'] = user

    res = requests.get(
        url=f'{current_app.config["PRAESEPE_BASE_URL"]}/api/v1/rating',
        headers={'X-PRAESEPE-AUTH': current_app.config['PRAESEPE_AUTH_TOKEN']},
        params=params
    )

    if res.status_code == 400:
        current_app.logger.info(f'No ratings found for object [{object_keys}] by user [{user}] for user [{target_user}].')
        return None
    elif res.status_code != 200:
        current_app.logger.error(f'Error {res.status_code} while retrieveing rating for object [{object_keys}] by user [{user}] for user [{target_user}]: {res.text}')
        return None

    ratings = res.json()['data']
    return ratings
