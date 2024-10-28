from sqlalchemy.orm.exc import NoResultFound

from ..utils.db import db


class UserTag(db.Model):
    __tablename__ = 'user_tag'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.String(8), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'tag_id', name='_user_tag_uc'),)

    def __init__(self, user_id, tag_id):
        self.user_id = user_id
        self.tag_id = tag_id

    def __repr__(self):
        return f'<UserTag user {self.user_id} tag {self.tag_id}>'


class WorkTag(db.Model):
    __tablename__ = 'work_tag'

    id = db.Column(db.Integer(), primary_key=True)
    work_id = db.Column(db.Integer(), db.ForeignKey('work.id', ondelete='CASCADE'), nullable=False)
    tag_id = db.Column(db.Integer(), db.ForeignKey('tag.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('work_id', 'tag_id', name='_work_tag_uc'),)

    def __init__(self, work_id, tag_id):
        self.work_id = work_id
        self.tag_id = tag_id

    def __repr__(self):
        return f'<WorkTag work {self.work_id} tag {self.tag_id}>'
    

class TaskTag(db.Model):
    __tablename__ = 'task_tag'

    id = db.Column(db.Integer(), primary_key=True)
    task_id = db.Column(db.String(8), db.ForeignKey('task.id', ondelete='CASCADE'), nullable=False)
    tag_id = db.Column(db.Integer(), db.ForeignKey('tag.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('task_id', 'tag_id', name='_task_tag_uc'),)

    def __init__(self, task_id, tag_id):
        self.task_id = task_id
        self.tag_id = tag_id

    def __repr__(self):
        return f'<TaskTag task {self.task_id} tag {self.tag_id}>'


class Tag(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), nullable=False, index=True)

    users = db.relationship('User', secondary=UserTag.__table__, lazy='select', back_populates='tags')
    works = db.relationship('Work', secondary=WorkTag.__table__, lazy='select', back_populates='tags')
    tasks = db.relationship('Task', secondary=TaskTag.__table__, lazy='select', back_populates='tags')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    @staticmethod
    def get_or_create(name):
        try:
            obj = Tag.query.filter_by(name=name).one()
        except NoResultFound:
            obj = Tag(name=name)
            db.session.add(obj)

        return obj
