import { createAsyncThunk, createEntityAdapter, createSlice } from '@reduxjs/toolkit';
import { useSelector } from 'react-redux';

import * as api from '../services/api';
import * as authService from '../services/auth';
import { RootState } from '../store';

const authAdapter = createEntityAdapter();

interface AuthState {
    authLoading: boolean;
    authError: string | null;
}

const initialState = authAdapter.getInitialState({
    authLoading: false,
    authError: null
} as AuthState);

export const signUp = createAsyncThunk(
    'auth/signUp',
    async (options: {
        email: string, pass: string, code: string, firstName?: string, lastName?: string,
        githubUser?: string, trelloUser?: string, upworkUser?: string, 
        availabilityWeeklyHours?: number, pricePerHour?: number
    }, { rejectWithValue }) => {
        try {
            return await authService.signUp(
                options.email, options.pass, options.code, options.firstName, options.lastName,
                options.githubUser, options.trelloUser, options.upworkUser, options.availabilityWeeklyHours,
                options.pricePerHour
            );
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const signIn = createAsyncThunk(
    'auth/signIn',
    async (options: { email: string, pass: string }, { rejectWithValue }) => {
        try {
            return await authService.signIn(options.email, options.pass);
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const signOut = createAsyncThunk(
    'auth/signOut',
    async (_options: Record<string, never>, { rejectWithValue }) => {
        try {
            return await authService.signOut();
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const activateUser = createAsyncThunk(
    'auth/activateUser',
    async (options: { activationToken: string }) => {
        return await api.activateUser(options.activationToken);
    }
);

export const resendActivationEmail = createAsyncThunk(
    'auth/resendActivationEmail',
    async (options: { unactivatedAccessToken: string }) => {
        return await api.resendUserActivationEmail(options.unactivatedAccessToken);
    }
);

export const resetPassword = createAsyncThunk(
    'auth/resetPassword',
    async (options: { email: string }, { rejectWithValue }) => {
        try {
            return await api.resetPassword(options.email);
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const resetPasswordValidate = createAsyncThunk(
    'auth/resetPasswordValidate',
    async (options: { code: string }, { rejectWithValue }) => {
        try {
            // reset password change endpoint with no new password value is just a
            // code validation endpoint
            return await api.resetPasswordChange(options.code);
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

export const resetPasswordChange = createAsyncThunk(
    'auth/resetPasswordChange',
    async (options: { code: string, newPassword: string }, { rejectWithValue }) => {
        try {
            return await api.resetPasswordChange(options.code, options.newPassword);
        } catch (err) {
            return rejectWithValue(err);
        }
    }
);

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        clearAuthError(state) {
            state.authError = null;
        }
    },
    extraReducers: (builder) => {
        builder.addCase(signUp.pending, (state) => {
            state.authLoading = true;
            state.authError = null;
        });
        builder.addCase(signUp.fulfilled, (state) => {
            state.authLoading = false;
        });
        builder.addCase(signUp.rejected, (state, action: any) => {
            state.authLoading = false;
            state.authError = action.payload.error;
        });
        builder.addCase(signIn.pending, (state) => {
            state.authLoading = true;
            state.authError = null;
        });
        builder.addCase(signIn.fulfilled, (state) => {
            state.authLoading = false;
        });
        builder.addCase(signIn.rejected, (state, action: any) => {
            state.authLoading = false;
            state.authError = action.payload.error;
        });
        builder.addCase(signOut.pending, (state) => {
            state.authLoading = true;
            state.authError = null;
        });
        builder.addCase(signOut.fulfilled, (state) => {
            state.authLoading = false;
        });
        builder.addCase(signOut.rejected, (state, action: any) => {
            state.authLoading = false;
            state.authError = action.payload.error;
        });
        builder.addCase(activateUser.pending, (state) => {
            state.authLoading = true;
        });
        builder.addCase(activateUser.fulfilled, (state) => {
            state.authLoading = false;
        });
        builder.addCase(activateUser.rejected, (state) => {
            state.authLoading = false;
        });
        builder.addCase(resendActivationEmail.pending, (state) => {
            state.authLoading = true;
        });
        builder.addCase(resendActivationEmail.fulfilled, (state) => {
            state.authLoading = false;
        });
        builder.addCase(resendActivationEmail.rejected, (state) => {
            state.authLoading = false;
        });
    }
});

export const { clearAuthError } = authSlice.actions;

export default authSlice.reducer;

interface AuthSelectorsType {
    authLoading: boolean;
    authError: string | null;
}

export const AuthSelectors = (): AuthSelectorsType => {
    const authLoading = useSelector(
        (state: RootState) => state.auth.authLoading
    );

    const authError = useSelector(
        (state: RootState) => state.auth.authError
    );

    return {
        authLoading,
        authError
    };
};
