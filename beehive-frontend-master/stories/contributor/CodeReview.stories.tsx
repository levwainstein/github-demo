import { Meta, Story } from '@storybook/react';
import React from 'react';

import CodeReview, {
    CodeReviewProps, mockReviews
} from '../../src/pages/ContributorWork/components/CodeReview';

export default {
    title: 'Contributor/CodeReview',
    component: CodeReview,
    argTypes: {},
    args: {}
} as Meta;

const Template: Story<CodeReviewProps> = (args) => <CodeReview {...args} />;

export const Primary = Template.bind({});

Primary.args = { reviews: mockReviews };
