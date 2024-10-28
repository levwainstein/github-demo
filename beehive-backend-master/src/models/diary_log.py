import enum
from sqlalchemy import ColumnElement
from sqlalchemy.ext.hybrid import hybrid_property

from ..utils.db import TimestampMixin, db

class UserRole(int, enum.Enum):
    CORE_TEAM = 1
    TECH_LEAD = 2
    QA_CONTRIBUTOR = 3
    CONTRIBUTOR = 4
    PROJECT_MANAGER = 5
    UI_UX = 6

class ExternalUserRole(TimestampMixin, db.Model):
    """
    TEMPORARY Model for mapping external users and their role
    NOTE: this should be substituted with proper user role service that aquires permission per project
    Currently used to attribute external manual time log to roles and incorporate users that are not in our beehive system
    """
    # TODO temporary table external_user_role, delete when user roles are implemented
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(256), nullable=False, index=True)
    role = db.Column(db.Enum(UserRole), nullable=False, index=True)
    price_per_hour = db.Column(db.DECIMAL(precision=5, scale=2))

    def __init__(self, email, role, price_per_hour):
        self.email = email
        self.role = role
        self.price_per_hour = price_per_hour

    def __repr__(self):
        return f'<ExternalUserRole {self.id} {self.email} {self.role}>'


class DiaryLog(TimestampMixin, db.Model):
    """
    Model for external manual time logging, no foreign keys here because user and project may not exist in system
    """
    id = db.Column(db.Integer(), primary_key=True)
    external_user_id = db.Column(db.Integer, db.ForeignKey('external_user_role.id'), nullable=False, index=True)
    project = db.Column(db.String(256), nullable=False)
    date = db.Column(db.Date(), nullable=False, index=True)
    duration_hours = db.Column(db.DECIMAL(precision=5, scale=2))
    text = db.Column(db.Text())

    user_role = db.relationship('ExternalUserRole', backref=db.backref('diary_logs', lazy='select', cascade='all,delete'), innerjoin=True)

    def __init__(self, external_user_id, project, date, duration_hours, text):
        self.external_user_id = external_user_id
        self.project = project
        self.date = date
        self.duration_hours = duration_hours
        self.text = text

    def __repr__(self):
        return f'<DiaryLog {self.id} {self.user_role.email} {self.project_name}>'

    @hybrid_property
    def cost(self) -> str:
        return self.duration_hours * self.user_role.price_per_hour

    @cost.inplace.expression
    @classmethod
    def _cost(cls) -> ColumnElement[str]:
        return db.select(ExternalUserRole.price_per_hour*cls.duration_hours).where(cls.external_user_id == ExternalUserRole.id).correlate_except(ExternalUserRole).limit(1).scalar_subquery()
