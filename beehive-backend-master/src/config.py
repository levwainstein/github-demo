from datetime import timedelta
import datetime


class Config(object):
    DEBUG = False
    TESTING = False

    # path is relative to the execution directory
    LOG_FILE_PATH = 'beehive.log'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    CORS_ORIGINS = []

    RQ_QUEUES = ['high', 'low']

    # no trailing slash
    FRONTEND_BASE_URL = 'http://localhost:3000'

    PROMETHEUS_ENABLED = False

    INTER_SERVICE_AUTH_KEYS = []
    METRICS_AUTH_KEYS = []

    OUTGOING_AUTH_TOKEN = 'abcdefghijklmnopqrstuvwxyz'

    SLACK_BOT_BASE_URL = None

    CUCKOO_BASE_URL = 'http://localhost:8000'
    CUCKOO_AUTH_TOKEN = 'abcdefghijklmnopqrstuvwxyz'

    PRAESEPE_BASE_URL = 'http://localhost:5002'
    PRAESEPE_AUTH_TOKEN = 'abcdefghijklmnopqrstuvwxyz'

    POLLINATOR_TASK_TYPE_BASE_URL = 'http://localhost:5055'
    POLLINATOR_BEEHAVE_BASE_URL = 'http://localhost:5056'
    POLLINATOR_BEEHAVE_PR_FEEDBACK_URL = 'http://localhost:5057'

    # this should only be used for testing
    USER_REGISTRATION_OVERRIDE_CODE = None

    AWS_ACCESS_KEY = None
    AWS_SECRET_KEY = None
    AWS_REGION_NAME = None

    EMAIL_NOTIFICATION_ENABLED = False
    EMAIL_NOTIFICATION_SOURCE_ADDRESS = None
    EMAIL_NOTIFICATION_ADMIN_ADDRESS = None

    MAX_MODIFICATION_REQUESTS_FOR_REVIEW_CHAIN = 3

    SYSTEM_USER_ID = '00000000'

    UPWORK_CONSUMER_KEY = None
    UPWORK_CONSUMER_SECRET = None
    UPWORK_BEEHIVE_COMPANY_ID = None
    UPWORK_CALLBACK_URL = None

    CUCKOO_START_DATE = datetime.date(2023, 1, 1)

    BEEHIVE_AUTH_HEADER = None

    ROBOBEE_GRPC_SERVER_ADDRESS = None
    ROBOBEE_GRPC_OUTGOING_AUTH_KEY = None


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = None

    JWT_SECRET_KEY = None
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=60)

    RQ_REDIS_URL = None

    PROMETHEUS_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql://root@127.0.0.1/beehive'
    # SQLALCHEMY_DATABASE_URI = 'mysql://bee_backend_service:bee_backend_service@127.0.0.1/beehive'
    # SQLALCHEMY_ECHO = True

    JWT_SECRET_KEY = '98bottlesofbeeronthewall'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    RQ_REDIS_URL = 'redis://localhost:6379/0'
    # USER_REGISTRATION_OVERRIDE_CODE = 'fake-registration-code'

    INTER_SERVICE_AUTH_KEYS = ['abcdefghijklmnopqrstuvwxyz']

    UPWORK_LOCAL_MODE = True
    ROBOBEE_GRPC_SERVER_ADDRESS = 'localhost:50080'
    ROBOBEE_GRPC_OUTGOING_AUTH_KEY = 'fake-testing-robobee-key'



class TestingConfig(Config):
    DEBUG = True
    TESTING = True

    SQLALCHEMY_DATABASE_URI = 'mysql://bee_backend_service:bee_backend_service@127.0.0.1/beehive'

    JWT_SECRET_KEY = 'test'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=3)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=5)

    RQ_REDIS_URL = 'redis://localhost:6379/0'

    RQ_ASYNC = False

    INTER_SERVICE_AUTH_KEYS = [
        'fake-testing-inter-service-key'
    ]

    USER_REGISTRATION_OVERRIDE_CODE = 'fake-registration-code'

    MAX_MODIFICATION_REQUESTS_FOR_REVIEW_CHAIN = 1

    AWS_REGION_NAME = 'us-east-1'

    ROBOBEE_GRPC_SERVER_ADDRESS = 'localhost:50080'
    ROBOBEE_GRPC_OUTGOING_AUTH_KEY = 'fake-testing-robobee-key'

# map env names to configuration classes
config_map = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
