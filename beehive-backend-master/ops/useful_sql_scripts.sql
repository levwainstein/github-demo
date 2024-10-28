-- distributio of all task types
select task_type, count(*) from task group by task_type order by task_type;

-- distribution of all task types by week
select week(created), task_type, count(*) from task group by week(created), task_type order by week(created), task_type;

-- distribution of tasks status type
select status, count(*) from task group by status order by status;

-- difference between when work is created to the community starting to work on it (todo: created histogram)
select work_record.created, work.created, timestampdiff(hour, work_record.created, work.created) from work_record inner join work;
