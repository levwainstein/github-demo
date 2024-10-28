import { createAsyncThunk, createEntityAdapter, createSlice } from '@reduxjs/toolkit';
import { useSelector } from 'react-redux';

import * as api from '../services/api';
import { RootState } from '../store';
import {
    DashboardCommunityMember,
    DashboardContributorHistoryItem,
    DashboardContributorsItem,
    DashboardHoneycomb,
    DashboardTask,
    DashboardWorkItem,
    DashboardWorkRecord
} from '../types/dashboard';

const dashboardAdapter = createEntityAdapter();

interface DashboardState {
    loading: boolean;
    error: boolean;
    activeRows: DashboardWorkRecord[];
    totalActiveRows: number;
    pendingRows: DashboardWorkItem[];
    totalPendingRows: number;
    completedRows: DashboardWorkItem[];
    totalCompletedRows: number;
    invalidRows: DashboardTask[];
    totalInvalidRows: number;
    communityRows: DashboardCommunityMember[];
    totalCommunityRows: number;
    honeycombRows: DashboardHoneycomb[];
    totalHoneycombRows: number;
    contributorsRows: DashboardContributorsItem[];
    totalContributorsRows: number;
    contributorHistoryRows: DashboardContributorHistoryItem[];
    totalContributorHistoryRows: number;
}

const initialState = dashboardAdapter.getInitialState({
    loading: false,
    error: false,
    activeRows: [],
    totalActiveRows: 0,
    pendingRows: [],
    totalPendingRows: 0,
    completedRows: [],
    totalCompletedRows: 0,
    invalidRows: [],
    totalInvalidRows: 0,
    communityRows: [],
    totalCommunityRows: 0,
    honeycombRows: [],
    totalHoneycombRows: 0,
    contributorsRows: [],
    totalContributorsRows: 0,
    contributorHistoryRows: [],
    totalContributorHistoryRows: 0
} as DashboardState);

export const fetchActiveRows = createAsyncThunk(
    'dashboard/fetchActiveRows',
    async (options: {page: number, resultsPerPage: number}) => {
        return await api.fetchDashboardActiveWork(options.page, options.resultsPerPage);
    }
);

export const fetchPendingRows = createAsyncThunk(
    'dashboard/fetchPendingRows',
    async (options: {page: number, resultsPerPage: number}) => {
        return await api.fetchDashboardPendingWork(options.page, options.resultsPerPage);
    }
);

export const fetchCompletedRows = createAsyncThunk(
    'dashboard/fetchCompletedRows',
    async (options: {page: number, resultsPerPage: number, filter?: {[key: string]: string}}) => {
        return await api.fetchDashboardCompletedWork(
            options.page, options.resultsPerPage, options.filter
        );
    }
);

export const fetchInvalidRows = createAsyncThunk(
    'dashboard/fetchInvalidRows',
    async (options: {page: number, resultsPerPage: number}) => {
        return await api.fetchDashboardInvalidTasks(options.page, options.resultsPerPage);
    }
);

export const fetchCommunityRows = createAsyncThunk(
    'dashboard/fetchCommunityRows',
    async (options: {page: number, resultsPerPage: number}) => {
        return await api.fetchDashboardCommunity(options.page, options.resultsPerPage);
    }
);

export const fetchHoneycombRows = createAsyncThunk(
    'dashboard/fetchHoneycombRows',
    async (options: {page: number, resultsPerPage: number}) => {
        return await api.fetchDashboardHoneycombs(options.page, options.resultsPerPage);
    }
);

