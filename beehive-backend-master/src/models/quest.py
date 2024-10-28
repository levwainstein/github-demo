import enum

from sqlalchemy import ColumnElement
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict

from ..utils.db import db, RandomStringIdMixin, TimestampMixin

from .user import User
# from .task import Task

class QuestStatus(int, enum.Enum):
    NEW = 1
    IN_PROCESS = 2
    IN_REVIEW = 3
    DONE = 4


class QuestType(int, enum.Enum):
    FEATURE = 1
    BUG = 2


class Quest(TimestampMixin, RandomStringIdMixin, db.Model):
    id = db.Column(db.String(8), primary_key=True)
    delegating_user_id = db.Column(db.String(8), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    description = db.Column(db.Text(), nullable=False)
    title = db.Column(db.Text(), nullable=True)
    status = db.Column(db.Enum(QuestStatus), nullable=False, index=True)
    quest_type = db.Column(db.Enum(QuestType), nullable=False)
    links = db.Column(MutableDict.as_mutable(db.JSON()))
    project = db.relationship('Project', backref=db.backref('quests', lazy='select', passive_deletes=True), innerjoin=True)
    project_id = db.Column(db.Integer(), db.ForeignKey('project.id', ondelete='SET NULL'), nullable=True, index=True)
    delegation_time_seconds = db.Column(db.Integer(), nullable=True)

    delegating_user = db.relationship('User', backref=db.backref('quests', lazy='select', cascade='all,delete'), innerjoin=True, foreign_keys=[delegating_user_id])

    def __init__(
        self, delegating_user_id, description, title,
        status, quest_type,
        links, project_id, task_ids=None, delegation_time_seconds=None
    ):
        self.id = self._get_random_id()

        self.delegating_user_id = delegating_user_id
        self.description = description
        self.title = title
        self.status = status
        self.quest_type = quest_type
        self.links = links
        self.project_id = project_id
        self.task_ids = task_ids
        self.project_id = project_id
        self.delegation_time_seconds = delegation_time_seconds

    def __repr__(self):
        return f'<Quest {self.id} {self.title}>'

    @hybrid_property
    def delegating_user_name(self) -> str:
        return self.delegating_user.name

    @delegating_user_name.inplace.expression
    @classmethod
    def _delegating_user_name(cls) -> ColumnElement[str]:
        return db.select(User.name).where(cls.delegating_user_id == User.id).scalar_subquery()

    @property
    def rating_object_key(self):
        return f'q-{self.id}'


class SuccessCriteria(TimestampMixin, RandomStringIdMixin, db.Model):
    id = db.Column(db.String(8), primary_key=True)
    quest_id = db.Column(db.String(8), db.ForeignKey('quest.id', ondelete='CASCADE'), nullable=False, index=True)
    description = db.Column(db.Text(), nullable=False)
    title = db.Column(db.Text(), nullable=False)
    explanation = db.Column(db.Text(), nullable=True)

    quest = db.relationship('Quest', backref=db.backref('success_criteria', lazy='select', cascade='all,delete'), innerjoin=True, foreign_keys=[quest_id])


    def __init__(self, quest_id, description, title, explanation):
        self.id = self._get_random_id()

        self.quest_id = quest_id
        self.description = description
        self.title = title
        self.explanation = explanation

    def __repr__(self):
        return f'<Success Criteria {self.id} {self.title} {self.explanation}>'
