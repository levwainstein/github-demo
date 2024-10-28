import time

from flask_marshmallow import Marshmallow
from marshmallow import post_dump
from marshmallow.validate import Validator, ValidationError
from webargs.flaskparser import FlaskParser

from .errors import abort


ma = Marshmallow()
parser = FlaskParser()


@parser.error_handler
def handle_error(error, req, schema, error_status_code, error_headers):
    # return status 400 instead of webargs' default 422
    abort(400, description=error.messages.get('json') or error.messages.get('querystring') or '')


class BeehiveSchemaMixin(object):
    @post_dump(pass_many=True)
    def wrap_with_envelope(self, data, many, **kwargs):
        return {
            'status': 'ok',
            'data': data
        }


class TimeEpochMs(Validator):
    """Validator which succeeds if the value passed to it is within the specified
    range of time. If ``past_delta`` is not specified, or is specified as `None`,
    the lower bound would be 0. If ``max`` is not specified, or is specified as `None`,
    no upper bound exists.

    :param past_delta: The timedelta to subtract from the current time.
        If not provided, minimum value will be 0.
    :param max: The maximum value (upper bound). If not provided, maximum
        value will not be checked.
    """

    message_min = 'Can\'t be too far in the past'
    message_max = 'Must be less than {max}.'
    message_all = 'Can\'t be too far in the past and must be less than {max}.'

    def __init__(self, past_delta=None, max=None):
        if past_delta and type(past_delta).__name__ != 'timedelta':
            raise TypeError('past_delta must be a datetime.timedelta instance')

        self.past_delta = past_delta
        self.max = max

    def _repr_args(self):
        return 'past_delta={!r}, max={!r}'.format(
            self.past_delta, self.max, self.min_inclusive, self.max_inclusive
        )

    def _format_error(self, value, message):
        return message.format(input=value, past_delta=self.past_delta, max=self.max)

    def _min_value(self):
        return int((time.time() - self.past_delta.total_seconds()) * 1000)

    def __call__(self, value):
        if (self.past_delta is None and value < 0) or \
           (self.past_delta is not None and value < self._min_value()):
            message = self.message_min if self.max is None else self.message_all
            raise ValidationError(self._format_error(value, message))

        if self.max is not None and value > self.max:
            message = self.message_max if self.past_delta is None else self.message_all
            raise ValidationError(self._format_error(value, message))

        return value