export const reserveWork = createAsyncThunk(
    'dashboard/reserveWork',
    async (options: { workId: number, userId: string}, { rejectWithValue }) => {
        try {
            return await api.reserveWork(options.workId, options.userId);
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const dismissWorkReservation = createAsyncThunk(
    'dashboard/dismissWorkReservation',
    async (options: { workId: number, userId: string}, { rejectWithValue }) => {
        try {
            return await api.dismissWorkReservation(options.workId, options.userId);
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const fetchContributorsRows = createAsyncThunk(
    'dashboard/fetchContributorsRows',
    async (options: {page: number, resultsPerPage: number, filter?: {[key: string]: string}}) => {
        return await api.fetchDashboardContributors(
            options.page, options.resultsPerPage, options.filter
        );
    }
);

export const fetchContributorHistoryRows = createAsyncThunk(
    'dashboard/fetchContributorHistoryRows',
    async (options: {userId: string, page: number, resultsPerPage: number}) => {
        return await api.fetchDashboardContributorHistory(
            options.userId, options.page, options.resultsPerPage
        );
    }
);

export const prohibitWork = createAsyncThunk(
    'dashboard/prohibitWork',
    async (options: { workId: number, userId: string}, { rejectWithValue }) => {
        try {
            return await api.prohibitWork(options.workId, options.userId);
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const dismissWorkProhibition = createAsyncThunk(
    'dashboard/dismissWorkProhibition',
    async (options: { workId: number, userId: string}, { rejectWithValue }) => {
        try {
            return await api.dismissWorkProhibition(options.workId, options.userId);
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const updateWorkPriority = createAsyncThunk(
    'task/updateWorkPriority',
    async (options: {
        workId: number,
        priority: number
    }, { rejectWithValue }) => {
        try {
            return await api.updateWorkPriority(
                options.workId,
                options.priority
            );
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

const dashboardSlice = createSlice({
    name: 'dashboard',
    initialState,
    reducers: {
        clearError(state) {
            state.error = false;
        }
    },
    extraReducers: (builder) => {
        builder.addCase(fetchActiveRows.pending, (state) => {
            state.loading = true;
            state.error = false;
        });
        builder.addCase(fetchActiveRows.fulfilled, (state, action) => {
            state.loading = false;
            state.error = false;

            state.totalActiveRows = action.payload.totalCount;

            // requests with 0 results per page are made only to receive the total count
            if (action.meta.arg.resultsPerPage > 0) {
                // remove all existing rows and push all fetched rows
                state.activeRows.splice(0, state.activeRows.length);
                state.activeRows.push(...action.payload.work);
            }
        });
        builder.addCase(fetchActiveRows.rejected, (state) => {
            state.loading = false;
            state.error = true;
        });
        builder.addCase(fetchPendingRows.pending, (state) => {
            state.loading = true;
            state.error = false;
        });
        builder.addCase(fetchPendingRows.fulfilled, (state, action) => {
            state.loading = false;
            state.error = false;

            state.totalPendingRows = action.payload.totalCount;

            // requests with 0 results per page are made only to receive the total count
            if (action.meta.arg.resultsPerPage > 0) {
                // remove all existing rows and push all fetched rows
                state.pendingRows.splice(0, state.pendingRows.length);
                state.pendingRows.push(...action.payload.work);
            }
        });
        builder.addCase(fetchPendingRows.rejected, (state) => {
            state.loading = false;
            state.error = true;
        });
        builder.addCase(fetchCompletedRows.pending, (state) => {
            state.loading = true;
            state.error = false;
        });
        builder.addCase(fetchCompletedRows.fulfilled, (state, action) => {
            state.loading = false;
            state.error = false;

            state.totalCompletedRows = action.payload.totalCount;

            // requests with 0 results per page are made only to receive the total count
            if (action.meta.arg.resultsPerPage > 0) {
                // remove all existing rows and push all fetched rows
                state.completedRows.splice(0, state.completedRows.length);
                state.completedRows.push(...action.payload.work);
            }
        });
        builder.addCase(fetchCompletedRows.rejected, (state) => {
            state.loading = false;
            state.error = true;
        });
        builder.addCase(fetchInvalidRows.pending, (state) => {
            state.loading = true;
            state.error = false;
        });
        builder.addCase(fetchInvalidRows.fulfilled, (state, action) => {
            state.loading = false;
            state.error = false;

            state.totalInvalidRows = action.payload.totalCount;

            // requests with 0 results per page are made only to receive the total count
            if (action.meta.arg.resultsPerPage > 0) {
                // remove all existing rows and push all fetched rows
                state.invalidRows.splice(0, state.invalidRows.length);
                state.invalidRows.push(...action.payload.tasks);
            }
        });
        builder.addCase(fetchInvalidRows.rejected, (state) => {
            state.loading = false;
            state.error = true;
        });
        builder.addCase(fetchCommunityRows.pending, (state) => {
            state.loading = true;
            state.error = false;
        });
        builder.addCase(fetchCommunityRows.fulfilled, (state, action) => {
            state.loading = false;
            state.error = false;

            state.totalCommunityRows = action.payload.totalCount;

            // requests with 0 results per page are made only to receive the total count
            if (action.meta.arg.resultsPerPage > 0) {
                // remove all existing rows and push all fetched rows
                state.communityRows.splice(0, state.communityRows.length);
                state.communityRows.push(...action.payload.users);
            }
        });
        builder.addCase(fetchCommunityRows.rejected, (state) => {
            state.loading = false;
            state.error = true;
        });
        builder.addCase(fetchHoneycombRows.pending, (state) => {
            state.loading = true;
            state.error = false;
        });
        builder.addCase(fetchHoneycombRows.fulfilled, (state, action) => {
            state.loading = false;
            state.error = false;

            state.totalHoneycombRows = action.payload.totalCount;

            // requests with 0 results per page are made only to receive the total count
            if (action.meta.arg.resultsPerPage > 0) {
                // remove all existing rows and push all fetched rows
                state.honeycombRows.splice(0, state.honeycombRows.length);
                state.honeycombRows.push(...action.payload.honeycombs);
            }
        });
        builder.addCase(fetchHoneycombRows.rejected, (state) => {
            state.loading = false;
            state.error = true;
        });
        builder.addCase(reserveWork.pending, (state) => {
            state.loading = true;
        });
        builder.addCase(reserveWork.fulfilled, (state) => {
            state.loading = false;
        });
        builder.addCase(reserveWork.rejected, (state) => {
            state.loading = false;
        });
        builder.addCase(dismissWorkReservation.pending, (state) => {
            state.loading = true;
        });
        builder.addCase(dismissWorkReservation.fulfilled, (state) => {
            state.loading = false;
        });
        builder.addCase(dismissWorkReservation.rejected, (state) => {
            state.loading = false;
        });
        builder.addCase(fetchContributorsRows.fulfilled, (state, action) => {
            state.loading = false;
            state.error = false;

            state.totalContributorsRows = action.payload.totalCount;

            // requests with 0 results per page are made only to receive the total count
            if (action.meta.arg.resultsPerPage > 0) {
                // remove all existing rows and push all fetched rows
                state.contributorsRows.splice(0, state.contributorsRows.length);
                state.contributorsRows.push(...action.payload.data);
            }
        });
        builder.addCase(fetchContributorsRows.rejected, (state) => {
            state.loading = false;
            state.error = true;
        });
        builder.addCase(fetchContributorsRows.pending, (state) => {
            state.loading = true;
            state.error = false;
        });
        builder.addCase(fetchContributorHistoryRows.fulfilled, (state, action) => {
            state.loading = false;
            state.error = false;

            state.totalContributorHistoryRows = action.payload.totalCount;

            // requests with 0 results per page are made only to receive the total count
            if (action.meta.arg.resultsPerPage > 0) {
                // remove all existing rows and push all fetched rows
                state.contributorHistoryRows.splice(0, state.contributorHistoryRows.length);
                state.contributorHistoryRows.push(...action.payload.work);
            }
        });
        builder.addCase(fetchContributorHistoryRows.rejected, (state) => {
            state.loading = false;
            state.error = true;
        });
        builder.addCase(fetchContributorHistoryRows.pending, (state) => {
            state.loading = true;
            state.error = false;
        });        
        builder.addCase(updateWorkPriority.pending, (state) => {
            state.loading = true;
        });
        builder.addCase(updateWorkPriority.fulfilled, (state, action) => {
            state.loading = false;
            if (action.meta.arg.workId) {
                state.pendingRows = state.pendingRows.map(row => {
                    if (row.id === action.meta.arg.workId) {
                        return {
                            ...row, priority: action.meta.arg.priority
                        };
                    }
                    return row;
                });
            }
        });
        builder.addCase(updateWorkPriority.rejected, (state) => {
            state.loading = false;
        });
    }
});

export const { clearError } = dashboardSlice.actions;

export default dashboardSlice.reducer;

interface DashboardSelectorsType {
    isLoading: boolean;
    isError: boolean;
    activeWorkRows: DashboardWorkRecord[];
    totalActiveWorkRows: number;
    pendingWorkRows: DashboardWorkItem[];
    totalPendingWorkRows: number;
    completedWorkRows: DashboardWorkItem[];
    totalCompletedWorkRows: number;
    invalidTaskRows: DashboardTask[];
    totalInvalidTaskRows: number;
    communityRows: DashboardCommunityMember[];
    totalCommunityRows: number;
    honeycombRows: DashboardHoneycomb[];
    totalHoneycombRows: number;
    contributorsRows: DashboardContributorsItem[];
    totalContributorsRows: number;
    contributorHistoryRows: DashboardContributorHistoryItem[];
    totalContributorHistoryRows: number;
}

export const DashboardSelectors = (): DashboardSelectorsType => {
    const isLoading = useSelector(
        (state: RootState) => state.dashboard.loading
    );

    const isError = useSelector(
        (state: RootState) => state.dashboard.error
    );

    const activeWorkRows = useSelector(
        (state: RootState) => state.dashboard.activeRows
    );

    const totalActiveWorkRows = useSelector(
        (state: RootState) => state.dashboard.totalActiveRows
    );

    const pendingWorkRows = useSelector(
        (state: RootState) => state.dashboard.pendingRows
    );

    const totalPendingWorkRows = useSelector(
        (state: RootState) => state.dashboard.totalPendingRows
    );

    const completedWorkRows = useSelector(
        (state: RootState) => state.dashboard.completedRows
    );

    const totalCompletedWorkRows = useSelector(
        (state: RootState) => state.dashboard.totalCompletedRows
    );

    const invalidTaskRows = useSelector(
        (state: RootState) => state.dashboard.invalidRows
    );

    const totalInvalidTaskRows = useSelector(
        (state: RootState) => state.dashboard.totalInvalidRows
    );

    const communityRows = useSelector(
        (state: RootState) => state.dashboard.communityRows
    );

    const totalCommunityRows = useSelector(
        (state: RootState) => state.dashboard.totalCommunityRows
    );

    const honeycombRows = useSelector(
        (state: RootState) => state.dashboard.honeycombRows
    );

    const totalHoneycombRows = useSelector(
        (state: RootState) => state.dashboard.totalHoneycombRows
    );

    const contributorsRows = useSelector(
        (state: RootState) => state.dashboard.contributorsRows
    );
    
    const totalContributorsRows = useSelector(
        (state: RootState) => state.dashboard.totalContributorsRows
    );

    const contributorHistoryRows = useSelector(
        (state: RootState) => state.dashboard.contributorHistoryRows
    );
    
    const totalContributorHistoryRows = useSelector(
        (state: RootState) => state.dashboard.totalContributorHistoryRows
    );

    return {
        isLoading,
        isError,
        activeWorkRows,
        totalActiveWorkRows,
        pendingWorkRows,
        totalPendingWorkRows,
        completedWorkRows,
        totalCompletedWorkRows,
        invalidTaskRows,
        totalInvalidTaskRows,
        communityRows,
        totalCommunityRows,
        honeycombRows,
        totalHoneycombRows,
        contributorsRows,
        totalContributorsRows,
        contributorHistoryRows,
        totalContributorHistoryRows
    };
};
