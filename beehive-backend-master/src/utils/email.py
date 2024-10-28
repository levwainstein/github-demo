import json
from flask import current_app


def _send_email(user_id, email_type, subject, body):
    from ..jobs.email import user_send_email
    if current_app.config['EMAIL_NOTIFICATION_ENABLED'] and \
       user_id != current_app.config['SYSTEM_USER_ID']:
        user_send_email.queue(
            user_id,
            email_type,
            subject,
            body
        )


def _send_admin_email(email_type, subject, body):
    from ..jobs.email import admin_send_email
    if current_app.config['EMAIL_NOTIFICATION_ENABLED']:
        admin_send_email.queue(
            email_type,
            subject,
            body
        )


def send_task_solved_email(task):
    _send_email(
        task.delegating_user_id,
        'task_solved',
        'Your Beehive task was just solved',
        f'<html><body><h4>Your task <u>{task.name}</u> ({task.id}) was just solved!</h4><p>The solution awaits you @ Beehive</p></body></html>'
    )


def send_task_error_email(task):
    _send_email(
        task.delegating_user_id,
        'task_error',
        'Your Beehive task was not created',
        f'<html><body><h4>An error occurred while preparing your task <u>{task.name}</u> ({task.id})</h4><p>The error is: <pre><i>{task.invalid_code}: {task.invalid_description}</i></pre></p><p>More info is available @ Beehive</p></body></html>'
    )


def send_task_feedback_email(task):
    _send_email(
        task.delegating_user_id,
        'task_feedback',
        'Your Beehive task just got some feedback',
        f'<html><body><h4>Your task <u>{task.name}</u> ({task.id}) just got some feedback</h4><p>The feedback is: <pre><i>{task.feedback}</i></pre></p><p>More info is available @ Beehive</p></body></html>'
    )


def send_work_deserted_email(user_id, work_record):
    _send_email(
        user_id,
        'work_deserted',
        'Your Beehive task was deserted',
        f'<html><body><h4>Your task <u>{work_record.work.task.name}</u> ({work_record.work.task.id}) just got deserted and will go back to the tasks queue</h4><p>contributor: <pre><i>{work_record.user_id}</i></pre></p><p>Time spent {"{:02}:{:02}:{:02}".format(work_record.duration_seconds//3600, work_record.duration_seconds%3600//60, work_record.duration_seconds%60)}</p></body></html>'
    )


def send_contributor_task_cancelled_email(user_id, task):
    _send_email(
        user_id,
        'task_cancelled',
        'Your Beehive task was just cancelled',
        f'<html><body><h4>Your task <u>{task.name}</u> ({task.id}) was just cancelled!</h4><p>Please pick another task from <a href="{current_app.config["FRONTEND_BASE_URL"]}>our portal</a></p></body></html>'
    )


def send_contributor_work_deserted_email(user, work):
    email_body = f'<html><body><h4>Hi, there is work that needs your attention on Beehive.</h4>'

    email_body += '<p>This work has been held for too long:'

    # add links to the specific work requested by the delegator
    email_body += f'<li><a href="{current_app.config["FRONTEND_BASE_URL"]}/?workId={work.id}">{work.task.name}</a></li></p>'

    email_body += '<p>Please note that the tasks are designed to be completed in 10h, after that they are freed for other developers to solve. Please contact our team asap if you\'d like to continue working on this task.</p></body></html>'

    _send_email(
        user.id,
        'contributor_work_deserted',
        'Your Beehive task was canceled',
        email_body
    )


def send_contributor_work_pre_deserted_email(user, work, task_notification_hours=2, task_deadline_hours=10):
    email_body = f'<html><body><h4>Hi, there is work that needs your attention on Beehive.</h4>'

    email_body += f'<p>This work is due in {task_notification_hours} hours:'

    # add links to the specific work requested by the delegator
    email_body += f'<li><a href="{current_app.config["FRONTEND_BASE_URL"]}/?workId={work.id}">{work.task.name}</a></li></p>'

    email_body += f'<p>Please note that the tasks are designed to be completed in {task_deadline_hours} hours, after that they are freed for other developers to solve. Please contact our team asap if you\'d like to continue this task.</p></body></html>'

    _send_email(
        user.id,
        'contributor_work_pre_deserted',
        'Your Beehive task will be cancelled soon',
        email_body
    )


