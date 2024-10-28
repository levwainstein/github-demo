import enum

from sqlalchemy import ColumnElement
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.sql import expression

from ..utils.db import db, RandomStringIdMixin, TimestampMixin

from .user import User
from .tag import TaskTag
from .skill import TaskSkill
from .repository import Repository
from .quest import Quest


class TaskStatus(int, enum.Enum):
    NEW = 1
    PENDING = 2
    PAUSED = 3
    IN_PROCESS = 4
    SOLVED = 5
    ACCEPTED = 6
    CANCELLED = 7
    INVALID = 8
    PENDING_CLASS_PARAMS = 9
    PENDING_PACKAGE = 10
    MODIFICATIONS_REQUESTED = 11


class TaskType(int, enum.Enum):
    CREATE_FUNCTION = 1
    UPDATE_FUNCTION = 2
    DESCRIBE_FUNCTION = 3
    REVIEW_TASK = 4
    OPEN_TASK = 5
    CREATE_REACT_COMPONENT = 6
    UPDATE_REACT_COMPONENT = 7
    CHECK_REUSABILITY = 8
    CUCKOO_CODING = 9
    CUCKOO_ITERATION = 10


class ReviewStatus(int, enum.Enum):
    INADEQUATE = 1
    REQUIRES_MODIFICATION = 2
    ADEQUATE = 3


class Task(TimestampMixin, RandomStringIdMixin, db.Model):
    id = db.Column(db.String(8), primary_key=True)
    delegating_user_id = db.Column(db.String(8), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    description = db.Column(db.Text(), nullable=False)
    func_name = db.Column(db.String(256), nullable=True)
    title = db.Column(db.Text(), nullable=True)
    delegation_time_seconds = db.Column(db.Integer(), nullable=True)
    status = db.Column(db.Enum(TaskStatus), nullable=False, index=True)
    feedback = db.Column(db.Text())
    priority = db.Column(db.SmallInteger(), nullable=False, default=1)
    task_type = db.Column(db.Enum(TaskType), nullable=False)
    review_feedback = db.Column(db.Text())
    review_status = db.Column(db.Enum(ReviewStatus))
    review_completed = db.Column(db.Boolean(), server_default=expression.false(), nullable=False)
    advanced_options = db.Column(MutableDict.as_mutable(db.JSON()))
    force_submit_reason = db.Column(db.Text())
    total_net_duration_seconds = db.Column(db.Integer)
    quest_id = db.Column(db.String(8), db.ForeignKey('quest.id', ondelete='CASCADE'), nullable=True, index=True)

    tags = db.relationship('Tag', secondary=TaskTag.__table__, lazy='select', back_populates='tasks')
    skills = db.relationship('Skill', secondary=TaskSkill.__table__, lazy='select', back_populates='tasks')
    delegating_user = db.relationship('User', backref=db.backref('tasks', lazy='select', cascade='all,delete'), innerjoin=True, foreign_keys=[delegating_user_id])
    repository = db.relationship('Repository', backref=db.backref('repo_tasks', lazy='select'), innerjoin=True)
    repository_id = db.Column(db.String(8), db.ForeignKey('repository.id'), nullable=False, index=True)
    quest = db.relationship('Quest', backref=db.backref('tasks', lazy='select', cascade='all,delete'), innerjoin=True, foreign_keys=[quest_id])

    def __init__(
        self, delegating_user_id, description, func_name, status,
        priority, task_type,
        advanced_options, review_feedback=None,
        review_status=None, review_completed=None, tags=None, skills=None,
        title=None, repository_id=None, delegation_time_seconds=None, quest_id=None
    ):
        self.id = self._get_random_id()

        self.delegating_user_id = delegating_user_id
        self.description = description
        self.func_name = func_name
        self.title = title
        self.status = status
        self.priority = priority
        self.task_type = task_type
        self.advanced_options = advanced_options
        self.review_feedback = review_feedback
        self.review_status = review_status
        self.review_completed = review_completed
        self.tags = tags
        self.skills = skills
        self.repository_id = repository_id
        self.delegation_time_seconds = delegation_time_seconds
        self.quest_id = quest_id

    @classmethod
    def from_cuckoo(cls, delegating_user_id, description,
        status, priority, task_type, title='', tags=None, skills=None, advanced_options=None, repository_id=None, quest_id=None):
        return cls(
            delegating_user_id = delegating_user_id,
            description = description,
            func_name = None,
            title = title,
            status = status,
            priority = priority,
            task_type = task_type,
            advanced_options = advanced_options,
            review_feedback = None,
            review_status = None,
            review_completed = None,
            tags = tags,
            skills = skills,
            repository_id = repository_id,
            quest_id = quest_id
        )
    
    @classmethod
    def from_delegation(cls, delegating_user_id, description, title, repository_id,
        status, priority, task_type, delegation_time_seconds=None, tags=None, skills=None, advanced_options=None):
        return cls(
            delegating_user_id = delegating_user_id,
            description = description,
            func_name = None,
            title = title,
            status = status,
            priority = priority,
            task_type = task_type,
            advanced_options = advanced_options,
            review_feedback = None,
            review_status = None,
            review_completed = None,
            tags = tags,
            skills = skills,
            repository_id = repository_id,
            delegation_time_seconds  = delegation_time_seconds
        )

    def __repr__(self):
        return f'<Task {self.id} {self.title}>'

    @staticmethod
    def _get_docker_id(task_id):
        # replace task id uppercase letters with '*{letter.lower()}' since docker
        # "repository name must be lowercase"
        valid_task_id = ''.join(f'_{c.lower()}' if c.isupper() else c for c in task_id)
        return f't-f{valid_task_id}'

    def get_docker_id(self):
        return Task._get_docker_id(self.id)

    @staticmethod
    def is_python_task(task_type):
        return task_type in (
            TaskType.CREATE_FUNCTION,
            TaskType.UPDATE_FUNCTION,
            TaskType.DESCRIBE_FUNCTION,
            TaskType.REVIEW_TASK,
            TaskType.OPEN_TASK,
            TaskType.CHECK_REUSABILITY
        )

    @staticmethod
    def is_react_task(task_type):
        return task_type in (
            TaskType.CREATE_REACT_COMPONENT,
            TaskType.UPDATE_REACT_COMPONENT
        )

    @property
    def name(self):
        if self.func_name:
            return self.func_name
        if self.title:
            return self.title
        if self.description:
            if '---' in self.description:
                return self.description.split('---',1)[0].strip()
            return self.description[:75]
        return None

    @hybrid_property
    def delegating_user_name(self) -> str:
        return self.delegating_user.name

    @delegating_user_name.inplace.expression
    @classmethod
    def _delegating_user_name(cls) -> ColumnElement[str]:
        return db.select(User.name).where(cls.delegating_user_id == User.id).scalar_subquery()

    @property
    def rating_object_key(self):
        return f't-{self.id}'
