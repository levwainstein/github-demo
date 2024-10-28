import { Paper } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { FunctionComponent, useEffect, useState } from 'react';

import { useAppDispatch } from '../../../hooks';
import { DashboardSelectors, fetchHoneycombRows } from '../../../reducers/dashboard';
import DataTable, { DataTableColumn } from './dataTable';

const columns: DataTableColumn[] = [
    {
        field: 'id',
        label: 'ID',
        minWidth: 100
    },
    {
        field: 'name',
        label: 'Name',
        minWidth: 100
    },
    {
        field: 'description',
        label: 'Description',
        minWidth: 100
    },
    {
        field: 'version',
        label: 'Version',
        minWidth: 100
    },
    {
        field: 'packageDependencyNames',
        label: 'Package Dependencies',
        minWidth: 100,
        format: (value: string[]) => value.join(', ')
    },
    {
        field: 'honeycombDependencyNames',
        label: 'Honeycomb Dependencies',
        minWidth: 100,
        format: (value: string[]) => value.join(', ')
    }
];

const useStyles = makeStyles({
    root: {
        width: '100%'
    }
});

type Props = Record<string, never>;

const HoneycombTab: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();

    const { honeycombRows, totalHoneycombRows } = DashboardSelectors();

    const [ currentPage, setCurrentPage ] = useState(0);
    const [ rowsPerPage, setRowsPerPage ] = useState(25);

    useEffect(() => {
        dispatch(fetchHoneycombRows({ page: currentPage + 1, resultsPerPage: rowsPerPage }));
    }, [ dispatch, currentPage, rowsPerPage ]);

    return (
        <Paper className={classes.root}>
            <DataTable
                columns={columns}
                rows={honeycombRows}
                totalRows={totalHoneycombRows}
                currentPage={currentPage}
                currentPageChanged={setCurrentPage}
                rowsPerPage={rowsPerPage}
                rowsPerPageChanged={setRowsPerPage}
            />
        </Paper>
    );
};

export default HoneycombTab;
