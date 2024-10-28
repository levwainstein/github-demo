import enum
from typing import Optional

from ..utils.db import db, RandomStringIdMixin, TimestampMixin


class UserCodeType(int, enum.Enum):
    REGISTRATION = 1
    RESET_PASSWORD = 2


class UserCode(TimestampMixin, RandomStringIdMixin, db.Model):
    id = db.Column(db.String(64), primary_key=True)
    used = db.Column(db.Boolean(), nullable=False)
    expires = db.Column(db.DateTime(), nullable=True)
    code_type = db.Column(db.Enum(UserCodeType), nullable=False)
    user_id = db.Column(db.String(8), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True)

    user = db.relationship('User', backref=db.backref('user_codes', lazy='select'), innerjoin=True, foreign_keys=[user_id], cascade='all,delete')

    def __init__(
        self,
        code_type: UserCodeType,
        used: bool = False,
        expires: Optional[bool] = None,
        user_id: Optional[str] = None
    ):
        self.id = self._get_random_id()

        self.code_type = code_type
        self.used = used
        self.expires = expires
        self.user_id = user_id

    def __repr__(self):
        return f'<UserCode {self.id}>'
