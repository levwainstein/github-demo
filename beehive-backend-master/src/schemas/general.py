from marshmallow.validate import Length

from ..utils.marshmallow import ma


class ReportBugRequestSchema(ma.Schema):
    task_id = ma.String(required=True, data_key='taskId')
    details = ma.String(required=True, validate=Length(min=1))
    source = ma.String(required=True)
