import { Paper } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { Link as LinkIcon } from '@material-ui/icons';
import dayjs from 'dayjs';
import duration from 'dayjs/plugin/duration';
import relativeTime from 'dayjs/plugin/relativeTime';
import utc from 'dayjs/plugin/utc';
import _ from 'lodash';
import { FunctionComponent, useEffect, useState } from 'react';

import { useAppDispatch } from '../../../hooks';
import { DashboardSelectors, dismissWorkProhibition, dismissWorkReservation, fetchPendingRows, prohibitWork, reserveWork, updateWorkPriority } from '../../../reducers/dashboard';
import { CopyButton } from '../../../shared';
import { TaskStatus } from '../../../types/task';
import { WorkType } from '../../../types/work';
import DataTable, { DataTableColumn } from './dataTable';
import PriorityColumn from './priorityColumn';
import WorkActionColumn from './workActionColumn';

// load dayjs duration and dependent plugin
dayjs.extend(duration);
dayjs.extend(relativeTime);
dayjs.extend(utc);

const columns: DataTableColumn[] = [
    {
        field: 'task|id',
        label: 'Task Id',
        minWidth: 100,
        tooltipField: 'task|description'
    },
    {
        field: 'task|delegatingUserId',
        label: 'Delegator Id',
        minWidth: 100,
        tooltipField: 'task|delegatingUserName'
    },
    {
        field: 'id',
        label: 'Work Id',
        minWidth: 50,
        suffixComponent: function suffixSpecificLink(value: number) {
            return (
                <CopyButton
                    text={`${window.location.protocol}//${window.location.host}/?workId=${value}`}
                    copyIcon={<LinkIcon color="primary" />}
                    copyTooltip="Copy direct link to clipboard"
                />
            );
        }
    },
    {
        field: 'workType',
        label: 'Work Type',
        minWidth: 100,
        format: (value: number) => _.startCase(_.toLower(WorkType[value]))
    },
    {
        field: 'task|status',
        label: 'Task Status',
        minWidth: 100,
        format: (value: number) => _.startCase(_.toLower(TaskStatus[value]))
    },
    {
        field: 'priority',
        label: 'Priority',
        minWidth: 100,
        submittableComponent: function emptyInputElement(row: any, value: string) {
            return (
                <PriorityColumn
                    row={row}
                    value={value}
                    onUpdatePriority={updateWorkPriority}
                />
            );
        
        }
    },
    {
        field: 'task|title',
        label: 'Task Title',
        minWidth: 100
    },
    {
        field: 'task|description',
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
        field: 'created',
        label: 'Time Since Creation',
        minWidth: 100,
        format: (value: string) => value ? dayjs.utc(value).fromNow() : '-'
    },
    {
        field: 'task|created',
        label: 'Time Since Task Creation',
        minWidth: 100,
        format: (value: string) => value ? dayjs.utc(value).fromNow() : '-'
    },
    {
        field: 'workRecordsCount',
        label: 'Work Record Count',
        minWidth: 100
    },
    {
        field: 'workRecordsTotalDurationSeconds',
        label: 'Work Record Duration Sum',
        minWidth: 100,
        format: (value: number) => value ? dayjs.duration(value, 'seconds').humanize() : '-'
    },
    {
        field: 'workRecordsContributorsViewed',
        label: 'Work Record Contributors Viewed',
        minWidth: 100,
        tooltipHeader: 'Number of contributors who viewed this task'
    },
    {
        field: 'reservedWorkerId',
        label: 'Reserved To Worker',
        minWidth: 50,
        submittableComponent: function emptyInputElement(row: any, value: any) {
            return (
                <WorkActionColumn
                    row={row}
                    value={value}
                    onSubmitFunc={reserveWork}
                    onCancelFunc={dismissWorkReservation}
                />
            );
        
        },
        tooltipField: 'reservedWorkerName'
    },
    {
        field: 'prohibitedWorkerId',
        label: 'Prohibited For Worker',
        minWidth: 50,
        submittableComponent: function emptyInputElement(row: any, value: any) {
            return (
                <WorkActionColumn
                    row={row}
                    value={value}
                    onSubmitFunc={prohibitWork}
                    onCancelFunc={dismissWorkProhibition}
                />
            );
        
        },
        tooltipField: 'prohibitedWorkerName'
    }
];

const useStyles = makeStyles({
    root: {
        width: '100%'
    }
});

type Props = Record<string, never>;

const PendingWorkTab: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();

    const { pendingWorkRows, totalPendingWorkRows } = DashboardSelectors();

    const [ currentPage, setCurrentPage ] = useState(0);
    const [ rowsPerPage, setRowsPerPage ] = useState(25);

    useEffect(() => {
        dispatch(fetchPendingRows({ page: currentPage + 1, resultsPerPage: rowsPerPage }));
    }, [ dispatch, currentPage, rowsPerPage ]);

    return (
        <Paper className={classes.root}>
            <DataTable
                columns={columns}
                rows={pendingWorkRows}
                totalRows={totalPendingWorkRows}
                currentPage={currentPage}
                currentPageChanged={setCurrentPage}
                rowsPerPage={rowsPerPage}
                rowsPerPageChanged={setRowsPerPage}
            />
        </Paper>
    );
};

export default PendingWorkTab;
