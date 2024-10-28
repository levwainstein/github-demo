import { Meta, Story } from '@storybook/react';
import React from 'react';

import { Rating } from '../../src/shared';
import { Props } from '../../src/shared/rating';

export default {
    title: 'Shared/Rating',
    component: Rating,
    argTypes: {
        onSubmit: { action: 'onSubmit' }
    },
    args: {}
} as Meta;

const Template: Story<Props> = (args) => <Rating {...args} />;

export const Primary = Template.bind({});

Primary.args = {
    subjects: [ 'work_description' ]
};
