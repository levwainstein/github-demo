from flask import current_app

import requests

from ..utils.metrics import trigger_pollinator_exception
from ..utils.rq import rq


@rq.job('high', timeout=30, result_ttl=3600)
@trigger_pollinator_exception.count_exceptions()
def trigger_pollinator(url, payload):
    current_app.logger.info(f'trigger pollinator url {url} with payload "{payload}"')

    # send http request to pollinator url
    ALLOWED_STATUS_CODES = [200, 429]
    try:
        res = requests.post(
            url=url,
            headers={'X-POLLINATOR-AUTH': current_app.config['OUTGOING_AUTH_TOKEN']},
            json=payload
        )
        if res.status_code not in ALLOWED_STATUS_CODES:
            raise Exception(f'Error ({res.status_code}) {res.text} while trying to trigger polinator url {url} with param {payload} ')
    except Exception as e: 
        current_app.logger.error(f'failed to trigger pollinator: {str(e)}')