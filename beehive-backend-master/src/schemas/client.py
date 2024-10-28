from ..utils.marshmallow import BeehiveSchemaMixin, ma

class ClientProjectResponseSchema(ma.Schema):
    id = ma.Integer()
    name = ma.String()
    trello_link = ma.String(data_key='trelloLink')

class ClientRepositoriesResponseSchema(ma.Schema, BeehiveSchemaMixin):
    id = ma.Integer()
    name = ma.String()
    url = ma.String()
    project = ma.Nested(ClientProjectResponseSchema)

