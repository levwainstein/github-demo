import os

from flask import Flask
from flask_cors import CORS

from .config import config_map
from .log import init_app_logging
from .utils.auth import test_after_response_add_cors_headers
from .utils.db import db, migrate
from .utils.errors import init_app as errors_init_app
from .utils.jwt import jwt_manager
from .utils.marshmallow import ma
from .utils.metrics import init_app as metrics_init_app
from .utils.rq import rq
from .utils.grpc_client import grpc_client


def create_app(env=None):
    app = Flask(__name__)

    # configure the app
    app.config.from_object(config_map.get(str(env or os.environ.get('FLASK_ENV') or 'default').lower()))
    app.config.from_envvar('BACKEND_CONFIG_FILE', silent=True)

    # init logging
    init_app_logging(app)

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt_manager.init_app(app)
    ma.init_app(app)
    errors_init_app(app)
    rq.init_app(app)
    grpc_client.init_app(app)

    CORS(app)

    if app.config['PROMETHEUS_ENABLED']:
        metrics_init_app(app)

    # import all jobs (only after rq is initialized)
    from . import jobs

    # import views
    from .resources.health import Live, Ready
    from .resources.task import NotifyContributors, CuckooTaskCRUD, TaskCRUD
    from .resources.quest import QuestCRUD
    from .resources.task_context import TaskContextCRUD

    from .resources.work import (
        WorkRecordCRUD,
        WorkHistory,
        AvailableWork,
        WorkStart,
        WorkSkipped,
        WorkCheckpoint,
        WorkFinish,
        WorkAnalyze,
        WorkSolutionReview
    )
    from .resources.user import (
        UserSignin,
        UserSignup,
        UserSignout,
        UserTokenRefresh,
        UserActivation,
        UserActivationResend,
        UserResetPassword,
        UserResetPasswordChange,
        UserProfile
    )
    from .resources.honeycomb import HoneycombCRUD
    from .resources.task_template import TaskTemplateCRUD
    from .resources.skill import AvailableSkills
    from .resources.backoffice import (
        TaskUpdateFeedback,
        WorkUpdatePriority,
        UserCodeCreate,
        TaskWork,
        BackofficeUserProfile,
        TagCRUD,
        SkillCRUD,
        ManualDiaryLog
    )
    from .resources.stats import (
        ActiveWork,
        CompletedWork,
        InvalidTasks,
        PendingWork,
        ActiveUsers,
        Honeycombs,
        WorkReservation,
        Contributors,
        WorkProhibition,
        ContributorHistory
    )
    from .resources.upwork import (
        UpworkWorkDiary,
        UpworkCallback,
        UpworkCostReport
    )
    from .resources.general import ReportBug
    from .resources.community import SkillsBreakdown, ContributorsBreakdown

    from .resources.project import ListProjects, ProjectActivity, ProjectBudgetReview, ProjectContributors, ProjectDelayedTasks, ProjectQueue
    from .resources.delegation import DelegatorRepositories, DelegationTemplates, DelegateTask, DelegateQuest, DelegationTemplateCRUD
    from .resources.client_dashboard import ListClientRepositories, ProjectWorkTimeReview, ProjectQuests

    # create views
    live_view = Live.as_view('live')
    ready_view = Ready.as_view('ready')
    task_view = TaskCRUD.as_view('task')
    cuckoo_task_view = CuckooTaskCRUD.as_view('cuckoo_task')
    quest_view = QuestCRUD.as_view('quest')
    task_context_view = TaskContextCRUD.as_view('task_context')
    available_work_view = AvailableWork.as_view('available_work')
    work_record_view = WorkRecordCRUD.as_view('work_record')
    work_history_view = WorkHistory.as_view('work_history')
    work_start_view = WorkStart.as_view('work_start')
    work_skipped_view = WorkSkipped.as_view('work_skipped')
    work_checkpoint_view = WorkCheckpoint.as_view('work_checkpoint')
    work_finish_view = WorkFinish.as_view('work_finish')
    work_analyze_view = WorkAnalyze.as_view('work_analyze')
    work_solution_review_view = WorkSolutionReview.as_view('work_solution_review')
    signup_view = UserSignup.as_view('signup')
    signin_view = UserSignin.as_view('signin')
    signout_view = UserSignout.as_view('signout')
    token_refresh_view = UserTokenRefresh.as_view('token_refresh')
    user_activation_view = UserActivation.as_view('user_activation')
    user_activation_resend_view = UserActivationResend.as_view('user_activation_resend')
    user_reset_password_view = UserResetPassword.as_view('user_reset_password')
    user_reset_password_change_view = UserResetPasswordChange.as_view('user_reset_password_change')
    user_profile_view = UserProfile.as_view('user_profile')
    task_notify_view = NotifyContributors.as_view('task_notify_view')
    task_template_view = TaskTemplateCRUD.as_view('task_template')
    available_skills_view = AvailableSkills.as_view('available_skills')
    backoffice_task_update_feedback_view = TaskUpdateFeedback.as_view('backoffice_task_update_feedback_view')
    backoffice_work_update_priority_view = WorkUpdatePriority.as_view('backoffice_work_update_priority_view')
    backoffice_user_code_create_view = UserCodeCreate.as_view('backoffice_user_code_create_view')
    backoffice_task_work_view = TaskWork.as_view('backoffice_task_work_view')
    backoffice_user_profile_view = BackofficeUserProfile.as_view('backoffice_user_profile_view')
    backoffice_tag_view = TagCRUD.as_view('backoffice_tag_view')
    backoffice_skill_view = SkillCRUD.as_view('backoffice_skill_view')
    backoffice_diary_log_view = ManualDiaryLog.as_view('backoffice_diary_log_view')
    upwork_callback_view = UpworkCallback.as_view('upwork_callback')
    upwork_work_diary_view = UpworkWorkDiary.as_view('upwork_work_diary_view')
    upwork_cost_report_view = UpworkCostReport.as_view('upwork_cost_report_view')
    stats_active_work_view = ActiveWork.as_view('stats_active_work_view')
    stats_pending_work_view = PendingWork.as_view('stats_pending_work_view')
    stats_completed_work_view = CompletedWork.as_view('stats_completed_work_view')
    stats_invalid_tasks_view = InvalidTasks.as_view('stats_invalid_tasks_view')
    stats_users_view = ActiveUsers.as_view('stats_users_view')
    stats_honeycombs_view = Honeycombs.as_view('stats_honeycombs_view')
    stats_contributors_view = Contributors.as_view('stats_contributors_view')
    stats_contributor_history_view = ContributorHistory.as_view('stats_contributor_history_view')
    list_projects_view = ListProjects.as_view('list_projects_view')
    project_queue_view = ProjectQueue.as_view('project_queue_view')
    project_activity_view = ProjectActivity.as_view('project_activity_view')
    project_contributors_view = ProjectContributors.as_view('project_contributors_view')
    project_delayed_tasks_view = ProjectDelayedTasks.as_view('project_delayed_tasks_view')
    project_budget_review_view = ProjectBudgetReview.as_view('project_budget_review_view')
    stats_work_reservation_view = WorkReservation.as_view('stats_work_reservation')
    stats_work_prohibition_view = WorkProhibition.as_view('stats_work_prohibition')
    general_report_bug_view = ReportBug.as_view('report_bug_view')
    honeycomb_view = HoneycombCRUD.as_view('honeycomb_view')
    skills_breakdown_view = SkillsBreakdown.as_view('skills_breakdown_view')
    contributors_breakdown_view = ContributorsBreakdown.as_view('contributors_breakdown_view')
    delegator_repositories_view = DelegatorRepositories.as_view('delegator_repositories_view')
    delegation_templates_view = DelegationTemplates.as_view('delegation_templates_view')
    delegate_task_view = DelegateTask.as_view('delegate_task_view')
    delegate_quest_view = DelegateQuest.as_view('delegate_quest_view')
    delegation_template_crud_view = DelegationTemplateCRUD.as_view('delegation_template_crud_view')
    list_client_repositories_view = ListClientRepositories.as_view('list_client_repositories_view')
    project_work_time_review_view = ProjectWorkTimeReview.as_view('project_work_time_review_view')
    project_quests_view = ProjectQuests.as_view('project_quests_view')
    

    # add url rules
    app.add_url_rule('/api/inner/v1/health/livez', view_func=live_view, methods=['GET'])
    app.add_url_rule('/api/inner/v1/health/readyz', view_func=ready_view, methods=['GET'])
    app.add_url_rule('/api/v1/task', view_func=task_view, methods=['GET'], defaults={'task_id': None})
    app.add_url_rule('/api/v1/task/<string:task_id>', view_func=task_view, methods=['GET', 'DELETE'])
    app.add_url_rule('/api/v1/task/notify', view_func=task_notify_view, methods=['POST'])
    app.add_url_rule('/api/v1/task/cuckoo', view_func=cuckoo_task_view, methods=['POST', 'PUT'])
    app.add_url_rule('/api/v1/quest', view_func=quest_view, methods=['POST', 'PUT'])
    app.add_url_rule('/api/v1/quest/<string:quest_id>', view_func=quest_view, methods=['GET', 'DELETE'])
    app.add_url_rule('/api/v1/quest/delegate', view_func=delegate_quest_view, methods=['POST'])
    app.add_url_rule('/api/v1/task/<string:task_id>/context', view_func=task_context_view, methods=['POST', 'GET'])
    app.add_url_rule('/api/v1/task/<string:task_id>/context/<string:id>', view_func=task_context_view, methods=['PUT', 'DELETE'])
    app.add_url_rule('/api/v1/task/delegate', view_func=delegate_task_view, methods=['POST'])
    app.add_url_rule('/api/v1/work', view_func=work_record_view, methods=['GET'], defaults={'work_id': None})
    app.add_url_rule('/api/v1/work/history', view_func=work_history_view, methods=['GET'])
    app.add_url_rule('/api/v1/work/<int:work_id>', view_func=work_record_view, methods=['GET'])
    app.add_url_rule('/api/v1/work/available', view_func=available_work_view, methods=['GET'])
    app.add_url_rule('/api/v1/work/start', view_func=work_start_view, methods=['POST'])
    app.add_url_rule('/api/v1/work/skip', view_func=work_skipped_view, methods=['POST'])
    app.add_url_rule('/api/v1/work/checkpoint', view_func=work_checkpoint_view, methods=['POST'])
    app.add_url_rule('/api/v1/work/finish', view_func=work_finish_view, methods=['POST'])
    app.add_url_rule('/api/v1/work/analyze', view_func=work_analyze_view, methods=['POST'])
    app.add_url_rule('/api/v1/work/review', view_func=work_solution_review_view, methods=['POST'])
    app.add_url_rule('/api/v1/signup', view_func=signup_view, methods=['POST'])
    app.add_url_rule('/api/v1/signin', view_func=signin_view, methods=['POST'])
    app.add_url_rule('/api/v1/signout', view_func=signout_view, methods=['POST'])
    app.add_url_rule('/api/v1/auth/refresh', view_func=token_refresh_view, methods=['POST'])
    app.add_url_rule('/api/v1/auth/activate', view_func=user_activation_view, methods=['POST'])
    app.add_url_rule('/api/v1/auth/resend', view_func=user_activation_resend_view, methods=['POST'])
    app.add_url_rule('/api/v1/auth/reset', view_func=user_reset_password_view, methods=['POST'])
    app.add_url_rule('/api/v1/auth/reset/change', view_func=user_reset_password_change_view, methods=['POST'])
    app.add_url_rule('/api/v1/user/profile', view_func=user_profile_view, methods=['GET', 'PUT'])
    app.add_url_rule('/api/v1/task_template', view_func=task_template_view, methods=['GET'])
    app.add_url_rule('/api/v1/skill', view_func=available_skills_view, methods=['GET'])
    app.add_url_rule('/api/v1/backoffice/task/<string:task_id>', view_func=backoffice_task_update_feedback_view, methods=['PUT'])
    app.add_url_rule('/api/v1/backoffice/work/priority/<string:work_id>', view_func=backoffice_work_update_priority_view, methods=['PUT'])
    app.add_url_rule('/api/v1/backoffice/user-code', view_func=backoffice_user_code_create_view, methods=['GET'])
    app.add_url_rule('/api/v1/backoffice/task/<string:task_id>/work', view_func=backoffice_task_work_view, methods=['GET'])
    app.add_url_rule('/api/v1/backoffice/user-profile/<string:user_id>', view_func=backoffice_user_profile_view, methods=['GET', 'PUT', 'DELETE'])
    app.add_url_rule('/api/v1/backoffice/tag', view_func=backoffice_tag_view, methods=['GET', 'POST', 'DELETE'])
    app.add_url_rule('/api/v1/backoffice/skill', view_func=backoffice_skill_view, methods=['GET', 'POST', 'DELETE'])
    app.add_url_rule('/api/v1/backoffice/upwork-diary', view_func=upwork_work_diary_view, methods=['GET'])
    app.add_url_rule('/api/v1/backoffice/cost-report', view_func=upwork_cost_report_view, methods=['GET'])
    app.add_url_rule('/api/v1/backoffice/diary-log', view_func=backoffice_diary_log_view, methods=['POST'])
    app.add_url_rule('/api/v1/upwork-callback', view_func=upwork_callback_view, methods=['GET'])
    app.add_url_rule('/api/v1/stats/work/active', view_func=stats_active_work_view, methods=['GET'])
    app.add_url_rule('/api/v1/stats/work/pending', view_func=stats_pending_work_view, methods=['GET'])
    app.add_url_rule('/api/v1/stats/work/completed', view_func=stats_completed_work_view, methods=['GET'])
    app.add_url_rule('/api/v1/stats/task/invalid', view_func=stats_invalid_tasks_view, methods=['GET'])
    app.add_url_rule('/api/v1/stats/user', view_func=stats_users_view, methods=['GET'])
    app.add_url_rule('/api/v1/stats/contributors', view_func=stats_contributors_view, methods=['GET'])
    app.add_url_rule('/api/v1/stats/contributor/<string:user_id>', view_func=stats_contributor_history_view, methods=['GET'])
    app.add_url_rule('/api/v1/delegation/repositories', view_func=delegator_repositories_view, methods=['GET'])
    app.add_url_rule('/api/v1/delegation/templates', view_func=delegation_templates_view, methods=['GET'])
    app.add_url_rule('/api/v1/delegation/template', view_func=delegation_template_crud_view, methods=['PUT', 'POST'])
    app.add_url_rule('/api/v1/delegation/template/<int:template_id>', view_func=delegation_template_crud_view, methods=['DELETE'])
    app.add_url_rule('/api/v1/dashboards/projects', view_func=list_projects_view, methods=['GET'])
    app.add_url_rule('/api/v1/dashboards/projects/<int:project_id>/queue', view_func=project_queue_view, methods=['GET'])
    app.add_url_rule('/api/v1/dashboards/projects/<int:project_id>/activity', view_func=project_activity_view, methods=['GET'])
    app.add_url_rule('/api/v1/dashboards/projects/<int:project_id>/contributors', view_func=project_contributors_view, methods=['GET'])
    app.add_url_rule('/api/v1/dashboards/projects/<int:project_id>/delayed', view_func=project_delayed_tasks_view, methods=['GET'])
    app.add_url_rule('/api/v1/dashboards/projects/<int:project_id>/budget', view_func=project_budget_review_view, methods=['GET'])
    app.add_url_rule('/api/v1/dashboards/client/repositories', view_func=list_client_repositories_view, methods=['GET'])
    app.add_url_rule('/api/v1/dashboards/client/<string:project_id>/work-time-review', view_func=project_work_time_review_view, methods=['GET'])
    app.add_url_rule('/api/v1/dashboards/client/<string:project_id>/quests', view_func=project_quests_view, methods=['GET'])
    app.add_url_rule('/api/v1/stats/honeycomb', view_func=stats_honeycombs_view, methods=['GET'])
    app.add_url_rule('/api/v1/stats/work/<int:work_id>/reserve/<string:user_id>', view_func=stats_work_reservation_view, methods=['POST', 'DELETE'])
    app.add_url_rule('/api/v1/stats/work/<int:work_id>/prohibit/<string:user_id>', view_func=stats_work_prohibition_view, methods=['GET', 'DELETE'])
    app.add_url_rule('/api/v1/general/report-bug', view_func=general_report_bug_view, methods=['POST'])
    app.add_url_rule('/api/v1/honeycomb', view_func=honeycomb_view, methods=['GET'])
    app.add_url_rule('/api/v1/community/skills', view_func=skills_breakdown_view, methods=['GET'])
    app.add_url_rule('/api/v1/community/contributors', view_func=contributors_breakdown_view, methods=['GET'])

    # for testing env add cors headers to responses
    if app.config['TESTING']:
        app.after_request(test_after_response_add_cors_headers)

    return app
