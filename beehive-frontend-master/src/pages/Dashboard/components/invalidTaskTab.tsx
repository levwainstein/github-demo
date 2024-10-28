import { Paper } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import dayjs from 'dayjs';
import duration from 'dayjs/plugin/duration';
import relativeTime from 'dayjs/plugin/relativeTime';
import _ from 'lodash';
import { FunctionComponent, useEffect, useState } from 'react';

import { useAppDispatch } from '../../../hooks';
import { DashboardSelectors, fetchInvalidRows } from '../../../reducers/dashboard';
import { TaskStatus, TaskType } from '../../../types/task';
import DataTable, { DataTableColumn } from './dataTable';

// load dayjs duration and dependent plugin
dayjs.extend(duration);
dayjs.extend(relativeTime);

const columns: DataTableColumn[] = [
    {
        field: 'id',
        label: 'Task Id',
        minWidth: 100,
        tooltipField: 'description'
    },
    {
        field: 'delegatingUserId',
        label: 'Delegator Id',
        minWidth: 100,
        tooltipField: 'delegatingUserName'
    },
    {
        field: 'taskType',
        label: 'Task Type',
        minWidth: 100,
        format: (value: number) => _.startCase(_.toLower(TaskType[value]))
    },
    {
        field: 'status',
        label: 'Task Status',
        minWidth: 100,
        format: (value: number) => _.startCase(_.toLower(TaskStatus[value]))
    },
    {
        field: 'title',
        label: 'Task Title',
        minWidth: 100
    },
    {
        field: 'description',
        label: 'Task Description',
        format: (value: string) => value ? (value.indexOf('---') !== -1 ? value.trim().substring(0, Math.min(100, value.indexOf('---'))): value.trim().substring(0, 100)) : '-',
        minWidth: 150
    },
    {
        field: 'tags',
        label: 'Tags',
        minWidth: 100,
        format: (value: []) => value && value.length > 0 ? value.join(', ') : ''
    },
    {
        field: 'skills',
        label: 'Skills',
        minWidth: 100,
        format: (value: []) => value && value.length > 0 ? value.join(', ') : ''
    },
    {
        field: 'invalidCode',
        label: 'Invalid Code',
        minWidth: 100
    },
    {
        field: 'invalidDescription',
        label: 'Invalid Description',
        minWidth: 170
    },
    {
        field: 'feedback',
        label: 'Feedback',
        minWidth: 170
    }
];

const useStyles = makeStyles({
    root: {
        width: '100%'
    }
});

type Props = Record<string, never>;

const InvalidTaskTab: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();

    const { invalidTaskRows, totalInvalidTaskRows } = DashboardSelectors();

    const [ currentPage, setCurrentPage ] = useState(0);
    const [ rowsPerPage, setRowsPerPage ] = useState(25);

    useEffect(() => {
        dispatch(fetchInvalidRows({ page: currentPage + 1, resultsPerPage: rowsPerPage }));
    }, [ dispatch, currentPage, rowsPerPage ]);

    return (
        <Paper className={classes.root}>
            <DataTable
                columns={columns}
                rows={invalidTaskRows}
                totalRows={totalInvalidTaskRows}
                currentPage={currentPage}
                currentPageChanged={setCurrentPage}
                rowsPerPage={rowsPerPage}
                rowsPerPageChanged={setRowsPerPage}
            />
        </Paper>
    );
};

export default InvalidTaskTab;
