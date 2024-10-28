from ..utils.db import db, RandomStringIdMixin, TimestampMixin

class ProjectDelegator(db.Model):
    __tablename__ = 'project_delegator'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.String(8), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    project_id = db.Column(db.Integer(), db.ForeignKey('project.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'project_id', name='_project_delegator_uc'),)

    def __init__(self, user_id, project_id):
        self.user_id = user_id
        self.project_id = project_id

    def __repr__(self):
        return f'<ProjectDelegator user {self.user_id} project {self.project_id}>'


class Project(TimestampMixin, db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(256), nullable=True)
    repo_link = db.Column(db.Text())
    trello_link = db.Column(db.Text())
    delegators = db.relationship('User', secondary=ProjectDelegator.__table__, lazy='select')

    def __init__(
        self, id, name, repo_link, trello_link, delegators=[]
    ):
        self.id = id

        self.name = name
        self.repo_link = repo_link
        self.trello_link = trello_link
        self.delegators = delegators

    def __repr__(self):
        return f'<Project {self.id}>'
