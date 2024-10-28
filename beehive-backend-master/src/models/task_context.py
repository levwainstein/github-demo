from ..utils.db import db, RandomStringIdMixin, TimestampMixin

from .project import Project

class TaskContext(TimestampMixin, RandomStringIdMixin, db.Model):
    id = db.Column(db.String(8), primary_key=True)
    file = db.Column(db.Text())
    entity = db.Column(db.Text())
    potential_use = db.Column(db.Text())
    task = db.relationship('Task', backref=db.backref('task_context', lazy='select', cascade='all,delete'), innerjoin=True)
    task_id = db.Column(db.String(8), db.ForeignKey('task.id'), nullable=False, index=True)

    def __init__(self, file, entity, potential_use, task_id):
        self.id = self._get_random_id()
        self.file = file
        self.entity = entity
        self.potential_use = potential_use
        self.task_id = task_id

    def __repr__(self):
        return f'<TaskContext id: {self.id} file: {self.file} entity: {self.entity} potential_use: {self.potential_use} task_id: {self.task_id}>'
    
    @staticmethod
    def create(file, entity, potential_use, task_id):
        context = TaskContext(file, entity, potential_use, task_id)
        db.session.add(context)
        return context
