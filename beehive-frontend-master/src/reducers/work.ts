import {
    createAsyncThunk,
    createEntityAdapter,
    createSlice,
    PayloadAction
} from '@reduxjs/toolkit';
import { useSelector } from 'react-redux';

import * as api from '../services/api';
import { RootState } from '../store';
import { initUserRatings, RatingSubject, UserRating, UserRatings } from '../types/rating';
import {
    WorkItem,
    WorkRecord,
    WorkReviewStatus,
    WorkType
} from '../types/work';

const workAdapter = createEntityAdapter();

interface WorkState {
    work: WorkItem | null;
    workLoading: boolean;
    workError: string | null;
    workFetched: boolean;
    workActionError: string | null;
    workActive: boolean;
    workStartTimeEpochMs: number;
    workRatings: UserRatings;
    workRatingAuthorizationCode: string | null;
    workRecordRatings: UserRatings;
    workRecordRatingAuthorizationCode: string | null;
    workDone: boolean;
    activeWorkRecord: WorkRecord | null;
    solutionUrl: string | null;
}

const initialState = workAdapter.getInitialState({
    work: null,
    workLoading: false,
    workError: null,
    workFetched: false,
    workActionError: null,
    workActive: false,
    workStartTimeEpochMs: 0,
    workRatings: {} as UserRatings,
    workRatingAuthorizationCode: null,
    workRecordRatings: {} as UserRatings,
    workRecordRatingAuthorizationCode: null,
    workDone: false,
    activeWorkRecord: null,
    solutionUrl: null
} as WorkState);

export const loadAvailableWork = createAsyncThunk(
    'work/loadAvailableWork',
    async (
        options: { currentWorkId?: number, specificWorkId?: number },
        { rejectWithValue }
    ) => {
        try {
            let fetchWorkResponse;

            if (options.specificWorkId) {
                fetchWorkResponse = await api.fetchSpecificWork(options.specificWorkId);
            } else {
                fetchWorkResponse = await api.fetchAvailableWork(options.currentWorkId);
            }

            return {
                work: fetchWorkResponse.work,
                workRecord: fetchWorkResponse.workRecord
            };
        } catch (err: any) {
            // 404 just means that there is no available work at the moment
            if (err.status === 404) {
                return { work: null };
            } else {
                return rejectWithValue(err);
            }
        }
    }
);

