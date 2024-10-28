import { Meta, Story } from '@storybook/react';
import React from 'react';

import TaskCompleted from '../../src/pages/ContributorWork/components/TaskCompleted';

export default {
    title: 'Other Pages/TaskCompleted',
    component: TaskCompleted,
    argTypes: {},
    args: {}
} as Meta;

const Template: Story = (args) => <TaskCompleted {...args} />;

export const Primary = Template.bind({});
