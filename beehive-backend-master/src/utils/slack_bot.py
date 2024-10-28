from flask import current_app
from requests import post as requests_post


def notify_new_task_description(task):
    # notify new description if base url is set
    if current_app.config.get('SLACK_BOT_BASE_URL'):
        try:
            res = requests_post(
                f'{current_app.config["SLACK_BOT_BASE_URL"]}/notify/description',
                json={
                    'taskId': task.id,
                    'description': task.description,
                    'funcName': task.func_name,
                    'taskType': task.task_type.name,
                    'delegatorId': task.delegating_user_id,
                }
            )

            if res.status_code == 200:
                current_app.logger.info('notified new description')
            else:
                current_app.logger.warning('failed to notify new description')
        except Exception as ex:
            current_app.logger.error('failed to notify new description with exception: %s', str(ex))


def notify_bug_report(user_id, task_id, details, source):
    # notify bug report if base url is set
    if current_app.config.get('SLACK_BOT_BASE_URL'):
        try:
            res = requests_post(
                f'{current_app.config["SLACK_BOT_BASE_URL"]}/notify/bug',
                json={
                    'userId': user_id,
                    'taskId': task_id,
                    'details': details,
                    'source': source
                }
            )

            if res.status_code == 200:
                current_app.logger.info('notified bug report')
            else:
                current_app.logger.warning('failed to notify bug report')
        except Exception as ex:
            current_app.logger.error('failed to notify bug report with exception: %s', str(ex))


def notify_user_profile_change(user_id, column, previous_value, new_value):
    # notify hourly rate change
    if current_app.config.get('SLACK_BOT_BASE_URL'):
        try:
            res = requests_post(
                f'{current_app.config["SLACK_BOT_BASE_URL"]}/notify/user_profile',
                json={
                    'column': column,
                    'userId': user_id,
                    'previousValue': previous_value,
                    'newValue': new_value
                }
            )
            if res.status_code == 200:
                current_app.logger.info(f'notified profile {column} change from {previous_value} to {new_value} about user {user_id}')
            else:
                current_app.logger.warning(f'failed to notify profile {column} change from {previous_value} to {new_value} about user {user_id}')
        except Exception as ex:
            current_app.logger.error('failed to notify profile change with exception: %s', str(ex))