export const activateWork = createAsyncThunk(
    'work/activateWork',
    async (
        options: { workId: number, workType: WorkType, startTimeEpochMs: number, tzName: string },
        { rejectWithValue }
    ) => {
        try {
            return await api.startWork(
                options.workId, options.startTimeEpochMs, options.tzName
            );
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const skipWork = createAsyncThunk(
    'work/skipWork',
    async (
        options: { workId: number, startTimeEpochMs: number, tzName: string },
        { rejectWithValue }
    ) => {
        try {
            const skipResponse = await api.skipWork(
                options.workId, options.startTimeEpochMs, options.tzName
            );
            
            return skipResponse;
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const checkpointWork = createAsyncThunk(
    'work/checkpointWork',
    (options: {
        workId: number,
        durationSeconds: number
    }) => {
        return api.checkpointWork(
            options.workId,
            options.durationSeconds
        );
    }
);

export const cancelWork = createAsyncThunk(
    'work/cancelWork',
    async (options: { workId: number, durationSeconds: number }, { rejectWithValue }) => {
        try {
            // notify finish work with no parameters (aka cancelled)
            return await api.finishWork(
                options.workId,
                options.durationSeconds
            );
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const submitWorkSolution = createAsyncThunk(
    'work/submitWorkSolution',
    async (options: {
        workId: number,
        durationSeconds: number,
        reviewStatus?: WorkReviewStatus,
        reviewFeedback?: string,
        solutionUrl?: string
    }, { rejectWithValue }) => {
        try {
            return await api.finishWork(
                options.workId,
                options.durationSeconds,
                undefined,
                options.reviewStatus,
                options.reviewFeedback,
                options.solutionUrl
            );
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const submitWorkFeedback = createAsyncThunk(
    'work/submitWorkFeedback',
    async (options: {
        workId: number,
        durationSeconds: number,
        feedback: string
    }, { rejectWithValue }) => {
        try {
            return await api.finishWork(
                options.workId,
                options.durationSeconds,
                options.feedback
            );
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const submitWorkSolutionUrl = createAsyncThunk(
    'work/submitWorkSolutionUrl',
    async (options: {
        workId: number,
        durationSeconds: number,
        solutionUrl: string
    }, { rejectWithValue }) => {
        try {
            return await api.finishWork(
                options.workId,
                options.durationSeconds,
                undefined,
                undefined,
                undefined,
                options.solutionUrl
            );
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const submitWorkRating = createAsyncThunk(
    'work/submitWorkRating',
    async (options: {
        code: string,
        subject: RatingSubject,
        rating: UserRating
    }, { rejectWithValue }) => {
        try {
            return await api.updateRating(
                options.code,
                options.subject,
                options.rating
            );
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const analyzeWorkSolution = createAsyncThunk(
    'work/analyzeWorkSolution',
    async (options: {
        workId: number,
        solutionUrl: string
    }, { rejectWithValue }) => {
        try {
            return await api.analyzeWork(
                options.workId,
                options.solutionUrl
            );
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const submitWorkTypeCorrection = createAsyncThunk(
    'work/submitWorkTypeCorrection',
    async (options: {
        input: any,
        predictedOutput: string,
        correctedOutput: string
    }, { rejectWithValue }) => {
        try {
            return await api.updateWorkTypeClassification(
                options.input,
                options.predictedOutput,
                options.correctedOutput
            );
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const reviewWork = createAsyncThunk(
    'work/reviewWork',
    async (options: {
        workRecordId: number
    }, { rejectWithValue }) => {
        try {
            return await api.reviewWork(options.workRecordId);
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

const workSlice = createSlice({
    name: 'work',
    initialState,
    reducers: {
        clearAvailableWorkError(state) {
            state.workError = null;
        },
        clearWorkActionError(state) {
            state.workActionError = null;
        },
        setWorkActionError(state, action: PayloadAction<string>) {
            state.workActionError = action.payload;
        },
        setWorkRatings(state, action: PayloadAction<UserRatings>) {
            state.workRatings = action.payload;
        },
        setWorkRecordRatings(state, action: PayloadAction<UserRatings>) {
            state.workRecordRatings = action.payload;
        }
    },
    extraReducers: (builder) => {
        builder.addCase(loadAvailableWork.pending, (state) => {
            state.workLoading = true;
            state.workError = null;
        });
        builder.addCase(loadAvailableWork.fulfilled, (state, action: any) => {
            state.work = action.payload.work;
            state.workRatings = action.payload.work?.ratingSubjects ? initUserRatings(action.payload.work?.ratingSubjects): {} as UserRatings;
            state.workRatingAuthorizationCode = action.payload.work?.ratingAuthorizationCode;
            state.workLoading = false;
            state.workError = null;
            state.workActive = false;
            state.workDone = false;
            state.workFetched = true;
            state.activeWorkRecord = null;

            // activate work if a work record was fetched (meaning the user already has
            // an active work item)
            if (action.payload.workRecord) {
                state.activeWorkRecord = action.payload.workRecord;
                state.workStartTimeEpochMs = action.payload.workRecord.startTimeEpochMs;
                state.workActive = true;

                // override rating for this work record 
                if (action.payload.workRecord.ratingSubjects) {
                    state.workRecordRatings = initUserRatings(action.payload.workRecord.ratingSubjects);
                }
                if (action.payload.workRecord.ratingAuthorizationCode) {
                    state.workRecordRatingAuthorizationCode = action.payload.workRecord.ratingAuthorizationCode;
                }  
            }
        });
        builder.addCase(loadAvailableWork.rejected, (state, action: any) => {
            state.work = null;
            state.workLoading = false;
            state.workError = action.payload.error;
            state.workFetched = true;
            state.workRatings = {} as UserRatings;
            state.workRatingAuthorizationCode = null;
        });
        builder.addCase(activateWork.pending, (state) => {
            state.workLoading = true;
            state.workActionError = null;
        });
        builder.addCase(activateWork.fulfilled, (state, action) => {
            state.workLoading = false;
            state.workActive = true;
            state.workStartTimeEpochMs = action.meta.arg.startTimeEpochMs;
            
            if (action.payload.workRecord) {
                state.activeWorkRecord = action.payload.workRecord;

                if (state.work && action.payload.workRecord?.ratingSubjects && action.payload.workRecord?.ratingAuthorizationCode) {
                    state.workRecordRatings = initUserRatings(action.payload.workRecord.ratingSubjects);
                    state.workRecordRatingAuthorizationCode = action.payload.workRecord.ratingAuthorizationCode;
                }
            }
        });
        builder.addCase(activateWork.rejected, (state, action: any) => {
            state.workLoading = false;
            state.workActionError = action.payload.error;
        });
        /* we currently don't indicate that a checkpoint is taking place. maybe in the future */
        /*builder.addCase(checkpointWork.pending, (state) => {
        });
        builder.addCase(checkpointWork.fulfilled, (state) => {
        });
        builder.addCase(checkpointWork.rejected, (state) => {
        });*/
        builder.addCase(cancelWork.pending, (state) => {
            state.workLoading = true;
            state.workActionError = null;
        });
        builder.addCase(cancelWork.fulfilled, (state) => {
            state.workLoading = false;
            state.workActive = false;
            state.activeWorkRecord = null;
        });
        builder.addCase(cancelWork.rejected, (state, action: any) => {
            state.workLoading = false;
            state.workActionError = action.payload.error;
        });
        builder.addCase(submitWorkSolution.pending, (state) => {
            state.workLoading = true;
            state.workActionError = null;
        });
        builder.addCase(submitWorkSolution.fulfilled, (state) => {
            state.workLoading = false;
            state.workDone = true;
            state.activeWorkRecord = null;
        });
        builder.addCase(submitWorkSolution.rejected, (state, action: any) => {
            state.workLoading = false;
            state.workActionError = action.payload.error;
        });
        builder.addCase(submitWorkFeedback.pending, (state) => {
            state.workLoading = true;
            state.workActionError = null;
        });
        builder.addCase(submitWorkFeedback.fulfilled, (state) => {
            state.workLoading = false;
            state.workDone = true;
            state.workActive = false;
        });
        builder.addCase(submitWorkFeedback.rejected, (state, action: any) => {
            state.workLoading = false;
            state.workActionError = action.payload.error;
        });
        builder.addCase(submitWorkSolutionUrl.pending, (state) => {
            state.workLoading = true;
            state.workActionError = null;
        });
        builder.addCase(submitWorkSolutionUrl.fulfilled, (state) => {
            state.workLoading = false;
            state.workDone = true;
            state.workActive = false;
            state.activeWorkRecord = null;
        });
        builder.addCase(submitWorkSolutionUrl.rejected, (state, action: any) => {
            state.workLoading = false;
            state.workActionError = action.payload.error;
        });   
        builder.addCase(submitWorkRating.pending, (state) => {
            state.workLoading = true;
        });
        builder.addCase(submitWorkRating.fulfilled, (state) => {
            state.workLoading = false;
        });
        builder.addCase(submitWorkRating.rejected, (state) => {
            state.workLoading = false;
        });
        builder.addCase(skipWork.pending, (state) => {
            state.workLoading = true;
        });
        builder.addCase(skipWork.fulfilled, (state) => {
            state.workLoading = false;
        });
        builder.addCase(skipWork.rejected, (state) => {
            state.workLoading = false;
        });
        builder.addCase(submitWorkTypeCorrection.pending, (state) => {
            state.workLoading = true;
        });
        builder.addCase(submitWorkTypeCorrection.fulfilled, (state) => {
            state.workLoading = false;
        });
        builder.addCase(submitWorkTypeCorrection.rejected, (state, action: any) => {
            state.workActionError = action.payload.error;
        });
        builder.addCase(analyzeWorkSolution.pending, (state) => {
            state.workLoading = true;
        });
        builder.addCase(analyzeWorkSolution.rejected, (state, action : any) => {
            state.workLoading = false;
            if (action.payload.status === 429) {
                state.workActionError = 'analyze_no_changes';
            } else {
                state.workActionError = 'analyze_unexpected_error';
            }
        });
        builder.addCase(analyzeWorkSolution.fulfilled, (state, action) => {
            state.workLoading = false;
            if (state.activeWorkRecord) {
                state.activeWorkRecord.latestBeehaveReview = action.payload.review_content;
            }
        });
        builder.addCase(reviewWork.pending, (state) => {
            state.workLoading = true;
        });
        builder.addCase(reviewWork.rejected, (state, action : any) => {
            state.workLoading = false;
            if (action.payload.status === 404) {
                state.workActionError = 'review_work_record_not_found';
            } else if (action.payload.status === 400) {
                state.workActionError = 'review_work_unauthorized';
            } else {
                state.workActionError = 'review_unexpected_error';
            }
        });
        builder.addCase(reviewWork.fulfilled, (state, action) => {
            state.workLoading = false;
            state.solutionUrl = action.payload.solutionUrl;
        });
    }
});

export const {
    clearAvailableWorkError,
    clearWorkActionError,
    setWorkActionError,
    setWorkRatings,
    setWorkRecordRatings
} = workSlice.actions;

export default workSlice.reducer;

interface WorkSelectorsType {
    work: WorkItem | null;
    workLoading: boolean;
    workError: string | null;
    workFetched: boolean;
    workActionError: string | null;
    workActive: boolean;
    workStartTimeEpochMs: number;
    workRatings: UserRatings;
    workRatingAuthorizationCode: string;
    workRecordRatings: UserRatings;
    workRecordRatingAuthorizationCode: string;
    workDone: boolean;
    activeWorkRecord: WorkRecord;
    workRecordSolutionUrl: string;
}

export const WorkSelectors = (): WorkSelectorsType => {
    const work = useSelector(
        (state: RootState) => state.work.work
    );

    const workLoading = useSelector(
        (state: RootState) => state.work.workLoading
    );

    const workError = useSelector(
        (state: RootState) => state.work.workError
    );

    const workFetched = useSelector(
        (state: RootState) => state.work.workFetched
    );

    const workActionError = useSelector(
        (state: RootState) => state.work.workActionError
    );

    const workActive = useSelector(
        (state: RootState) => state.work.workActive
    );

    const workDone = useSelector(
        (state: RootState) => state.work.workDone
    );

    const workStartTimeEpochMs = useSelector(
        (state: RootState) => state.work.workStartTimeEpochMs
    );

    const workRatings = useSelector(
        (state: RootState) => state.work.workRatings
    );

    const workRatingAuthorizationCode = useSelector(
        (state: RootState) => state.work.workRatingAuthorizationCode
    );

    const workRecordRatings = useSelector(
        (state: RootState) => state.work.workRecordRatings
    );

    const workRecordRatingAuthorizationCode = useSelector(
        (state: RootState) => state.work.workRecordRatingAuthorizationCode
    );

    const activeWorkRecord = useSelector(
        (state: RootState) => state.work.activeWorkRecord
    );

    const workRecordSolutionUrl = useSelector(
        (state: RootState) => state.work.solutionUrl
    );

    return {
        work,
        workLoading,
        workError,
        workFetched,
        workActionError,
        workActive,
        workDone,
        workStartTimeEpochMs,
        workRatings,
        workRatingAuthorizationCode,
        workRecordRatings,
        workRecordRatingAuthorizationCode,
        activeWorkRecord,
        workRecordSolutionUrl
    };
};
