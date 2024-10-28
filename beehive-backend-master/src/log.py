import logging
from logging.handlers import RotatingFileHandler

from flask import Flask


class HealthCheckLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # filter out only if method is get, url starts with /health/
        # and status is 200
        return not (
            record.args.get('m') == 'GET'
            and (record.args.get('U') or '').startswith('/api/inner/v1/health/')
            and record.args.get('s') == '200'
        )


def init_app_logging(app: Flask) -> None:
    # if gunicorn logger is available (meaning it is running flask) add its
    # handlers to flask's logger so that all messages are directed to the same
    # places
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger.handlers:
        # remove default handler
        app.logger.removeHandler(app.logger.handlers[0])

        # add gunicorn logger handlers
        for h in gunicorn_logger.handlers:
            app.logger.addHandler(h)

        # add filter to prevent health check requests from being logged to the
        # access log
        logging.getLogger('gunicorn.access').addFilter(HealthCheckLogFilter())

    # log our messages to file
    handler = RotatingFileHandler(
        app.config['LOG_FILE_PATH'], maxBytes=1024 * 1024 * 5, backupCount=3
    )
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(
        logging.Formatter(
            '%(asctime)s [%(process)d] [%(levelname)s] %(message)s', '[%Y-%m-%d %H:%M:%S %z]'
        )
    )
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)

    # if we are running as an rq worker using the rq cli add the flask handlers
    # to the rq logger so messages are directed to the same handlers
    rq_worker_logger = logging.getLogger('rq.worker')
    if rq_worker_logger.handlers:
        for h in app.logger.handlers:
            rq_worker_logger.addHandler(h)
