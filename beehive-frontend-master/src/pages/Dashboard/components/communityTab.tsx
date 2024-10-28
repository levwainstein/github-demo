import { Paper } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { FunctionComponent, useEffect, useState } from 'react';

import { useAppDispatch } from '../../../hooks';
import { DashboardSelectors, fetchCommunityRows } from '../../../reducers/dashboard';
import DataTable, { DataTableColumn } from './dataTable';

const columns: DataTableColumn[] = [
    {
        field: 'userId',
        label: 'ID',
        minWidth: 100
    },
    {
        field: 'email',
        label: 'Email',
        minWidth: 100
    },
    {
        field: 'name',
        label: 'Name',
        minWidth: 100
    },
    {
        field: 'githubUser',
        label: 'Github User',
        minWidth: 100
    },
    {
        field: 'trelloUser',
        label: 'Trello User',
        minWidth: 100
    },
    {
        field: 'upworkUser',
        label: 'Upwork User',
        minWidth: 100
    },
    {
        field: 'admin',
        label: 'Is Admin',
        minWidth: 30,
        format: (value: boolean) => value ? 'V' : ''
    },
    {
        field: 'availabilityWeeklyHours',
        label: 'Availablity (Weekly Hours)',
        minWidth: 100
    },
    {
        field: 'pricePerHour',
        label: 'Price per Hour',
        minWidth: 100,
        format: (value: number) => value ? `$${value}` : ''
    },
    {
        field: 'tags',
        label: 'Tags',
        minWidth: 100,
        format: (value: []) => value.length > 0 ? value.join('\n') : ''
    },
    {
        field: 'skills',
        label: 'Skills',
        minWidth: 100,
        format: (value: []) => value.length > 0 ? value.join('\n') : ''
    }
];

const useStyles = makeStyles({
    root: {
        width: '100%'
    }
});

type Props = Record<string, never>;

const CommunityTab: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();

    const { communityRows, totalCommunityRows } = DashboardSelectors();

    const [ currentPage, setCurrentPage ] = useState(0);
    const [ rowsPerPage, setRowsPerPage ] = useState(100);

    useEffect(() => {
        dispatch(fetchCommunityRows({ page: currentPage + 1, resultsPerPage: rowsPerPage }));
    }, [ dispatch, currentPage, rowsPerPage ]);

    return (
        <Paper className={classes.root}>
            <DataTable
                columns={columns}
                rows={communityRows}
                totalRows={totalCommunityRows}
                currentPage={currentPage}
                currentPageChanged={setCurrentPage}
                rowsPerPage={rowsPerPage}
                rowsPerPageChanged={setRowsPerPage}
            />
        </Paper>
    );
};

export default CommunityTab;
