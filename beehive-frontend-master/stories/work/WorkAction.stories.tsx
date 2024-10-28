import { configureStore } from '@reduxjs/toolkit';
import { Meta, Story } from '@storybook/react';
import { Provider } from 'react-redux';

import Actions from '../../src/pages/Work/components/work/actions';
import { test as storeTest } from '../../src/store';

interface WorkActionsProps {
    taskId: string;
    workActive: boolean;
    workLoading: boolean;
    onAcceptClick: () => void;
    onSkipClick: () => void;
    onSubmitFeedback: (feedback: string) => void;
    onCancelClick: () => void;
}

const codingStore = configureStore({ ...storeTest.storeOptions });

export default {
    title: 'Work/WorkAction',
    component: Actions,
    argTypes: {
        onAcceptClick: { action: 'onAcceptClick' },
        onSkipClick: { action: 'onSkipClick' },
        onSubmitFeedback: { action: 'onSubmitFeedback' },
        onCancelClick: { action: 'onCancelClick' }
    },
    decorators: [ (Story) => <Provider store={codingStore}><Story /></Provider> ]
} as Meta;

const Template: Story<WorkActionsProps> = (args) => <Actions {...args} />;

export const WorkActive = Template.bind({});

WorkActive.args = {
    taskId: 'abcdefgh',
    workActive: true,
    workLoading: false
};

export const WorkSubmitted = Template.bind({});

WorkSubmitted.args = {
    taskId: 'abcdefgh',
    workActive: false,
    workLoading: false
};
