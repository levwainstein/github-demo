import { Paper } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';	
import dayjs from 'dayjs';	
import duration from 'dayjs/plugin/duration';	
import relativeTime from 'dayjs/plugin/relativeTime';	
import utc from 'dayjs/plugin/utc';	
import _ from 'lodash';	
import { FunctionComponent, useEffect, useState } from 'react';	
import { useLocation } from 'react-router-dom';	

import { useAppDispatch } from '../../hooks';	
import {	
    DashboardSelectors,	
    fetchContributorHistoryRows	
} from '../../reducers/dashboard';	
import { RatingSubject } from '../../types/rating';	
import { TaskStatus } from '../../types/task';	
import { WorkOutcome } from '../../types/work';	
import DataTable, { DataTableColumn } from '../Dashboard/components/dataTable';	

// load dayjs duration and dependent plugin	
dayjs.extend(duration);	
dayjs.extend(relativeTime);	
dayjs.extend(utc);	

const userRatingDisplayLabel = (subject: RatingSubject) => {	
    switch (subject) {	
        case 'work_description':
            return 'description';
        case 'work_solution_match_requirements':
            return 'match req';
        case 'work_solution_code_quality':
            return 'code quality';
        case 'work_review_qa_functionality':	
            return 'review qa functionality';	
        case 'work_review_code_quality':	
            return 'review code quality';	
    }	
};	

const columns: DataTableColumn[] = [	
    {	
        field: 'work|task|id',	
        label: 'Task Id',	
        minWidth: 100,	
        tooltipField: 'work|task|description'	
    },	
    {	
        field: 'workId',	
        label: 'Work Id',	
        minWidth: 50	
    },	
    {	
        field: 'id',	
        label: 'Work Record Id',	
        minWidth: 50	
    },	
    {	
        field: 'outcome',	
        label: 'Work Outcome',	
        minWidth: 100,	
        format: (value: number) => _.startCase(_.toLower(WorkOutcome[value]))	
    },	
    {	
        field: 'ratings',	
        label: 'Work Record Rating Score',	
        format: (value: []) => value && value.length > 0 ? value.map((rating) => userRatingDisplayLabel(rating['subject']) + ':' + Math.round(rating['score'])).join(', ') : '',	
        minWidth: 120,	
        tooltipField: 'averageRating'	
    },	
    {	
        field: 'ratings',	
        label: 'Work Record Rating Text',	
        format: (value: []) => value && value.length > 0 ? value.map((rating) => rating['text'] ? userRatingDisplayLabel(rating['subject']) + ': ' + rating['text'] : null).filter(Boolean).join(', ') : '',	
        minWidth: 100	
    },	
    {	
        field: 'work|task|status',	
        label: 'Task Status',	
        minWidth: 100,	
        format: (value: number) => _.startCase(_.toLower(TaskStatus[value]))	
    },	
    {	
        field: 'work|task|description',	
        label: 'Task Title',	
        format: (value: string) => value ? (value.indexOf('---') !== -1 ? value.trim().substring(0, value.indexOf('---')): value.trim().substring(0, 100)) : '-',	
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
        field: 'utcStartTime',	
        label: 'Start Time',	
        minWidth: 100,	
        format: (value: string) => value ? dayjs.utc(value).toString() : '-'	
    },	
    {	
        field: 'utcEndTime',	
        label: 'End Time',	
        minWidth: 100,	
        format: (value: string) => value ? dayjs.utc(value).toString() : '-'	
    },	
    {	
        field: 'iterationsPerTask',	
        label: 'Iterations per task',	
        minWidth: 100,	
        tooltipField: 'averageIterationsPerTask'	
    },	
    {	
        field: 'userId',	
        label: 'Worker Id',	
        minWidth: 100,	
        tooltipField: 'workerName'	
    }	
];	

const useStyles = makeStyles({	
    root: {	
        width: '100%',	
        padding: 0	
    }	
});	

type Props = Record<string, never>;	

const DashboardContributorHistory: FunctionComponent<Props> = ({ }: Props) => {	
    const classes = useStyles();	
    const dispatch = useAppDispatch();	
    const location = useLocation();	

    const [ currentPage, setCurrentPage ] = useState(0);	
    const [ rowsPerPage, setRowsPerPage ] = useState(100);	

    const { contributorHistoryRows, totalContributorHistoryRows } = DashboardSelectors();	

    useEffect(() => {	
        if (location) {	
            const searchParams = new URLSearchParams(location.search.slice(1));	

            const userId = searchParams.get('userId');	
            if (userId) {	
                // load contributor history on mount	
                dispatch(	
                    fetchContributorHistoryRows({ userId, page: currentPage + 1, resultsPerPage: rowsPerPage })	
                );	
            }	
        }	
    }, [ location, dispatch, currentPage, rowsPerPage ]);	

    return (	
        <Paper className={classes.root}>	
            <DataTable	
                columns={columns}	
                rows={contributorHistoryRows}	
                totalRows={totalContributorHistoryRows}	
                currentPage={currentPage}	
                currentPageChanged={setCurrentPage}	
                rowsPerPage={rowsPerPage}	
                rowsPerPageChanged={setRowsPerPage}	
            />	
        </Paper>	
    );	
};	

export default DashboardContributorHistory;	
