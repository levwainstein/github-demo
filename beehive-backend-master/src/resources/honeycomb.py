from flask import current_app
from flask.views import MethodView
from sqlalchemy.orm import joinedload

from ..models.honeycomb import Honeycomb
from ..schemas.honeycomb import HoneycombResponseSchema
from ..utils.auth import activated_jwt_required


class HoneycombCRUD(MethodView):
    @activated_jwt_required
    def get(self):
        current_app.logger.info(f'Getting honeycombs')

        honeycombs = Honeycomb.query.options(
            joinedload(Honeycomb.honeycomb_dependencies)
        ).all()

        for honeycomb in honeycombs:
            honeycomb_dependencies = honeycomb.get_dependencies()
            honeycomb.all_honeycomb_dependencies = {dependency.id: dependency.name for dependency in honeycomb_dependencies}

        return HoneycombResponseSchema(many=True).jsonify(honeycombs)
