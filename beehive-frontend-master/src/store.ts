import { configureStore } from '@reduxjs/toolkit';

import authReducer from './reducers/auth';
import contributorWorkReducer from './reducers/contributorWork';
import dashboardReducer from './reducers/dashboard';
import generalReducer from './reducers/general';
import historyReducer from './reducers/history';
import userReducer from './reducers/user';
import workReducer from './reducers/work';

// define store options as a variable so we can export it for tests to use
const storeOptions: any = {
    reducer: {
        auth: authReducer,
        dashboard: dashboardReducer,
        general: generalReducer,
        history: historyReducer,
        user: userReducer,
        work: workReducer,
        contributorWork: contributorWorkReducer
    }
};

const store = configureStore(storeOptions);

export default store;

// infer the `RootState` type from the store
export type RootState = ReturnType<typeof store.getState>;

// infer the `AppDispatch` type from the store so thunk actions can return promises
export type AppDispatch = typeof store.dispatch;

export const test = {
    storeOptions
};
