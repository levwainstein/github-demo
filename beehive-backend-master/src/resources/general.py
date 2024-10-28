from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.orm import joinedload

from ..schemas import EmptyResponseSchema
from ..schemas.general import ReportBugRequestSchema
from ..models.work import Work, WorkStatus
from ..models.work_record import WorkRecord
from ..utils.auth import activated_jwt_required
from ..utils.marshmallow import parser
from ..utils.slack_bot import notify_bug_report


class ReportBug(MethodView):
    @activated_jwt_required
    @parser.use_args(ReportBugRequestSchema(), as_kwargs=True)
    def post(self, task_id, details, source):
        user_id = get_jwt_identity()

        # notify bug report using slack bot
        notify_bug_report(user_id, task_id, details, source)

        return EmptyResponseSchema().jsonify()