def send_contributors_task_update_email(user_id, work):
    _send_email(
        user_id,
        'feedback_task',
        'Your Beehive task was just updated',
        f'<html><body><h4>Your task <u>{work.task.name}</u> has some more details!</h4><p>Please proceed to <a href="{current_app.config["FRONTEND_BASE_URL"]}/?workId={work.id}">the task page in our portal</a> for all details</p></body></html>'
    )

def send_contributor_task_modifications_email(user_id, work):
    email_body = f'<html><body><h4>Hi, You got a PR review for your task solved on Beehive.</h4>'

    if work:
        email_body += '<p>Please fix according to the changes pull request url in the task description: <ul>'
        email_body += f'<li><a href="{current_app.config["FRONTEND_BASE_URL"]}/?workId={work.id}">{work.task.name}</a></li>'
        email_body += '</p>'

    _send_email(
        user_id,
        'modifications_task',
        'Your Beehive solution requires modifications',
        f'<html><body><h4>Your task <u>{work.task.name}</u> got reviewed.</h4><p>Please modify solution according to pull request comments detailed in the <a href="{current_app.config["FRONTEND_BASE_URL"]}/?workId={work.id}">task in our portal</a></p></body></html>'
    )

def send_contributors_notification_email(users, work):
    email_body = f'<html><body><h4>Hi, there is more work that needs your attention on Beehive.</h4>'

    if work:

        email_body += '<p>Important tasks include: <ul>'

        # add links to the specific work requested by the delegator
        for work_item in work:
            email_body += f'<li><a href="{current_app.config["FRONTEND_BASE_URL"]}/?workId={work_item.id}">{work_item.task.name}</a></li>'

        email_body += '</ul></p>'

    email_body += '<p>Please note that the tasks are available to other engineers and may become unavailable at any time.</p></body></html>'

    for user in users:
        _send_email(
            user.id,
            'new_task',
            'New Beehive tasks',
            email_body
        )


def send_user_activation_email(user_id, activation_url):
    _send_email(
        user_id,
        'account_activation',
        'Welcome to Beehive!',
        f'<html><body><h4>Welcome to Beehive!</h4><p>Activate your account by clicking the link below or by copying it and pasting in your browser -</p><a href="{activation_url}">{activation_url}</a><p>If you are having issues with activation don\'t hesitate to contact us ♥</p></body></html>'
    )


def send_user_reset_password_email(user_id, reset_url):
    _send_email(
        user_id,
        'reset_password',
        'Reset your Beehive Password',
        f'<html><body><h4>Reset your Beehive Password</h4><p>We received a request to reset the password associated with this email address. If you didn\'t initiate this request no harm was done and you can safely ignore this email.</p><p>If, however, it was you who requested your password be changed, click the link below or copy and paste it in your browser -</p><a href="{reset_url}">{reset_url}</a><p>Note that the link above is only valid for 24 hours, please use it before it expires.</p><p>If you are having issues with accessing your account don\'t hesitate to contact us ♥</p></body></html>'
    )


def send_admin_unrecognized_users_email(data:list[dict]=None):
    email_body = f'<html><body><h4>Hi, These are upwork freelancers that do not match a beehive profile.</h4>'

    if data:
        email_body += '<p><ul>'
        for d in data:
            dict_html = json.dumps(d, indent=4).replace(",\n", ",<br>").replace("\n", "<br>")
            email_body += f'<li>{dict_html}</li>'
        email_body += '</ul></p>'

    email_body += '<p>Please update corresponding beehive user profiles with their upwork user.</p></body></html>'

    _send_admin_email(
        'unrecognized_upwork_alert',
        'Unrecognized upwork freelancers alert',
        email_body
    )
