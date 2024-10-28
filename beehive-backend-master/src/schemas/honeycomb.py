from ..utils.marshmallow import BeehiveSchemaMixin, ma
from ..models.honeycomb import Honeycomb


class HoneycombSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Honeycomb

    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
    version = ma.auto_field()
    code = ma.auto_field()
    honeycomb_dependencies = ma.auto_field(data_key='honeycombDependencies')


class HoneycombResponseSchema(HoneycombSchema, BeehiveSchemaMixin):
    packages = ma.List(ma.String(), data_key='packages')
    all_honeycomb_dependencies = ma.Dict(keys=ma.Integer(), values=ma.String(), data_key='allHoneycombDependencies')
