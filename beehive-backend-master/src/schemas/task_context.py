from ..utils.marshmallow import BeehiveSchemaMixin, ma


class TaskContextResponseSchema(ma.SQLAlchemySchema, BeehiveSchemaMixin):
    id = ma.String(required=True)
    file = ma.String(required=True)
    entity = ma.String(required=True)
    potential_use = ma.String(data_key='potentialUse')


class TaskContextRequestSchema(ma.Schema):
    file = ma.String(required=True)
    entity = ma.String(required=True)
    potential_use = ma.String(required=True, data_key='potentialUse')

