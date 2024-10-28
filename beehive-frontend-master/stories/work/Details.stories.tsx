import { Meta, Story } from '@storybook/react';
import React from 'react';
import { Provider } from 'react-redux';

import Details from '../../src/pages/Work/components/work/details';
import store from '../../src/store';
import { UserRatings } from '../../src/types/rating';
import { TaskTypeClassification } from '../../src/types/task';
import { WorkType } from '../../src/types/work';

interface DetailsProps {
    workId: number;
    workType: WorkType;
    workPriority?: number;
    description: string;
    taskId?: string;
    taskTypeClassification?: TaskTypeClassification;
    skills?: [string];
    workLoading: boolean;
    workActive: boolean;
    workStartTimeEpochMs: number;
    workDone: boolean;
    handleActivateWork: () => void;
    handleSkipWork: () => void;
    handleNextWorkClick: () => void;
    handleCancelWork: () => void;
    handleSubmitWorkFeedback: (feedback: string) => void;
    handleSubmitUrlSolution: (url: string) => void;
    handleSubmitSolutionReview: () => void;
    handleAnalyzeUrlSolution: (url: string) => void;
    handleSubmitRating: (ratings: UserRatings) => Promise<any>;
    handleSubmitTaskClassificationCorrection: (predictedOutput: string, correctedOutput: string) => void;
    submitConditionsFulfilled: boolean;
}

export default {
    title: 'Work/Details',
    component: Details,
    argTypes: {
        handleActivateWork: { action: 'handleActivateWork' },
        handleSkipWork: { action: 'handleSkipWork' },
        handleCancelWork: { action: 'handleCancelWork' },
        handleSubmitWorkFeedback: { action: 'handleSubmitWorkFeedback' }
    },
    decorators: [ (Story) => <Provider store={store}><Story /></Provider> ]
} as Meta;

const Template: Story<DetailsProps> = (args) => <Details {...args} />;

export const Primary = Template.bind({});
Primary.args = {
    workId: 'aaaaaaaa',
    workType: WorkType.CREATE_FUNCTION,
    description: 'Return the sum of the two numbers',
    testCases: [
        {
            caseInput: [ '1', '2' ],
            caseOutput: '3'
        },
        {
            caseInput: [ '15', '3' ],
            caseOutput: '18'
        },
        {
            caseInput: [ '-1', '-2' ],
            caseOutput: '-3'
        }
    ],
    paramsLoading: false,
    params: [ { name: 'secret' } ],
    classFunction: false,
    workContext: { 'docstrings': { mul: 'multiples parameters' } },
    taskId: 'bbbbbbbb',
    skills: [ 'skill a' ],
    workLoading: false,
    workActive: true,
    workStartTimeEpochMs: Date.now() - (5 * 60 * 1000),
    workDone: false,
    submitConditionsFulfilled: true
};

export const NoTestsOrParams = Template.bind({});
NoTestsOrParams.args = {
    workId: 'aaaaaaaa',
    workType: WorkType.CREATE_FUNCTION,
    description: 'Return the sum of the two numbers',
    testCases: [],
    paramsLoading: false,
    params: [],
    classFunction: false,
    workContext: { 'docstrings': {} },
    taskId: 'bbbbbbbb',
    skills: undefined,
    workLoading: false,
    workActive: true,
    workStartTimeEpochMs: Date.now() - (5 * 60 * 1000),
    workDone: false
};

export const ParamsLoading = Template.bind({});
ParamsLoading.args = {
    workId: 'aaaaaaaa',
    workType: WorkType.CREATE_FUNCTION,
    description: 'Return the sum of the two numbers',
    testCases: [],
    paramsLoading: true,
    params: [],
    classFunction: false,
    workContext: { 'docstrings': {} },
    taskId: 'bbbbbbbb',
    skills: undefined,
    workLoading: false,
    workActive: true,
    workStartTimeEpochMs: Date.now() - (5 * 60 * 1000),
    workDone: false
};

export const DescriptionLinks = Template.bind({});
DescriptionLinks.args = {
    workId: 'aaaaaaaa',
    workType: WorkType.CREATE_FUNCTION,
    description: 'Normal http: [http example.org](http://example.org)\nNormal https: [https example.org](https://example.org)\nNormal mailto: [mailto no-one at example.org](mailto:no-one@example.org)\nNormal tel: [tel 000000000](tel:000000000)\nNo protocol: [example.org](example.org)\nVisited link: [google.com](https://www.google.com/)',
    testCases: [],
    paramsLoading: false,
    params: [],
    classFunction: false,
    workContext: { 'docstrings': {} },
    taskId: 'bbbbbbbb',
    skills: undefined,
    workLoading: false,
    workActive: true,
    workStartTimeEpochMs: Date.now() - (5 * 60 * 1000),
    workDone: false
};

export const DescriptionLists = Template.bind({});
DescriptionLists.args = {
    workId: 'aaaaaaaa',
    workType: WorkType.CREATE_FUNCTION,
    description: '### Numbered list\n\n1. first\n\n2. second\n\n3. third\n\n### Point list\n\n* first\n\n* second\n\n* third',
    testCases: [],
    paramsLoading: false,
    params: [],
    classFunction: false,
    workContext: { 'docstrings': {} },
    taskId: 'bbbbbbbb',
    skills: undefined,
    workLoading: false,
    workActive: true,
    workStartTimeEpochMs: Date.now() - (5 * 60 * 1000),
    workDone: false
};
