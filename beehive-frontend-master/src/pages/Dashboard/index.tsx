import { AppBar, Snackbar, Tab, Tabs } from '@material-ui/core';
import { FunctionComponent, useEffect, useState } from 'react';
import { useHash } from 'react-use';

import { useAppDispatch } from '../../hooks';
import {
    clearError,
    DashboardSelectors,
    fetchActiveRows,
    fetchCommunityRows,
    fetchCompletedRows,
    fetchContributorsRows,
    fetchHoneycombRows,
    fetchInvalidRows,
    fetchPendingRows
} from '../../reducers/dashboard';
import { Wrapper } from '../../shared';
import {
    ActiveWorkTab,
    CommunityTab,
    CompletedWorkTab,
    ContributorsTab,
    HoneycombTab,
    InvalidTaskTab,
    PendingWorkTab
} from './components';

const tabs = [
    {
        id: 'active',
        title: 'Active Work',
        component: <ActiveWorkTab />,
        countFunc: () => DashboardSelectors().totalActiveWorkRows
    },
    {
        id: 'pending',
        title: 'Pending Work',
        component: <PendingWorkTab />,
        countFunc: () => DashboardSelectors().totalPendingWorkRows
    },
    {
        id: 'completed',
        title: 'Completed Work',
        component: <CompletedWorkTab />,
        countFunc: () => DashboardSelectors().totalCompletedWorkRows
    },
    {
        id: 'invalid',
        title: 'Invalid Tasks',
        component: <InvalidTaskTab />,
        countFunc: () => DashboardSelectors().totalInvalidTaskRows
    },
    {
        id: 'community',
        title: 'Community',
        component: <CommunityTab />,
        countFunc: () => DashboardSelectors().totalCommunityRows
    },
    {
        id: 'honeycomb',
        title: 'Honeycombs',
        component: <HoneycombTab />,
        countFunc: () => DashboardSelectors().totalHoneycombRows
    },
    {
        id: 'contributors',
        title: 'Contributors',
        component: <ContributorsTab />,
        countFunc: () => DashboardSelectors().totalContributorsRows
    }
];

type Props = Record<string, never>;

const Dashboard: FunctionComponent<Props> = ({}: Props) => {
    const dispatch = useAppDispatch();
    const [ hash, setHash ] = useHash();

    const { isLoading, isError } = DashboardSelectors();

    const [ selectedTab, setSelectedTab ] = useState(0);

    useEffect(() => {
        // filter out empty hash parts (ie. '#/a/' splits into ['#', 'a', ''])
        const hashParts = hash.split('/').filter(p => p);

        if (hashParts.length > 0) {
            for (let i = 0; i < tabs.length; i++) {
                if (tabs[i].id === hashParts[1]) {
                    setSelectedTab(i);
                    return;
                }
            }
        }

        // tab was not found so set hash to first tab's id
        setHash(`/${tabs[0].id}`);
    }, [ hash, setHash, setSelectedTab ]);

    const handleSelectedTabChange = (_, newValue: number) => {
        setHash(`/${tabs[newValue].id}`);
    };

    useEffect(() => {
        // load all types of rows to get total counts
        dispatch(fetchActiveRows({ page: 1, resultsPerPage: 0 }));
        dispatch(fetchPendingRows({ page: 1, resultsPerPage: 0 }));
        dispatch(fetchCompletedRows({ page: 1, resultsPerPage: 0 }));
        dispatch(fetchInvalidRows({ page: 1, resultsPerPage: 0 }));
        dispatch(fetchCommunityRows({ page: 1, resultsPerPage: 0 }));
        dispatch(fetchHoneycombRows({ page: 1, resultsPerPage: 0 }));
        dispatch(fetchContributorsRows({ page: 1, resultsPerPage: 0 }));
    }, [ dispatch ]);

    return (
        <Wrapper loading={isLoading}>
            <AppBar position="static" color="default">
                <Tabs
                    value={selectedTab}
                    onChange={handleSelectedTabChange}
                    indicatorColor="primary"
                    variant="fullWidth"
                >
                    {tabs.map((tab, i) => (
                        <Tab
                            label={`${tab.title} (${tab.countFunc()})`}
                            id={`dashboard-tab-${i}`}
                            key={`dashboard-tab-${i}`}
                            aria-controls={`dashboard-tabpanel-${i}`}
                        />
                    ))}
                </Tabs>
                {tabs[selectedTab].component}
            </AppBar>
            <Snackbar
                open={!!isError}
                autoHideDuration={4000}
                onClose={() => dispatch(clearError())}
                message="Woops! Not sure what happened there... Please try again"
            />
        </Wrapper>
    );
};

export default Dashboard;
