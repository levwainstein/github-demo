"""
Offline script to query upwork diaries in batches. Requires env variable BEEHIVE_AUTH_HEADER 
This endpoint is quite timely (times out for more than 7-10 days) so this script splits a date range into increments and downloads upwork diaries to db 

To run:
PYTHONPATH="$(pwd)/src:$PYTHONPATH" FLASK_ENV=development python scripts/requests_date_inc.py

"""

import os
from datetime import date, timedelta
import requests
from flask.config import Config

from src import config as app_config

config = Config(root_path=os.path.dirname(os.path.abspath(__file__)))
config.from_object(
    app_config.config_map.get(str(os.environ.get('FLASK_ENV') or 'default').lower())
)
config.from_envvar('BACKEND_CONFIG_FILE', silent=True)


def daterange(start_dt, end_dt, steps=1):
    """Yields dates in increments of steps days from startdate to enddate"""
    num_days = (end_dt-start_dt).days
    for x in range (0, num_days, steps):
        yield start_dt + timedelta(days = x)


start_date = date(2024, 4, 3)
end_date = date(2024, 4, 7)
# end_date = date(2023, 5, 3)
days_increment = 5

url = 'https://prod.bh.caas.ai/backend/api/v1/backoffice/upwork-diary'

numdays = (end_date-start_date).days 
start_dt = start_date
end_dt = start_date + timedelta(days = days_increment)
while start_dt <= end_date:
    print(f'Requesting for: {start_dt} - {end_dt}')
    print(f'---')

    res = requests.get(
        url,
        params = {
            'startDate': start_dt.strftime('%Y%m%d'),
            'endDate': end_dt.strftime('%Y%m%d')
        },
        headers = {
            'X-BEE-AUTH': config['BEEHIVE_AUTH_HEADER']
        }
    )
    if (res.status_code != 200):
        print(f'ERROR: {res.status_code} {res.text}')
        exit
    else:
        print(f'SUCCESS: {res.json()}')

    start_dt = start_dt + timedelta(days = days_increment+1)
    end_dt = min([end_dt + timedelta(days = days_increment+1), end_date])

