import enum
import requests

from flask import current_app

class CuckooEvent(int, enum.Enum):
    WORK_ACCEPTED = 1
    WORK_SOLVED = 2
    WORK_CANCELED = 3
    WORK_NEW_FEEDBACK = 4
    WORK_DESERTED = 5
    WORK_RESERVED = 8
    WORK_DISMISSED = 9
    WORK_PROHIBITED = 10
    WORK_UNPROHIBITED = 11
    NET_DURATION_UPDATED = 12
    TASK_DELEGATED = 13
    QUEST_DELEGATED = 14

def dispatch_cuckoo_event(task_id, event):
    res = requests.post(
        url=f'{current_app.config["CUCKOO_BASE_URL"]}/api/notification',
        headers={'X-CUCKOO-AUTH': current_app.config['CUCKOO_AUTH_TOKEN']},
        json={
            'taskId': task_id,
            'event': event
        }
    )

    if res.status_code != 200:
        current_app.logger.error(f'Error while notifying cuckoo service {res.text}')
        return False
    return True

def get_trello_card_link(task_ids):
    res = requests.post(
        url=f'{current_app.config["CUCKOO_BASE_URL"]}/api/v1/task',
        headers={'X-CUCKOO-AUTH': current_app.config['CUCKOO_AUTH_TOKEN']},
        json={
            'task_ids': task_ids
        }
    )

    if res.status_code != 200:
        current_app.logger.error(f'Error while fetching data from cuckoo service {res.text}')
        return []
    return res.json()['data']['links']

def get_card(beehive_id):
    res = requests.get(
        url=f'{current_app.config["CUCKOO_BASE_URL"]}/api/inner/v1/card/{beehive_id}',
        headers={'X-CUCKOO-AUTH': current_app.config['CUCKOO_AUTH_TOKEN']},
    )

    if res.status_code != 200:
        current_app.logger.error(f'Error while fetching data from cuckoo service {res.text}')
        return None
    return res.json()
