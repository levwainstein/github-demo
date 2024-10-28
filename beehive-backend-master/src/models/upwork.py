from datetime import datetime, timedelta
import json

from sqlalchemy import ColumnElement
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.exc import NoResultFound

from ..utils.db import db, TimestampMixin


class WorkRecordUpworkDiary(db.Model):
    __tablename__ = 'work_record_upwork_diary'
    __table_args__ = (db.UniqueConstraint('work_record_id', 'upwork_diary_id', name='_work_record_upwork_diary_uc'),)

    id = db.Column(db.Integer(), primary_key=True)
    work_record_id = db.Column(db.Integer(), db.ForeignKey('work_record.id', ondelete='CASCADE'), nullable=False)
    upwork_diary_id = db.Column(db.Integer(), db.ForeignKey('upwork_diary.id'), nullable=False)
    net_duration_seconds = db.Column(db.Integer(), nullable=False)
    cost = db.Column(db.DECIMAL(precision=12, scale=2), nullable=True)
    upwork_duration_seconds = db.Column(db.Integer(), nullable=False)
    upwork_cost = db.Column(db.DECIMAL(precision=12, scale=2), nullable=True)

    work_record = db.relationship('WorkRecord', backref=db.backref('work_record_upwork_diaries', lazy='subquery', cascade='all,delete'), innerjoin=True, foreign_keys=[work_record_id])
    upwork_diary = db.relationship('UpworkDiary', backref=db.backref('work_record_upwork_diaries', lazy='subquery', cascade='all,delete'), innerjoin=True, foreign_keys=[upwork_diary_id])

    def __init__(self, work_record_id, upwork_diary_id, net_duration_seconds, cost, upwork_duration_seconds, upwork_cost):
        self.work_record_id = work_record_id
        self.upwork_diary_id = upwork_diary_id
        self.net_duration_seconds = net_duration_seconds
        self.cost = cost
        self.upwork_duration_seconds = upwork_duration_seconds
        self.upwork_cost = upwork_cost

    def __repr__(self):
        return f'<WorkRecordUpworkDiary work records {self.work_record_id} upwork diary {self.upwork_diary_id}>'

    @staticmethod
    def insert_or_update(work_record_id, upwork_diary_id, net_duration_seconds, work_record_cost, upwork_duration_seconds, upwork_cost):
        """
        Inserts a new WorkRecordUpworkDiary object or updates it if one exists (according to the unique index)
        Caller of the method must call db.session.commit() for the changes in this method to be saved to database
        """
        try:
            obj = WorkRecordUpworkDiary.query.filter_by(work_record_id=work_record_id, upwork_diary_id=upwork_diary_id).one()
            obj.net_duration_seconds = net_duration_seconds
            obj.cost = work_record_cost
            obj.upwork_duration_seconds = upwork_duration_seconds
            obj.upwork_cost = upwork_cost
        except NoResultFound:
            obj = WorkRecordUpworkDiary(
                work_record_id=work_record_id,
                upwork_diary_id=upwork_diary_id,
                net_duration_seconds=net_duration_seconds,
                cost=work_record_cost,
                upwork_duration_seconds=upwork_duration_seconds,
                upwork_cost=upwork_cost
            )
            db.session.add(obj)

        return obj


