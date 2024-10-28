import enum

from sqlalchemy import ColumnElement
from sqlalchemy.ext.hybrid import hybrid_property

from ..logic.work_mappers.base import BaseWorkMapper, deflate_mapper
from ..utils.db import db, TimestampMixin

from .tag import WorkTag
from .skill import WorkSkill
from .user import User


# will probably add more statuses in the future for reserved work etc.
class WorkStatus(int, enum.Enum):
    AVAILABLE = 1
    UNAVAILABLE = 2
    COMPLETE = 3
    PENDING_PACKAGE = 4


class WorkType(int, enum.Enum):
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
    CUCKOO_QA = 11


class Work(TimestampMixin, db.Model):
    id = db.Column(db.Integer(), primary_key=True)  # sqlalchemy sets only-primary-key-integer field to auto increments
    task_id = db.Column(db.String(8), db.ForeignKey('task.id'), nullable=False, index=True)
    status = db.Column(db.Enum(WorkStatus), nullable=False)
    work_type = db.Column(db.Enum(WorkType), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    work_input = db.Column(db.JSON, nullable=True)
    chain = db.Column(db.JSON)
    priority = db.Column(db.SmallInteger(), nullable=False)
    reserved_worker_id = db.Column(db.String(8), db.ForeignKey('user.id', ondelete='CASCADE'))
    reserved_until_epoch_ms = db.Column(db.BigInteger())
    prohibited_worker_id = db.Column(db.String(8), db.ForeignKey('user.id', ondelete='CASCADE'))

    task = db.relationship('Task', backref=db.backref('works', lazy='select', cascade='all,delete'), innerjoin=True)
    reserved_worker = db.relationship('User', backref=db.backref('works', lazy='select', cascade='all,delete'), innerjoin=True, foreign_keys=[reserved_worker_id])
    prohibited_worker = db.relationship('User', backref=db.backref('prohibited_works', lazy='select', cascade='all,delete'), innerjoin=True, foreign_keys=[prohibited_worker_id])
    tags = db.relationship('Tag', secondary=WorkTag.__table__, lazy='select', back_populates='works')
    skills = db.relationship('Skill', secondary=WorkSkill.__table__, lazy='select', back_populates='works')

    def __init__(self, task_id, status, work_type, description, work_input, chain=None, deflated_chain=None, priority=2, tags=None, skills=None):
        # validate params
        self._validate_chain(chain, deflated_chain)

        self.task_id = task_id
        self.status = status
        self.work_type = work_type
        self.description = description
        self.work_input = work_input
        self.tags = tags
        self.skills = skills
        self.priority = priority

        if deflated_chain:
            self.chain = deflated_chain
        elif chain:
            self.chain = self._serialize_chain(chain)

    @classmethod
    def from_cuckoo(cls, task_id, status, work_type, description, priority=2, tags=None, skills=None, chain=None, work_input=None):
        return cls(
            task_id = task_id,
            status = status,
            work_type = work_type,
            description = description,
            work_input = work_input,
            chain = chain,
            priority=priority,
            deflated_chain=None,
            tags = tags,
            skills = skills
        )

    def __repr__(self):
        return f'<Work {self.id}>'

    @staticmethod
    def _validate_chain(chain, deflated_chain):
        if chain and deflated_chain:
            raise ValueError('only one of "chain", "deflated_chain" may be supplied')

        if chain:
            if type(chain) is not list:
                raise TypeError('chain must be a list')
            if any(not isinstance(link, BaseWorkMapper) for link in chain):
                raise TypeError('all chain links must be descendants of BaseWorkMapper')
        elif deflated_chain:
            if type(deflated_chain) is not list:
                raise TypeError('deflated_chain must be a list')

    @staticmethod
    def _serialize_chain(chain):
        return [deflate_mapper(link) for link in chain]

    @hybrid_property
    def reserved_worker_name(self) -> str:
        return self.reserved_worker.name

    @reserved_worker_name.inplace.expression
    @classmethod
    def _reserved_worker_name(cls) -> ColumnElement[str]:
        return db.select([User.name]).where(cls.reserved_worker_id == User.id).scalar_subquery()

    @hybrid_property
    def prohibited_worker_name(self) -> str:
        return self.prohibited_worker.name

    @prohibited_worker_name.inplace.expression
    @classmethod
    def _prohibited_worker_name(cls) -> ColumnElement[str]:
        return db.select([User.name]).where(cls.prohibited_worker_id == User.id).scalar_subquery()

    @property
    def rating_object_key(self):
        return f'w-{self.id}'
