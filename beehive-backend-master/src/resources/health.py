from flask import current_app
from flask.views import MethodView

from ..schemas import EmptyResponseSchema
from ..utils.db import db
from ..utils.errors import abort


class Live(MethodView):
    def get(self):
        return EmptyResponseSchema().jsonify()


class Ready(MethodView):
    def get(self):
        try:
            # check if db connection is successful
            db.session.connection()

            return EmptyResponseSchema().jsonify()
        except Exception as ex:
            current_app.logger.error('health check failed: %s', str(ex))
            abort(500)
