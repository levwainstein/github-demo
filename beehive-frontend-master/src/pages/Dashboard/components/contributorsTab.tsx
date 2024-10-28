import { Paper } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { History as HistoryIcon, Link as LinkIcon } from '@material-ui/icons';
import dayjs from 'dayjs';
import duration from 'dayjs/plugin/duration';
import relativeTime from 'dayjs/plugin/relativeTime';
import utc from 'dayjs/plugin/utc';
import { FunctionComponent, useEffect, useState } from 'react';
import { NavLink as Link } from 'react-router-dom';
import { useHash } from 'react-use';

import { useAppDispatch } from '../../../hooks';
import { DashboardSelectors, fetchContributorsRows } from '../../../reducers/dashboard';
import { CopyButton } from '../../../shared';
import DataTable, { DataTableColumn } from './dataTable';

// load dayjs duration and dependent plugin
dayjs.extend(duration);
dayjs.extend(relativeTime);
dayjs.extend(utc);

const columnsKeys: string[] = [
    'id', 
    'name',
    'activeWork',
    'numberOfReservedWorks',
    'numberOfWorksInReview',
    'numberOfCompletedWorks',
    'numberOfTotalWorks',
    'numberOfCancelledWorks',
    'numberOfSkippedWorks',
    'skippedTotalWorksRatio',
    'timeSinceLastEngagement',
    'timeSinceLastWork',
    'billableHoursAvailabilityRatio',
    'averageBillable',
    'weeklyAvailability',
    'averageGrossWorkDuration',
    'averageNetWorkDuration',
    'averageWorkPrice',
    'averageIterationsPerWork',
    'hourlyRate'
];

const suffixComponent = (key: string) => {
    return key === 'activeWork' ? function suffixSpecificLink(value: string) {
        return (
            value !== 'none' ? 
                <CopyButton
                    text={`${window.location.protocol}//${window.location.host}/?workId=${value}`}
                    copyIcon={<LinkIcon color="primary" />}
                    copyTooltip="Copy direct link to clipboard"
                /> : <div/>
        );
    } : key === 'id' ? function suffixContributorHistoryLink(value: string) {
        return (
            value !== 'none' ? 
                <Link to={ { pathname: '/dashboard/contributor-history', search: `?userId=${value}` } }>
                    <HistoryIcon />
                </Link> : <div/>
        );
    } : function emptyFunction() { 
        return <div/>;
    };
};

const viewType = (key:string) => {
    return key === 'billableHoursAvailabilityRatio' ? 'gauge' : 'label';
};

const tooltipHeader = (key:string) => {
    return key === 'averageBillable' ? 'average weekly hours spent, calculated from the work_record duration field' : key.split(/(?=[A-Z])/).map(s => s.toLowerCase()).join(' ');
};

const formatFunc = (key:string) => {
    if (key === 'timeSinceLastWork' || key === 'averageGrossWorkDuration' || key === 'averageNetWorkDuration' || key === 'timeSinceLastEngagement') {
        return (value: number) => value ? dayjs.duration(value, 'seconds').format('HH:mm:ss') : '-';
    }
    if (key === 'averageWorkPrice') {
        return (value: number) => value ? '$' + value : '-';
    }
    return (value: string) => value;
};

const columns: DataTableColumn[] = columnsKeys.map( key => ({
    field: key,
    label: key.split(/(?=[A-Z])/).map(s => s.toLowerCase()).join(' '),
    minWidth: 100,
    tooltipHeader: tooltipHeader(key),
    viewType: viewType(key),
    suffixComponent: suffixComponent(key),
    format: formatFunc(key)
}));

const TAB_ID = 'contributors';

const useStyles = makeStyles({
    root: {
        width: '100%',
        height: '100%'
    }
});

type Props = Record<string, never>;

const ContributorsTab: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();
    const [ hash, setHash ] = useHash();

    const { contributorsRows, totalContributorsRows } = DashboardSelectors();

    const [ currentPage, setCurrentPage ] = useState(0);
    const [ rowsPerPage, setRowsPerPage ] = useState(100);
    const [ projectFilter, setProjectFilter ] = useState<string | undefined>(undefined);

    useEffect(() => {
        // filter out empty hash parts (ie. '#/a/' splits into ['#', 'a', ''])
        const hashParts = hash.split('/').filter(p => p);

        // make sure this is the active tab
        if (hashParts.length < 1 || hashParts[1] !== TAB_ID) {
            return;
        }

        if (hashParts.length > 2) {
            setProjectFilter(hashParts[2]);
            setCurrentPage(0);
        } else {
            setProjectFilter(undefined);
        }
    }, [ hash, setProjectFilter, setCurrentPage ]);

    useEffect(() => {
        const fetchOptions: { page: number, resultsPerPage: number, filter?: {[key: string]: string} } = {
            page: currentPage + 1,
            resultsPerPage: rowsPerPage
        };

        if (projectFilter) {
            fetchOptions.filter = { project: projectFilter };
        }

        dispatch(fetchContributorsRows(fetchOptions));
    }, [ dispatch, currentPage, rowsPerPage, projectFilter ]);

    return (
        <Paper className={classes.root}>
            <DataTable
                columns={columns}
                rows={contributorsRows}
                totalRows={totalContributorsRows}
                currentPage={currentPage}
                currentPageChanged={setCurrentPage}
                rowsPerPage={rowsPerPage}
                rowsPerPageChanged={setRowsPerPage}
                onLinkClicked={(newHash) => setHash(newHash)}
            />
        </Paper>
    );
};

export default ContributorsTab;
