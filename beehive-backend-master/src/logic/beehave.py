import requests

from flask import current_app

def beehave_review_pr(pr_url: str, work_description: str, previous_pr_sha: str = None):
    ALLOWED_STATUS_CODES = [200, 429]
    payload = {
        'input': {
            'pr_url': pr_url,
            'task_description': work_description,
            'previous_pr_commit_id': previous_pr_sha
        }
    }

    res = requests.post(
        url=f'{current_app.config["POLLINATOR_BEEHAVE_BASE_URL"]}/api/v1/predict',
        headers={'X-POLLINATOR-AUTH': current_app.config['OUTGOING_AUTH_TOKEN']},
        json=payload
    )
    if res.status_code != 200:
        current_app.logger.error(f'Error in requesting review from Beehave: {res.text}')
        return res.status_code if res.status_code in ALLOWED_STATUS_CODES else 500, ''

    return 200, res.json()


def run_beehave_pr_github_bot(pr_url, description):
    """
    Run asyncronassly the pollinator pr bot model based on description and pr url.
    The bot updates pr with review comments according to solution code.
    Arguments:
        description - the description of task
        pr_url - url of pull request to read the code changes from and add the review comments to
    Returns:
        success boolean: True on success, False on failure
    """
    payload = {
        'input': {
            'pr_url': pr_url,
            'task_description': description
        }
    }

    from ..jobs.pollinator import trigger_pollinator
    trigger_pollinator.queue(
        f'{current_app.config["POLLINATOR_BEEHAVE_PR_FEEDBACK_URL"]}/api/v1/predict',
        payload
    )
