## Initialize script for testing locally on fresh DB
## To run: PYTHONPATH="$(pwd)/src:$PYTHONPATH" FLASK_APP="src.app:create_app" FLASK_ENV=development python scripts/initialize.py

from src import app as flask_app
from src.utils.db import db
from src.models.user import User
from src.models.task import Task, TaskType, TaskStatus
from src.models.team import Team
from src.models.work import Work, WorkStatus, WorkType

app = flask_app.create_app('testing')
with app.app_context():

    # Creating user and setting it as activated
    email = input('enter email\n')
    password = str(input('enter password\n')).strip()
    user = User(email = email, 
                hashed_password = User._hash_password(password),
                first_name = "",
                last_name = "",
                github_user = "",
                trello_user = "",
                availability_weekly_hours = 0,
                price_per_hour = 0,
                notifications = False,
                activation_token = ""
                )
    user.activated = True

    print('creating user')
    db.session.add(user)
    db.session.commit()

    user_id = user.id
    print('new user id', user_id)

    # Creating team
    print('creating team')
    team = Team("generated team", user_id)
    db.session.add(team)
    db.session.commit()

    print('updating user team')
    user.team_id = team.id
    db.session.add(user)

    # Creating dummy task
    print('creating task')
    task = Task(
            delegating_user_id=user_id,
            delegating_team_id=None,
            description="Dummy task from initialize.py",
            func_name=None,
        func_input=None,
            status=TaskStatus.PENDING,
            solution_code="",
            target_file="",
            absolute_target_file="",
            priority=0,
            task_type=TaskType.CUCKOO_CODING,
            original_code="",
            class_name="",
            class_id=None,
            class_init_params="",
            available_names=None,
            advanced_options={},
            tags=[],
            skills=[]
        )
    db.session.add(task)
    db.session.commit()

    # Creating work
    print('creating work')
    work = Work(
        task_id=task.id,
        status=WorkStatus.AVAILABLE,
        work_type=WorkType.CUCKOO_CODING,
        description=task.description,
        work_input=None,
        chain=None,
        deflated_chain=None,
        priority=task.priority,
        tags=task.tags,
        skills=task.skills
    )
    db.session.add(work)
    db.session.commit()