"""delegation_historical_links_populations

Revision ID: 0077
Revises: 0076
Create Date: 2024-06-05 11:56:03.107703

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base

# revision identifiers, used by Alembic.
revision = '0077'
down_revision = '0076'
branch_labels = None
depends_on = None

Base = automap_base()
Session = sessionmaker()


def upgrade():
    bind = op.get_bind()
    Base.prepare(autoload_with=bind, generate_relationship=lambda *args, **kwargs: None)
    Task = Base.classes.task
    TaskTag = Base.classes.task_tag 
    Tag = Base.classes.tag
    Repository = Base.classes.repository  
    Project = Base.classes.project  

    session = Session(bind=bind)
    tasks = session.query(Task).all()
    tags = session.query(Tag).all()
    tags_starts_with_project = [t for t in tags if t.name.startswith('project:')]
    for task in tasks:
        task_tags = session.query(TaskTag).filter(TaskTag.task_id == task.id).all()
        if not task.repository_id:
            print(f'task {task.id} missing repoId')
            joined_tags =  [t for t in tags_starts_with_project if len([s for s in task_tags if s.tag_id == t.id])]
            if len(joined_tags):
                project_name = joined_tags[0].name[8:]
                project = session.query(Project).filter(Project.name == project_name).first()
                if project:
                    print(f'looking for the repo of project_name {project_name} for task {task.id}')
                    repo = session.query(Repository).filter(Repository.project_id == project.id).first()
                    if repo:
                        print(f'setting repo id {repo.id} for task {task.id}')
                        task.repository_id = repo.id
                else:
                    print(f'missing project for task with id {task.id}')

        else:
            print(f'task {task.id} is already linked to a repo, making sure it has also the correct task tag')
            repo = session.query(Repository).filter(Repository.id == task.repository_id).first()
            if repo:
                print(f'found repo with project id {repo.project_id}')
                project = session.query(Project).filter(Project.id == repo.project_id).first()
                if project:
                    print(f'found project {project.name} will look for the tag')
                    tags_ends_with_the_project = [t for t in tags if t.name.endswith(project.name)]
                    if len(tags_ends_with_the_project):
                        tag_id = tags_ends_with_the_project[0].id
                        print(f'found tag with id {repo.project_id}')
                        if len([ts for ts in task_tags if ts.task_id == task.id and ts.tag_id == tag_id]):
                            print('task tag already exists')
                        else:
                            print('creating a task tag')
                            task_tag = TaskTag(task_id=task.id, tag_id=tag_id)
                            session.add(task_tag)
    session.commit()

def downgrade():
    pass
   