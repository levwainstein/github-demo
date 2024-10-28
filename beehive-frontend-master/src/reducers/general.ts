import { createAsyncThunk, createEntityAdapter, createSlice } from '@reduxjs/toolkit';
import { useSelector } from 'react-redux';

import * as api from '../services/api';
import { sleep, testUrl } from '../services/utils';
import { RootState } from '../store';

const generalAdapter = createEntityAdapter();

interface GeneralState {
    reportBugLoading: boolean;
    reportBugError: boolean;
    reportBugSuccess: boolean;
}

const initialState = generalAdapter.getInitialState({
    reportBugLoading: false,
    reportBugError: false,
    reportBugSuccess: false
} as GeneralState);

export const sendBugReport = createAsyncThunk(
    'general/sendBugReport',
    async (options: { taskId: string, details: string }) => {
        return await api.sendBugReport(options.taskId, options.details);
    }
);

export const waitForUrl = createAsyncThunk(
    'general/waitForUrl',
    async (url: string) => {
        let success = false;
        let attempts = 10;

        while (!success && attempts > 0) {
            attempts--;

            try {
                await testUrl(url);
                success = true;
            } catch {
                await sleep(3000);
            }
        }

        return Promise.resolve(success);
    }
);

const generalSlice = createSlice({
    name: 'general',
    initialState,
    reducers: {
        clearReportBugError(state) {
            state.reportBugError = false;
        },
        clearReportBugSuccess(state) {
            state.reportBugSuccess = false;
        }
    },
    extraReducers: (builder) => {
        builder.addCase(sendBugReport.pending, (state) => {
            state.reportBugLoading = true;
            state.reportBugError = false;
            state.reportBugSuccess = false;
        });
        builder.addCase(sendBugReport.fulfilled, (state) => {
            state.reportBugLoading = false;
            state.reportBugSuccess = true;
        });
        builder.addCase(sendBugReport.rejected, (state) => {
            state.reportBugLoading = false;
            state.reportBugError = true;
        });
    }
});

export const { clearReportBugError, clearReportBugSuccess } = generalSlice.actions;

export default generalSlice.reducer;

interface GeneralSelectorsType {
    isReportBugLoading: boolean;
    isReportBugError: boolean;
    isReportBugSuccess: boolean;
}

export const GeneralSelectors = (): GeneralSelectorsType => {
    const isReportBugLoading = useSelector(
        (state: RootState) => state.general.reportBugLoading
    );

    const isReportBugError = useSelector(
        (state: RootState) => state.general.reportBugError
    );

    const isReportBugSuccess = useSelector(
        (state: RootState) => state.general.reportBugSuccess
    );

    return {
        isReportBugLoading,
        isReportBugError,
        isReportBugSuccess
    };
};
