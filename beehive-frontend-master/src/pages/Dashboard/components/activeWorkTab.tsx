import { Paper } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import dayjs from 'dayjs';
import duration from 'dayjs/plugin/duration';
import relativeTime from 'dayjs/plugin/relativeTime';
import _ from 'lodash';
import { FunctionComponent, useEffect, useState } from 'react';

import { useAppDispatch } from '../../../hooks';
import { DashboardSelectors, fetchActiveRows } from '../../../reducers/dashboard';
import { workMaxDurationMs, WorkType } from '../../../types/work';
import DataTable, { DataTableColumn } from './dataTable';

// load dayjs duration and dependent plugin
dayjs.extend(duration);
dayjs.extend(relativeTime);

const columns: DataTableColumn[] = [
    {
        field: 'work|task|id',
        label: 'Task Id',
        minWidth: 100,
        tooltipField: 'work|task|description'
    },
    {
        field: 'work|task|delegatingUserId',
        label: 'Delegator Id',
        minWidth: 100,
        tooltipField: 'work|task|delegatingUserName'
    },
    {
        field: 'work|id',
        label: 'Work Id',
        minWidth: 50
    },
    {
        field: 'id',
        label: 'Work Record Id',
        minWidth: 100
    },
    {
        field: 'userId',
        label: 'Worker Id',
        minWidth: 100,
        tooltipField: 'userName'
    },
    {
        field: 'work|workType',
        label: 'Work Type',
        minWidth: 100,
        format: (value: number) => _.startCase(_.toLower(WorkType[value]))
    },
    {
        field: 'work|task|title',
        label: 'Task Title',
        minWidth: 100
    },
    {
        field: 'work|task|description',
        label: 'Task Description',
        format: (value: string) => value ? (value.indexOf('---') !== -1 ? value.trim().substring(0, Math.min(100, value.indexOf('---'))): value.trim().substring(0, 100)) : '-',
        minWidth: 150
    },
    {
        field: 'work|tags',
        label: 'Tags',
        minWidth: 100,
        format: (value: []) => value && value.length > 0 ? value.join(', ') : ''
    },
    {
        field: 'work|skills',
        label: 'Skills',
        minWidth: 100,
        format: (value: []) => value && value.length > 0 ? value.join(', ') : ''
    },
    {
        field: 'durationSeconds',
        label: 'Elapsed',
        minWidth: 100,
        format: (value: number) => value ? dayjs.duration(value, 'seconds').humanize() : '-'
    },
    {
        field: 'startTimeEpochMs',
        label: 'Work Deadline',
        minWidth: 120,
        format: (value: number) => value ? dayjs(value + workMaxDurationMs).fromNow() : '-'
    },
    {
        field: 'workRecordsContributorsViewed',
        label: 'Work Record Contributors Viewed',
        minWidth: 100,
        tooltipHeader: 'Number of contributors who viewed this task'
    }
];

const useStyles = makeStyles({
    root: {
        width: '100%'
    }
});

type Props = Record<string, never>;

const ActiveWorkTab: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();

    const { activeWorkRows, totalActiveWorkRows } = DashboardSelectors();

    const [ currentPage, setCurrentPage ] = useState(0);
    const [ rowsPerPage, setRowsPerPage ] = useState(25);

    useEffect(() => {
        dispatch(fetchActiveRows({ page: currentPage + 1, resultsPerPage: rowsPerPage }));
    }, [ dispatch, currentPage, rowsPerPage ]);

    return (
        <Paper className={classes.root}>
            <DataTable
                columns={columns}
                rows={activeWorkRows}
                totalRows={totalActiveWorkRows}
                currentPage={currentPage}
                currentPageChanged={setCurrentPage}
                rowsPerPage={rowsPerPage}
                rowsPerPageChanged={setRowsPerPage}
            />
        </Paper>
    );
};

export default ActiveWorkTab;
