from datetime import datetime

from ..utils.db import db


class RevokedToken(db.Model):
    id = db.Column(db.Integer(), primary_key=True)  # sqlalchemy sets only-primary-key-integer field to auto increments
    token_id = db.Column(db.String(36), nullable=False, index=True)  # using flask-jwt-extended jti-s are (undocumentdatly) uuids, and so 36 characters long
    user_id = db.Column(db.String(8), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    revoked = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('revoked_tokens', lazy='select', cascade='all,delete'), innerjoin=True, foreign_keys=[user_id])

    def __init__(self, token_id, user_id):
        self.token_id = token_id
        self.user_id = user_id

    def __repr__(self):
        return f'<RevokedToken {self.id}>'
