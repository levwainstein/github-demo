from ..utils.db import db, RandomStringIdMixin, TimestampMixin

from .project import Project

class Repository(TimestampMixin, db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(256), nullable=True)
    url = db.Column(db.Text())
    project = db.relationship('Project', backref=db.backref('repositories', lazy='subquery', cascade='all,delete'), innerjoin=True)
    project_id = db.Column(db.Integer(), db.ForeignKey('project.id'), nullable=False, index=True)

    def __init__(self, id, name, url, project_id):
        self.id = id
        self.project_id = project_id
        self.name = name
        self.url = url

    def __repr__(self):
        return f'<Repository name: {self.name} url: {self.url}>'
