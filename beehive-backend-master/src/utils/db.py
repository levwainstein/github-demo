from datetime import datetime
import string

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .misc import generate_random_string


db = SQLAlchemy(session_options={'expire_on_commit': False})
migrate = Migrate()


class TimestampMixin(object):
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)


class RandomStringIdMixin(object):
    GET_RANDOM_ID_ATTEMPTS = 5

    def _get_random_id(self):
        model_class = type(self)
        if not model_class or \
            not hasattr(model_class, 'id') or \
            not hasattr(model_class.id, 'property') or \
            not isinstance(model_class.id.property, db.ColumnProperty) or \
            not isinstance(model_class.id.property.columns[0].type, db.String):
            raise Exception('no string id column available')

        # generate an available random id
        chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
        result = None
        attempt = 0
        while not result and attempt < RandomStringIdMixin.GET_RANDOM_ID_ATTEMPTS:
            attempt += 1
            random_id = generate_random_string(chars, model_class.id.property.columns[0].type.length)
            if model_class.query.filter_by(id=random_id).first() is None:
                result = random_id

        if not result:
            raise Exception(f'failed to find an available id over {RandomStringIdMixin.GET_RANDOM_ID_ATTEMPTS} attempts')

        return result
