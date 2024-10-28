import {
    createAsyncThunk,
    createEntityAdapter,
    createSlice
} from '@reduxjs/toolkit';
import { useSelector } from 'react-redux';

import * as api from '../services/api';
import { RootState } from '../store';
import { UserProfile } from '../types/user';

const userAdapter = createEntityAdapter();

interface UserState {
    profile: UserProfile | null;
    profileLoading: boolean;
    availableSkills: string[];
}

const initialState = userAdapter.getInitialState({
    profile: null,
    profileLoading: false,
    availableSkills: []
} as UserState);

export const loadUserProfile = createAsyncThunk(
    'user/loadUserProfile',
    async (_options: Record<string, never>, { rejectWithValue }) => {
        try {
            return await api.fetchUserProfile();
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const loadAvailableSkills = createAsyncThunk(
    'user/loadAvailableSkills',
    async (_options: Record<string, never>, { rejectWithValue }) => {
        try {
            return await api.fetchAvailableSkills();
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const updateUserProfile = createAsyncThunk(
    'user/updateUserProfile',
    async (options: {
        email?: string,
        firstName?: string,
        lastName?: string,
        githubUser?: string,
        trelloUser?: string,
        upworkUser?: string,
        availabilityWeeklyHours?: number,
        pricePerHour?: number,
        skills?: string[]
    }, { rejectWithValue }) => {
        try {
            return await api.updateUserProfile(
                options.email,
                options.firstName,
                options.lastName,
                options.githubUser,
                options.trelloUser,
                options.upworkUser,
                options.availabilityWeeklyHours,
                options.pricePerHour,
                options.skills
            );
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

const userSlice = createSlice({
    name: 'user',
    initialState,
    reducers: {},
    extraReducers: (builder) => {
        builder.addCase(loadUserProfile.pending, (state) => {
            state.profileLoading = true;
            state.profile = null;
        });
        builder.addCase(loadUserProfile.fulfilled, (state, action) => {
            state.profileLoading = false;
            state.profile = action.payload;
        });
        builder.addCase(loadUserProfile.rejected, (state) => {
            state.profileLoading = false;
        });
        builder.addCase(loadAvailableSkills.pending, (state) => {
            state.profileLoading = true;
            state.availableSkills = [];
        });
        builder.addCase(loadAvailableSkills.fulfilled, (state, action) => {
            state.profileLoading = false;
            state.availableSkills = action.payload.map((skill) => skill.name);
        });
        builder.addCase(loadAvailableSkills.rejected, (state) => {
            state.profileLoading = false;
        });
        builder.addCase(updateUserProfile.pending, (state) => {
            state.profileLoading = true;
        });
        builder.addCase(updateUserProfile.fulfilled, (state) => {
            state.profileLoading = false;
        });
        builder.addCase(updateUserProfile.rejected, (state) => {
            state.profileLoading = false;
        });
    }
});

export default userSlice.reducer;

interface UserSelectorsType {
    profile: UserProfile | null;
    profileLoading: boolean;
    availableSkills: string[];
}

export const UserSelectors = (): UserSelectorsType => {
    const profile = useSelector(
        (state: RootState) => state.user.profile
    );

    const profileLoading = useSelector(
        (state: RootState) => state.user.profileLoading
    );

    const availableSkills = useSelector(
        (state: RootState) => state.user.availableSkills
    );

    return {
        profile,
        profileLoading,
        availableSkills
    };
};
