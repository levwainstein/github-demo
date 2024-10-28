import { Paper } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import dayjs from 'dayjs';
import duration from 'dayjs/plugin/duration';
import relativeTime from 'dayjs/plugin/relativeTime';
import utc from 'dayjs/plugin/utc';
import _ from 'lodash';
import { FunctionComponent, useEffect, useState } from 'react';
import { useHash } from 'react-use';

import { useAppDispatch } from '../../../hooks';
import { DashboardSelectors, fetchCompletedRows } from '../../../reducers/dashboard';
import { TaskStatus } from '../../../types/task';
import { WorkType } from '../../../types/work';
import DataTable, { DataTableColumn } from './dataTable';

// load dayjs duration and dependent plugin
dayjs.extend(duration);
dayjs.extend(relativeTime);
dayjs.extend(utc);

const TAB_ID = 'completed';

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
        linkHash: (value: string) => `/${TAB_ID}/${value}`,
        tooltipField: 'task|delegatingUserName'
    },
    {
        field: 'id',
        label: 'Work Id',
        minWidth: 50
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
        field: 'workRecordsCost',
        label: 'Work Record Cost',
        minWidth: 100,
        format: (value: number) => value ? '$' + value : '-',
        tooltipHeader: 'calculated cost for the intersection between upwork exact tracking time and our work record time'
    },
    {
        field: 'workRecordsNetDurationSeconds',
        label: 'Work Record Net Duration Sum',
        minWidth: 100,
        format: (value: number) => value ? dayjs.duration(value, 'seconds').format('HH:mm:ss') : '-',
        tooltipHeader: 'intersection between upwork exact tracking time and our work record time',
        tooltipField: 'exactUpworkDurations'
    },
    {
        field: 'workRecordsUpworkCost',
        label: 'Work Record Upwork Cost',
        minWidth: 100,
        format: (value: number) => value ? '$' + value : '-',
        tooltipHeader: 'calculated complete upwork cost, including upwork management fee'
    },
    {
        field: 'workRecordsUpworkDurationSeconds',
        label: 'Work Record Upwork Duration Sum',
        minWidth: 100,
        format: (value: number) => value ? dayjs.duration(value, 'seconds').format('HH:mm:ss') : '-',
        tooltipHeader: 'intersection between upwork rounded time and our work record time',
        tooltipField: 'roundedUpworkDurations'
    },
    {
        field: 'workRecordsContributorsViewed',
        label: 'Work Record Contributors Viewed',
        minWidth: 100,
        tooltipHeader: 'Number of contributors who viewed this task'
    },
    {
        field: 'workerId',
        label: 'Worker Id',
        minWidth: 100,
        tooltipField: 'workerName'
    }
];

const useStyles = makeStyles({
    root: {
        width: '100%',
        height: '100%'
    }
});

type Props = Record<string, never>;

const CompletedWorkTab: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();
    const [ hash, setHash ] = useHash();

    const { completedWorkRows, totalCompletedWorkRows } = DashboardSelectors();

    const [ currentPage, setCurrentPage ] = useState(0);
    const [ rowsPerPage, setRowsPerPage ] = useState(25);
    const [ delegatorUserIdFilter, setDelegatorUserIdFilter ] = useState<string | undefined>(undefined);

    useEffect(() => {
        // filter out empty hash parts (ie. '#/a/' splits into ['#', 'a', ''])
        const hashParts = hash.split('/').filter(p => p);

        // make sure this is the active tab
        if (hashParts.length < 1 || hashParts[1] !== TAB_ID) {
            return;
        }

        if (hashParts.length > 2) {
            setDelegatorUserIdFilter(hashParts[2]);
            setCurrentPage(0);
        } else {
            setDelegatorUserIdFilter(undefined);
        }
    }, [ hash, setDelegatorUserIdFilter, setCurrentPage ]);

    useEffect(() => {
        const fetchOptions: { page: number, resultsPerPage: number, filter?: {[key: string]: string} } = {
            page: currentPage + 1,
            resultsPerPage: rowsPerPage
        };

        if (delegatorUserIdFilter) {
            fetchOptions.filter = { delegatorId: delegatorUserIdFilter };
        }

        dispatch(fetchCompletedRows(fetchOptions));
    }, [ dispatch, currentPage, rowsPerPage, delegatorUserIdFilter ]);

    return (
        <Paper className={classes.root}>
            <DataTable
                columns={columns}
                rows={completedWorkRows}
                totalRows={totalCompletedWorkRows}
                currentPage={currentPage}
                currentPageChanged={setCurrentPage}
                rowsPerPage={rowsPerPage}
                rowsPerPageChanged={setRowsPerPage}
                onLinkClicked={(newHash) => setHash(newHash)}
            />
        </Paper>
    );
};

export default CompletedWorkTab;
