import uuid

import bcrypt
from flask import current_app
from sqlalchemy import ColumnElement
from sqlalchemy.ext.hybrid import hybrid_property

from ..utils.db import db, RandomStringIdMixin, TimestampMixin
from .tag import UserTag
from .skill import UserSkill


class User(TimestampMixin, RandomStringIdMixin, db.Model):
    id = db.Column(db.String(8), primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True, index=True)
    hashed_password = db.Column(db.Text(), nullable=False)
    admin = db.Column(db.Boolean(), default=False, nullable=False)
    notifications = db.Column(db.Boolean(), default=False, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    github_user = db.Column(db.String(256))
    trello_user = db.Column(db.String(256))
    upwork_user = db.Column(db.String(256))
    availability_weekly_hours = db.Column(db.Integer())
    price_per_hour = db.Column(db.DECIMAL(precision=5, scale=2))
    price_per_hour_currency = db.Column(db.String(8))
    activated = db.Column(db.Boolean(), default=False, nullable=False)
    activation_token = db.Column(db.String(32), nullable=False, index=True)

    tags = db.relationship('Tag', secondary=UserTag.__table__, lazy='select', back_populates='users')
    skills = db.relationship('Skill', secondary=UserSkill.__table__, lazy='select', back_populates='users')

    def __init__(
        self, email, hashed_password, first_name, last_name, github_user, trello_user,
        availability_weekly_hours, price_per_hour, notifications, activation_token,
        upwork_user = None, tags=[], skills=[]
    ):
        self.id = self._get_random_id()

        self.email = email
        self.hashed_password = hashed_password
        self.first_name = first_name
        self.last_name = last_name
        self.notifications = notifications
        self.activation_token = activation_token
        self.github_user = github_user
        self.trello_user = trello_user
        self.availability_weekly_hours = availability_weekly_hours
        self.price_per_hour = price_per_hour
        self.price_per_hour_currency = 'usd'
        self.upwork_user = upwork_user
        self.tags = tags
        self.skills = skills


    def __repr__(self):
        return f'<User {self.id}>'

    @staticmethod
    def signup(
        email, password, first_name, last_name, github_user, trello_user, upwork_user,
        availability_weekly_hours, price_per_hour, notifications
    ):
        # check if email is already taken
        if User.query.filter(db.func.lower(User.email) == db.func.lower(email)).first():
            return None, 'email_exists', None

        hashed_password = User._hash_password(password)
        activation_token = uuid.uuid4().hex
        new_user = User(
            email, hashed_password, first_name, last_name, github_user, trello_user,
            availability_weekly_hours, price_per_hour, notifications, activation_token, upwork_user
        )

        # add and commit here since hashed_password should only be available inside this class
        db.session.add(new_user)
        db.session.commit()

        # success
        return new_user.id, None, activation_token

    @staticmethod
    def signin(email, password):
        user = User.query.filter(db.func.lower(User.email) == email.lower()).first()

        if not user:
            current_app.logger.warning(f'user login attempt with non existing email: {email}')
            return None, False, False

        if user.id == current_app.config['SYSTEM_USER_ID']:
            current_app.logger.warning(f'user login attempt with system user email: {email}')
            return None, False, False

        if not bcrypt.checkpw(password.encode('utf8'), user.hashed_password.encode('utf-8')):
            current_app.logger.warning(f'user login attempt with bad password for email: {email}')
            return None, False, False

        # success (return field values instead of the entire object to avoid leaking data)
        return user.id, user.admin, user.activated

    def change_password(self, new_password: str):
        self.hashed_password = User._hash_password(new_password)

    @staticmethod
    def _hash_password(password: str):
        return bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

    @hybrid_property
    def name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    @name.inplace.expression
    @classmethod
    def _name(cls) -> ColumnElement[str]:
        return db.func.concat(cls.first_name,' ',cls.last_name)

    @hybrid_property
    def utc_last_engagement(self) -> int:
        if not self.work_records:
            return None
        return max([wr.utc_end_time for wr in self.work_records if wr.utc_end_time])

    @utc_last_engagement.inplace.expression
    @classmethod
    def _utc_last_engagement(cls) -> ColumnElement[int]:
        from .work_record import WorkRecord

        return db.select(WorkRecord.utc_end_time) \
            .where(cls.id == WorkRecord.user_id) \
            .order_by(WorkRecord.utc_end_time.desc()) \
            .limit(1).scalar_subquery()
