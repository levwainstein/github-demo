import { Meta, Story } from '@storybook/react';
import React from 'react';

import { ContributorHeader } from '../../src/shared';
import { Props } from '../../src/shared/contributorHeader';

export default {
    title: 'Shared/ContributorHeader',
    component: ContributorHeader,
    argTypes: {},
    args: {}
} as Meta;

const Template: Story<Props> = (args) => <ContributorHeader {...args} />;

export const Primary = Template.bind({});

Primary.args = {
    avatar: 'avatar.png',
    name: 'King David',
    country: 'Israel',
    time: '3:15 PM local time',
    rating: 2.5,
    totalRatings: '242',
    statusOptions: [ 'Inactive', 'Unavailable', 'Active' ]
};
