from flask import request
from prometheus_client import Counter, Summary
from prometheus_flask_exporter import _to_status_code
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics

from .auth import metrics_auth
from ..__version__ import __major__, __micro__, __minor__, __title__, __version__


def init_app(app):
    # init prometheus_flask_exporter here so that the prometheus multiprocess
    # object doesn't initialize and look for its env vars
    metrics = GunicornInternalPrometheusMetrics(
        app=app,
        group_by='endpoint',
        default_labels={
            'path': lambda: request.path
        },
        #path=None
        metrics_decorator=metrics_auth
    )

    #tmp_path = metrics.path
    #metrics.path = None
    #metrics.init_app(app)
    #metrics.path = tmp_path

    # record info metric with info about this running instance
    metrics.info(
        'app_info',
        __title__,
        version=__version__,
        major=__major__,
        minor=__minor__,
        micro=__micro__
    )

    # register non-flask-exporter metrics with the used registry
    metrics.registry.register(work_finish_summary)
    metrics.registry.register(task_prepare_duration)
    metrics.registry.register(task_prepare_exception)
    metrics.registry.register(task_prepare_success)
    metrics.registry.register(task_prepare_derived_duration)
    metrics.registry.register(task_prepare_derived_exception)
    metrics.registry.register(task_prepare_derived_success)
    metrics.registry.register(find_deserted_work_exception)
    metrics.registry.register(find_pre_deserted_work_exception)
    metrics.registry.register(user_send_email_exception)
    metrics.registry.register(admin_send_email_exception)
    metrics.registry.register(trigger_pollinator_exception)

# work-finish metric which records work output
work_finish_summary = Summary(
    'beehive_work_finish_summary',
    'Work finish summary',
    ['output'],
    registry=None
)
work_finish_summary.labels(output='request_package')
work_finish_summary.labels(output='feedback')
work_finish_summary.labels(output='solve')
work_finish_summary.labels(output='cancel')

# task-prepare job duration metric
task_prepare_duration = Summary(
    'beehive_task_prepare_duration_seconds',
    'Task prepare duration seconds summary',
    registry=None
)

# task-prepare job exception metric
task_prepare_exception = Counter(
    'beehive_task_prepare_exception',
    'Task prepare exception counter',
    registry=None
)

# task-prepare job success metric
task_prepare_success = Counter(
    'beehive_task_prepare_success',
    'Task prepare success counter',
    registry=None
)

# task-prepare-derived job duration metric
task_prepare_derived_duration = Summary(
    'beehive_task_prepare_derived_duration_seconds',
    'Task prepare derived duration seconds summary',
    registry=None
)

# task-prepare-derived job exception metric
task_prepare_derived_exception = Counter(
    'beehive_task_prepare_derived_exception',
    'Task prepare derived exception counter',
    registry=None
)

# task-prepare-derived job success metric
task_prepare_derived_success = Counter(
    'beehive_task_prepare_derived_success',
    'Task prepare derived success counter',
    registry=None
)

# task-prepare-cuckoo job duration metric
task_prepare_cuckoo_duration = Summary(
    'beehive_task_prepare_cuckoo_duration_seconds',
    'Task prepare cuckoo duration seconds summary',
    registry=None
)

# task-prepare-cuckoo job exception metric
task_prepare_cuckoo_exception = Counter(
    'beehive_task_prepare_cuckoo_exception',
    'Task prepare cuckoo exception counter',
    registry=None
)

# task-prepare-cuckoo job success metric
task_prepare_cuckoo_success = Counter(
    'beehive_task_prepare_cuckoo_success',
    'Task prepare cuckoo success counter',
    registry=None
)

# find-deserted-work job exception metric
find_deserted_work_exception = Counter(
    'beehive_find_deserted_work_exception',
    'Find deserted work exception counter',
    registry=None
)

# find-pre-deserted-work job exception metric
find_pre_deserted_work_exception = Counter(
    'beehive_find_pre_deserted_work_exception',
    'Find pre deserted work exception counter',
    registry=None
)

# find-past-reserved-work job exception metric
find_past_reserved_work_exception = Counter(
    'beehive_find_past_reserved_work_exception',
    'Find past reservation work exception counter',
    registry=None
)

# user_send_email job exception metric
user_send_email_exception = Counter(
    'beehive_user_send_email_exception',
    'User send email exception counter',
    registry=None
)

# admin_send_email job exception metric
admin_send_email_exception = Counter(
    'beehive_admin_send_email_exception',
    'Admin send email exception counter',
    registry=None
)

# trigger_pollinator job exception metric
trigger_pollinator_exception = Counter(
    'trigger_pollinator_exception',
    'Trigger pollinator exception counter',
    registry=None
)

# find_net_duration_work_records job duration metric
find_net_duration_work_records_duration = Summary(
    'beehive_find_net_duration_work_records_duration_seconds',
    'Find net duration work records duration seconds summary',
    registry=None
)

# find_net_duration_work_records job exception metric
find_net_duration_work_records_exception = Counter(
    'beehive_find_net_duration_work_records_exception',
    'Find net duration work records exception counter',
    registry=None
)

# find_net_duration_work_records job success metric
find_net_duration_work_records_success = Counter(
    'beehive_find_net_duration_work_records_success',
    'Find net duration work records success counter',
    registry=None
)

# find_net_duration_cuckoo_accepted_tasks job duration metric
find_net_duration_cuckoo_accepted_tasks_duration = Summary(
    'beehive_find_net_duration_cuckoo_accepted_tasks_duration_seconds',
    'Find net duration cuckoo accepted tasks duration seconds summary',
    registry=None
)

# find_net_duration_cuckoo_accepted_tasks job exception metric
find_net_duration_cuckoo_accepted_tasks_exception = Counter(
    'beehive_find_net_duration_cuckoo_accepted_tasks_exception',
    'Find net duration cuckoo accepted tasks exception counter',
    registry=None
)

# find_net_duration_cuckoo_accepted_tasks job success metric
find_net_duration_cuckoo_accepted_tasks_success = Counter(
    'beehive_find_net_duration_cuckoo_accepted_tasks_success',
    'Find net duration cuckoo accepted tasks success counter',
    registry=None
)
