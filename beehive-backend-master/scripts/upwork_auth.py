"""
Offline script to refresh upwork oauth2 token. 
Requires env variable UPWORK_CONSUMER_KEY, UPWORK_CONSUMER_SECRET, UPWORK_CALLBACK_URL

To run:
PYTHONPATH="$(pwd)/src:$PYTHONPATH" FLASK_ENV=development python scripts/upwork_auth.py
"""
import os
import upwork
from flask.config import Config

from src import config as app_config

config = Config(root_path=os.path.dirname(os.path.abspath(__file__)))
config.from_object(
    app_config.config_map.get(str(os.environ.get('FLASK_ENV') or 'default').lower())
)
config.from_envvar('BACKEND_CONFIG_FILE', silent=True)

config = upwork.Config(
    {
        "client_id": config['UPWORK_CONSUMER_KEY'],
        "client_secret": config['UPWORK_CONSUMER_SECRET'],
        "redirect_uri": config['UPWORK_CALLBACK_URL']
    }
)

client = upwork.Client(config)

try:
    config.token
except AttributeError:
    authorization_url, state = client.get_authorization_url()
    # cover "state" flow if needed
    authz_code = input(
        "Please enter the full callback URL you get "
        "following this link:\n{0}\n\n> ".format(authorization_url)
    )

    print("Retrieving access and refresh tokens.... ")
    token = client.get_access_token(authz_code)
    print(token)
