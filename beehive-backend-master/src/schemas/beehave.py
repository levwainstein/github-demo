
from ..utils.marshmallow import ma
from ..models.beehave_review import BeehaveReview

class BeehaveReviewSchema(ma.SQLAlchemySchema):
    class Meta:
        model = BeehaveReview

    review_content = ma.auto_field('review_content')