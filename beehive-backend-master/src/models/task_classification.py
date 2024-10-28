import enum
from ..utils.db import db, TimestampMixin

class TaskTypeClassification(enum.Enum):
    CREATE_COMPONENT = 'Create a component'
    MODIFY_COMPONENT = 'Modify/fix a component'
    CREATE_PAGE = 'Create a page/screen'
    MODIFY_PAGE = 'Modify/fix a page/screen'
    MODIFY_DESIGN = 'Change to match design'
    CREATE_ANIMATION = 'Creating an animation'
    CREATE_EVENT = 'Write events to Mixpanel/monitoring'
    CREATE_DATA_MODEL = 'Create/modify a data model'
    CREATE_ENDPOINT = 'Create/Modify an endpoint'
    CREATE_DJANGO_VIEW = 'Create a django view'
    MODIFY_DJANGO_VIEW = 'Modify/Fix a django view'
    CREATE_ALGORITHM = 'Write an algorithm / business logic'
    CREATE_SCRAPER = 'Scraping'
    CREATE_API_CONNECTOR = 'Connect a screen/component to an API/view/functionality'
    REFACTOR_CODE = 'Refactor existing code'
    CREATE_TEST_CASE = 'Write test cases'
    CREATE_AUTH = 'Authorization/Authentication'
    OTHER = 'Other'
    UNCERTAIN = 'Uncertain'

    def __str__(self) -> str:
        return self.value


class TaskClassification(TimestampMixin, db.Model):
    """
    Classification model for all task classifications retrieved by pollinator service.
    Conceptually an extension of the task model. 
    Currently supports only task type. 
    """
    id = db.Column(db.Integer(), primary_key=True)
    task_id = db.Column(db.String(8), db.ForeignKey('task.id', ondelete='CASCADE'), nullable=False)
    task_type = db.Column(db.Enum(TaskTypeClassification), nullable=False)

    task = db.relationship('Task', backref=db.backref('task_classifications', lazy='select', cascade='all,delete'), innerjoin=True, foreign_keys=[task_id])

    def __init__(
        self,
        task_id: str,
        task_type: TaskTypeClassification
    ):
        self.task_id = task_id
        self.task_type = task_type

    def __repr__(self):
        return f'<TaskTypeClassification {self.id} task {self.task_id}> type {self.task_type}'
