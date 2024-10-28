from .task import *
from .work import *
from .upwork import *


# schedule cron jobs
find_deserted_work.cron('0 * * * *', 'beehive-find-deserted-work')
find_past_reserved_work.cron('0 * * * *', 'beehive-find-past-reserved-work')
find_net_duration_work_records.cron('0 1,13 * * *', 'beehive-find-net-duration-work-records')
find_net_duration_cuckoo_accepted_tasks.cron('30 1 * * *', 'beehive-find-net-duration-cuckoo-accepted-tasks')
