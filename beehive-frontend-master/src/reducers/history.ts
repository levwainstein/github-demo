import {
    createAsyncThunk,
    createEntityAdapter,
    createSlice
} from '@reduxjs/toolkit';
import { useSelector } from 'react-redux';

import * as api from '../services/api';
import { RootState } from '../store';
import { HistoryElement } from '../types/history';

const historyAdapter = createEntityAdapter();

interface HistoryState {
    historyLoading: boolean;
    historyError: string | null;
    completedWork: HistoryElement[] | null;
}

const initialState = historyAdapter.getInitialState({
    historyLoading: false,
    historyError: null,
    completedWork: null
} as HistoryState);

export const loadWorkHistory = createAsyncThunk(
    'history/loadWorkHistory',
    async (_options: Record<string, never>, { rejectWithValue }) => {
        try {
            return await api.fetchWorkHistory();
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

const historySlice = createSlice({
    name: 'history',
    initialState,
    reducers: {
        clearWorkHistoryError(state) {
            state.historyError = null;
        }
    },
    extraReducers: (builder) => {
        builder.addCase(loadWorkHistory.pending, (state) => {
            state.historyLoading = true;
            state.completedWork = null;
            state.historyError = null;
        });
        builder.addCase(loadWorkHistory.fulfilled, (state, action) => {
            state.historyLoading = false;
            state.completedWork = action.payload;
        });
        builder.addCase(loadWorkHistory.rejected, (state, action: any) => {
            state.historyLoading = false;
            state.historyError = action.payload.error;
        });
    }
});

export const { clearWorkHistoryError } = historySlice.actions;

export default historySlice.reducer;

interface HistorySelectorsType {
    historyLoading: boolean;
    historyError: string | null;
    completedWork: HistoryElement[] | null;
}

export const HistorySelectors = (): HistorySelectorsType => {

    const historyLoading = useSelector(
        (state: RootState) => state.history.historyLoading
    );

    const historyError = useSelector(
        (state: RootState) => state.history.workHistoryError
    );

    const completedWork = useSelector(
        (state: RootState) => state.history.completedWork
    );

    return {
        historyLoading,
        historyError,
        completedWork
    };
};

