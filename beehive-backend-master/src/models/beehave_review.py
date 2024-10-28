from ..utils.db import db, TimestampMixin

class BeehaveReview(TimestampMixin, db.Model):
    __tablename__ = 'beehave_review'

    id = db.Column(db.Integer(), primary_key=True)  # sqlalchemy sets only-primary-key-integer field to auto increments
    work_record_id = db.Column(db.Integer, db.ForeignKey('work_record.id'), nullable=False, index=True)
    review_content = db.Column(db.JSON)
    last_commit_sha = db.Column(db.String(64))

    work_record = db.relationship('WorkRecord', backref=db.backref('beehave_reviews', lazy='select', cascade='all,delete'), innerjoin=True)

    def __repr__(self):
        return f'<BeehaveReview {self.id}>'
