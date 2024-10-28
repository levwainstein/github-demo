import {
    createEntityAdapter,
    createSlice
} from '@reduxjs/toolkit';
import { useSelector } from 'react-redux';

import { RootState } from '../store';
import { WorkItem } from '../types/work';

const workAdapter = createEntityAdapter();

interface ContributorWorkState {
    pendingWork: WorkItem[]
}

const initialState = workAdapter.getInitialState({
    pendingWork: [
        {
            id: 1,
            created: '23-10-2023 12:00:00',
            taskId: '1',
            taskType: 'Create a component',
            skills: [ 'React' ],
            task: {
                id: '11',
                functionName: 'create login page',
                status: 1
            },
            status: 1,
            workType: 1,
            priority: 1,
            description: 'In this task, you need to implement the skip functionality on the “contributor-work” route of our application. Please setup a reducer and get multiple tasks form there to show on the “contributor-rote”. Currently we are showing only one task on the page. By clicking the skip user will get the next task in the list.',
            workInput: {
                code: 'def test(x):\n    pass',
                context: {
                    class_functions: [],
                    docstrings: {},
                    functions: [],
                    imports: [],
                    requirements: []
                }
            }
        },
        {
            id: 1,
            created: '2021-10-01T00:00:00',
            taskId: 'abcdefgh',
            task: {
                id: 'abcdefgh',
                functionName: 'create forget password page',
                status: 2
            },
            skills: [ 'React Native' ],
            status: 1,
            workType: 2,
            description: 'this is a work item description',
            workInput: {
                code: 'def test(x):\n    pass',
                context: {
                    class_functions: [],
                    docstrings: {},
                    functions: [],
                    imports: [],
                    requirements: []
                }
            }
        }
    ]
} as ContributorWorkState);

const contributorWorkSlice = createSlice({
    name: 'contributorWork',
    initialState,
    reducers: {}
});

export const { } = contributorWorkSlice.actions;

export default contributorWorkSlice.reducer;

interface ContributorWorkSelectorsType {
    pendingWork: WorkItem[]
}

export const ContributorWorkSelectors = (): ContributorWorkSelectorsType => {
    const pendingWork = useSelector(
        (state: RootState) => state.contributorWork.pendingWork
    );

    return {
        pendingWork
    };
};
