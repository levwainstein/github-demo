import { Meta, Story } from '@storybook/react';
import React from 'react';

import { ContributorWork } from '../../src/shared';
import { Props } from '../../src/shared/contributorWork';

export default {
    title: 'Shared/ContributorWork',
    component: ContributorWork,
    argTypes: {},
    args: {}
} as Meta;

const Template: Story<Props> = (args) => <ContributorWork {...args} />;

export const Primary = Template.bind({});

Primary.args = {
    name: 'Task name......'
};
