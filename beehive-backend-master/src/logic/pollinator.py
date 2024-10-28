import requests

from flask import current_app

from ..models.task_classification import TaskClassification, TaskTypeClassification
from ..utils.db import db

def get_task_type_classification(task_id, description, skills):
    """
    Get a task type classification based on description and skills, updates database task_classification table with result
    Arguments:
        task_id - the id of task
        description - the description of task
        skills - list of a task skills
    Returns:
        None if there's no classification. Otherwise returns a TaskTypeClassification string value.
    """
    
    payload = {
        'input': {
            'task_description': description,
            'task_skills': [s.name for s in skills]
        }
    }

    res = requests.post(
        url=f'{current_app.config["POLLINATOR_TASK_TYPE_BASE_URL"]}/api/v1/predict',
        headers={'X-POLLINATOR-AUTH': current_app.config['OUTGOING_AUTH_TOKEN']},
        json=payload
    )
    if res.status_code != 200:
        current_app.logger.error(f'Error while trying to classify task {res.text}')
        return None

    data = res.json().get('data')
    task_type_label = data.get('label')
    task_type_code = TaskTypeClassification(task_type_label)

    task_classification = TaskClassification(task_id, task_type_code)
    db.session.add(task_classification)
    db.session.commit()

    return task_classification.task_type.value