class UpworkDiary(TimestampMixin, db.Model):
    __table_args__ = (db.UniqueConstraint('upwork_user_id', 'start_time_epoch_ms', name='_upwork_diary_uc'),)

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(8), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True, index=True)
    upwork_user_id = db.Column(db.String(256), nullable=False, index=True)
    upwork_user_name = db.Column(db.String(256), nullable=False, index=True)
    start_time_epoch_ms = db.Column(db.BigInteger(), nullable=False)
    end_time_epoch_ms = db.Column(db.BigInteger(), nullable=False)
    duration_min = db.Column(db.Integer)
    description = db.Column(db.Text)

    user = db.relationship('User', backref=db.backref('upwork_records', lazy='select', cascade='all,delete'), innerjoin=True, foreign_keys=[user_id])

    def __init__(self, user_id, upwork_user_id, upwork_user_name, start_time_epoch_ms, end_time_epoch_ms, duration_min, description):
        self.user_id = user_id
        self.upwork_user_id = upwork_user_id
        self.upwork_user_name = upwork_user_name
        self.start_time_epoch_ms = start_time_epoch_ms
        self.end_time_epoch_ms = end_time_epoch_ms
        self.duration_min = duration_min
        self.description = description

    def __repr__(self):
        return f'<UpworkDiary {self.id}>'

    @staticmethod
    def insert_or_update(user_id, upwork_user_id, upwork_user_name, start_time_epoch_ms, end_time_epoch_ms, duration_min, description):
        """
        Inserts a new UpworkDiary object or updates it if one exists (according to the unique index)
        Caller of the method must call db.session.commit() for the changes in this method to be saved to database
        """
        try:
            obj = UpworkDiary.query.filter_by(upwork_user_id=upwork_user_id,start_time_epoch_ms=start_time_epoch_ms).one()
            obj.user_id = user_id
            obj.end_time_epoch_ms = end_time_epoch_ms
            obj.duration_min = duration_min
            obj.description = description
        except NoResultFound:
            obj = UpworkDiary(
                user_id,
                upwork_user_id,
                upwork_user_name,
                start_time_epoch_ms,
                end_time_epoch_ms,
                duration_min,
                description
            )
            db.session.add(obj)

        return obj

    @hybrid_property
    def utc_start_time(self) -> datetime:
        return datetime.utcfromtimestamp(self.start_time_epoch_ms / 1000)

    @utc_start_time.inplace.expression
    @classmethod
    def _utc_start_time(cls) -> ColumnElement[datetime]:
        return db.func.from_unixtime(cls.start_time_epoch_ms / 1000)

    @hybrid_property
    def utc_end_time(self) -> datetime:
        return datetime.utcfromtimestamp(self.end_time_epoch_ms / 1000)

    @utc_end_time.inplace.expression
    @classmethod
    def _utc_end_time(cls) -> ColumnElement[datetime]:
        return db.func.from_unixtime(cls.end_time_epoch_ms / 1000)

    ## upwork round start time to past 10-minute time
    @hybrid_property
    def rounded_utc_start_time(self) -> datetime:
        return (self.utc_start_time - timedelta(minutes=self.utc_start_time.minute % 10, seconds=0, microseconds=0)).replace(second=0, microsecond=0)

    @rounded_utc_start_time.inplace.expression
    @classmethod
    def _rounded_utc_start_time(cls) -> ColumnElement[datetime]:
        return db.func.from_unixtime(
            db.func.truncate(cls.start_time_epoch_ms / 1000 / 600, 0) * 600
        )

    ## upwork round end time to next 10-minute time
    @hybrid_property
    def rounded_utc_end_time(self) -> datetime:
        return (self.utc_end_time + timedelta(minutes=10 - self.utc_end_time.minute % 10, seconds=0, microseconds=0)).replace(second=0, microsecond=0)

    @rounded_utc_end_time.inplace.expression
    @classmethod
    def _rounded_utc_end_time(cls) -> ColumnElement[datetime]:
        return db.func.from_unixtime(
            db.func.ceil(cls.end_time_epoch_ms / 1000 / 600) * 600
        )

    @hybrid_property
    def duration_string(self) -> str:
        return f'{self.utc_start_time.strftime("%Y/%m/%d %H:%M")} - {self.utc_end_time.strftime("%Y/%m/%d %H:%M")}'

    @duration_string.inplace.expression
    @classmethod
    def _duration_string(cls) -> ColumnElement[str]:
        return db.func.concat(
            db.func.date_format(cls.utc_start_time, '%Y/%m/%d %H:%i'),
            ' - ',
            db.func.date_format(cls.utc_end_time, '%Y/%m/%d %H:%i')
        )

    @hybrid_property
    def upwork_duration_string(self) -> str:
        return f'{self.rounded_utc_start_time.strftime("%Y/%m/%d %H:%M")} - {self.rounded_utc_end_time.strftime("%Y/%m/%d %H:%M")}'

    @upwork_duration_string.inplace.expression
    @classmethod
    def _upwork_duration_string(cls) -> ColumnElement[str]:
        return db.func.concat(
            db.func.date_format(cls.rounded_utc_start_time, '%Y/%m/%d %H:%i'),
            ' - ',
            db.func.date_format(cls.rounded_utc_end_time, '%Y/%m/%d %H:%i')
        )


class UpworkAuthToken(TimestampMixin, db.Model):
    __table_args__ = (db.UniqueConstraint('access_token', 'refresh_token', 'token_type', 'expires_at', name='_upwork_auth_token_uc'),)

    id = db.Column(db.Integer(), primary_key=True)
    access_token = db.Column(db.String(64), nullable=False)
    refresh_token = db.Column(db.String(64), nullable=False)
    token_type = db.Column(db.String(64), nullable=False)
    expires_in = db.Column(db.BigInteger(), nullable=False)
    expires_at = db.Column(db.Float(), nullable=False)

    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        token_type: str,
        expires_in: int,
        expires_at: float
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires_in = expires_in
        self.expires_at = expires_at

    def __repr__(self):
        return f'<UpworkAuthToken {self.id}>'
    
    def toJSON(self):
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_type': self.token_type, 
            'expires_in': self.expires_in, 
            'expires_at': self.expires_at
        }

    @staticmethod
    def get_recent_token() -> str:
        recent_token = UpworkAuthToken.query.order_by(UpworkAuthToken.created.desc()).first()
        return recent_token.toJSON()

    @staticmethod
    def insert_or_update(access_token, refresh_token, token_type, expires_in, expires_at):
        """
        Inserts a new UpworkAuthToken object or updates it if one exists (according to the unique index)
        Caller of the method must call db.session.commit() for the changes in this method to be saved to database
        """
        try:
            obj = UpworkAuthToken.query.filter_by(access_token=access_token,refresh_token=refresh_token,token_type=token_type).one()
            obj.expires_at = expires_at
            obj.expires_in = expires_in
        except NoResultFound:
            obj = UpworkAuthToken(
                access_token,
                refresh_token,
                token_type,
                expires_in,
                expires_at
            )
        db.session.add(obj)
        return obj




