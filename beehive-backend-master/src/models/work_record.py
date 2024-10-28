from datetime import datetime
import enum
from typing import Optional

from flask import current_app
from sqlalchemy import ColumnElement
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from .user import User
from ..utils.db import db, TimestampMixin

from ..logic.praesepe import get_rating_items


class SolutionRating(int, enum.Enum):
    INADEQUATE = 1
    REQUIRES_MODIFICATION = 2
    ADEQUATE = 3


class WorkOutcome(int, enum.Enum):
    REQUESTED_PACKAGE = 1
    FEEDBACK = 2
    SOLVED = 3
    CANCELLED = 4
    SKIPPED = 5
    TASK_CANCELLED = 6


class WorkRecord(TimestampMixin, db.Model):
    id = db.Column(db.Integer(), primary_key=True)  # sqlalchemy sets only-primary-key-integer field to auto increments
    user_id = db.Column(db.String(8), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    work_id = db.Column(db.Integer, db.ForeignKey('work.id'), nullable=False, index=True)
    active = db.Column(db.Boolean, nullable=False)
    start_time_epoch_ms = db.Column(db.BigInteger(), nullable=False)
    tz_name = db.Column(db.String(48), nullable=False)  # current max time zone name length is 32 but unsure if that is the limit
    duration_seconds = db.Column(db.Integer)
    feedback = db.Column(db.Text())
    solution_rating = db.Column(db.Enum(SolutionRating))
    solution_feedback = db.Column(db.Text())
    force_submit_reason = db.Column(db.Text())
    solution_url = db.Column(db.Text())
    outcome = db.Column(db.Enum(WorkOutcome))
    review_start_time_epoch_ms = db.Column(db.BigInteger(), nullable=True)
    review_tz_name = db.Column(db.String(48), nullable=True)
    review_duration_seconds = db.Column(db.Integer, nullable=True)
    review_user_id = db.Column(db.String(8), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True, index=True)

    work = db.relationship('Work', backref=db.backref('work_records', lazy='select', cascade='all,delete'), innerjoin=True)
    user = db.relationship('User', backref=db.backref('work_records', lazy='select', cascade='all,delete'), innerjoin=True, foreign_keys=[user_id])


    def __init__(self, user_id, work_id, active, start_time_epoch_ms, tz_name, outcome=None):
        self.user_id = user_id
        self.work_id = work_id
        self.active = active
        self.start_time_epoch_ms = start_time_epoch_ms
        self.tz_name = tz_name
        self.outcome = outcome

    def __repr__(self):
        return f'<WorkRecord {self.id}>'
    
    @hybrid_property
    def utc_start_time(self) -> datetime:
        return datetime.utcfromtimestamp(self.start_time_epoch_ms / 1000)

    @utc_start_time.inplace.expression
    @classmethod
    def _utc_start_time(cls) -> ColumnElement[datetime]:
        return db.func.from_unixtime(cls.start_time_epoch_ms / 1000)

    @hybrid_property
    def utc_end_time(self) -> Optional[datetime]:
        if not self.duration_seconds:
            return None

        return datetime.utcfromtimestamp(self.start_time_epoch_ms / 1000 + self.duration_seconds)

    @utc_end_time.inplace.expression
    @classmethod
    def utc_end_time(cls) -> ColumnElement[Optional[str]]:
        if (cls.duration_seconds is None) is True:
            return None

        return db.func.from_unixtime(cls.start_time_epoch_ms / 1000 + cls.duration_seconds)

    @hybrid_method
    def start_time_diff_sec(self, other) -> int:
        return int((other - self.utc_start_time).total_seconds())

    @start_time_diff_sec.inplace.expression
    @classmethod
    def _start_time_diff_sec(cls, other) -> ColumnElement[int]:
        return db.func.abs(
            db.func.timestampdiff(
                db.text('SECOND'),
                other,
                cls.utc_start_time
            )
        )

    @hybrid_method
    def end_time_diff_sec(self, other) -> int:
        return int((other - self.utc_end_time).total_seconds())

    @end_time_diff_sec.inplace.expression
    @classmethod
    def _end_time_diff_sec(cls, other) -> ColumnElement[int]:
        return db.func.abs(
            db.func.timestampdiff(
                db.text('SECOND'),
                other,
                cls.utc_end_time
            )
        )

    @hybrid_property
    def user_name(self) -> str:
        return self.user.name

    @user_name.inplace.expression
    @classmethod
    def _user_name(cls) -> ColumnElement[str]:
        return db.select(User.name).where(cls.user_id == User.id).scalar_subquery()
    
    @property
    def rating_object_key(self):
        return f'wr-{self.id}'
    
    @property
    def solution_review_url(self):
        return f'{current_app.config["FRONTEND_BASE_URL"]}/redirect?workRecordId={self.id}'
    
    def get_ratings(self):
        target_user = self.user_id,
        object_key = self.rating_object_key

        ratings = get_rating_items(target_user, [object_key])
        return ratings
