from ..utils.marshmallow import ma, BeehiveSchemaMixin

from ..models.skill import Skill


class SkillSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Skill

    id = ma.auto_field()
    name = ma.auto_field()


class SkillResponseSchema(SkillSchema, BeehiveSchemaMixin):
    pass
