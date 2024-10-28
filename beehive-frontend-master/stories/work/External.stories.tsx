import { Meta, Story } from '@storybook/react';
import React from 'react';
import { Provider } from 'react-redux';

import External from '../../src/pages/Work/components/work/external';
import store from '../../src/store';

interface ExternalProps {
    workActive: boolean;
    workDone: boolean;
    workLoading: boolean;
    handleSubmitUrlSolution: (url: string) => void;
    handleSubmitSolutionReview: () => void;
    handleCancelWork: () => void;
    handleNextWorkClick: () => void;
    requirePRUrl?: boolean;
    handleAnalyzeUrlSolution: (url: string) => void;
    submitConditionsFulfilled: boolean;
}

export default {
    title: 'Work/External',
    component: External,
    argTypes: {
        handleSubmitUrlSolution: { action: 'handleSubmitUrlSolution' },
        handleCancelWork: { action: 'handleCancelWork' },
        handleNextWorkClick: { action: 'handleNextWorkClick' }
    },
    decorators: [ (Story) => <Provider store={store}><Story /></Provider> ]
} as Meta;

const Template: Story<ExternalProps> = (args) => <External {...args} />;

export const Primary = Template.bind({});
Primary.args = {
    workActive: true,
    workDone: false,
    workLoading: false,
    requirePRUrl: true,
    beehaveReviewed: false
};

export const WorkNotActive = Template.bind({});
WorkNotActive.args = {
    workActive: false,
    workDone: false,
    workLoading: false,
    requirePRUrl: true,
    beehaveReviewed: false
};

export const WorkDone = Template.bind({});
WorkDone.args = {
    workActive: false,
    workDone: true,
    workLoading: false,
    requirePRUrl: true,
    beehaveReviewed: false
};
