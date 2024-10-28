from flask.views import MethodView

from ..models.skill import Skill
from ..schemas.skill import SkillResponseSchema
from ..utils.auth import activated_jwt_required


class AvailableSkills(MethodView):
    # get all supported packages
    @activated_jwt_required
    def get(self):
        """
        Get all skills available
        """
        skills = Skill.query.all()
        return SkillResponseSchema(many=True).jsonify(skills)
