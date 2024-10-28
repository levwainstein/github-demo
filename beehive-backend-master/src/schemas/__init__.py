from ..utils.marshmallow import BeehiveSchemaMixin, ma


class EmptyResponseSchema(ma.Schema, BeehiveSchemaMixin):
    # add a no-argument overload
    def jsonify(self):
        return super(EmptyResponseSchema, self).jsonify(None)
