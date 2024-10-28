from .task import TaskType
from .task_classification import TaskTypeClassification
from ..utils.db import db
from .skill import TaskTemplateSkill


class TaskTemplate(db.Model):
    id = db.Column(db.Integer(), primary_key=True)  # sqlalchemy sets only-primary-key-integer field to auto increments
    name = db.Column(db.String(64), nullable=False, index=True)
    task_description = db.Column(db.Text(), nullable=False)
    #the following field is deprecated, use task_classification instead
    task_type = db.Column(db.Enum(TaskType), nullable=False)
    task_classification = db.Column(db.Enum(TaskTypeClassification), nullable=False)
    repository = db.relationship('Repository', backref=db.backref('repo_templates', lazy='select', cascade='all,delete'), innerjoin=True)
    repository_id = db.Column(db.String(8), db.ForeignKey('repository.id'), nullable=False, index=True)
    skills = db.relationship('Skill', secondary=TaskTemplateSkill.__table__, lazy='subquery')

    def __init__(self, name, task_description, task_type, repository_id, skills = [], task_classification = None):
        self.name = name
        self.task_description = task_description
        self.task_type = task_type
        self.repository_id = repository_id
        self.skills = skills
        self.task_classification = task_classification

    def __repr__(self):
        return f'<DelegationTemplate {self.name}>'
