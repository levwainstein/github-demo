from sqlalchemy.orm.exc import NoResultFound

from ..utils.db import db


class UserSkill(db.Model):
    __tablename__ = 'user_skill'
    
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.String(8), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'skill_id', name='_user_skill_uc'),)

    def __init__(self, user_id, skill_id):
        self.user_id = user_id
        self.skill_id = skill_id

    def __repr__(self):
        return f'<UserSkill user {self.user_id} skill {self.skill_id}>'


class WorkSkill(db.Model):
    __tablename__ = 'work_skill'

    id = db.Column(db.Integer(), primary_key=True)
    work_id = db.Column(db.Integer(), db.ForeignKey('work.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer(), db.ForeignKey('skill.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('work_id', 'skill_id', name='_work_skill_uc'),)

    def __init__(self, work_id, skill_id):
        self.work_id = work_id
        self.skill_id = skill_id

    def __repr__(self):
        return f'<WorkSkill work {self.work_id} skill {self.skill_id}>'


class TaskSkill(db.Model):
    __tablename__ = 'task_skill'

    id = db.Column(db.Integer(), primary_key=True)
    task_id = db.Column(db.String(8), db.ForeignKey('task.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer(), db.ForeignKey('skill.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('task_id', 'skill_id', name='_task_skill_uc'),)

    def __init__(self, task_id, skill_id):
        self.task_id = task_id
        self.skill_id = skill_id

    def __repr__(self):
        return f'<TaskSkill task {self.task_id} skill {self.skill_id}>'
    
class TaskTemplateSkill(db.Model):
    __tablename__ = 'task_template_skill'

    id = db.Column(db.Integer(), primary_key=True)
    task_template_id = db.Column(db.String(8), db.ForeignKey('task_template.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer(), db.ForeignKey('skill.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('task_template_id', 'skill_id', name='template_skill_uc'),)

    def __init__(self, task_template_id, skill_id):
        self.task_template_id = task_template_id
        self.skill_id = skill_id

    def __repr__(self):
        return f'<TaskTemplateSkill template {self.task_template_id} skill {self.skill_id}>'


class Skill(db.Model):
    id = db.Column(db.Integer(), primary_key=True) 
    name = db.Column(db.String(64), nullable=False, index=True)

    users = db.relationship('User', secondary=UserSkill.__table__, lazy='select', back_populates='skills')
    works = db.relationship('Work', secondary=WorkSkill.__table__, lazy='select', back_populates='skills')
    tasks = db.relationship('Task', secondary=TaskSkill.__table__, lazy='select', back_populates='skills')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    @staticmethod
    def get_or_create(name):
        try:
            obj = Skill.query.filter_by(name=name).one()
        except NoResultFound:
            obj = Skill(name=name)
            db.session.add(obj)

        return obj
