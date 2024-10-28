import { Meta, Story } from '@storybook/react';
import React from 'react';

import { ContributorStatus } from '../../src/shared';
import { Props } from '../../src/shared/contributorStatus';

export default {
    title: 'Shared/ContributorStatus',
    component: ContributorStatus,
    argTypes: {},
    args: {}
} as Meta;

const Template: Story<Props> = (args) => <ContributorStatus {...args} />;

export const Primary = Template.bind({});

Primary.args = {
    options: [ 'Inactive', 'Unavailable', 'Active' ],
    value: 'Inactive'
};
