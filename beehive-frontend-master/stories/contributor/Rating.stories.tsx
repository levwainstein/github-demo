import { Meta, Story } from '@storybook/react';
import React from 'react';

import Rating from '../../src/pages/ContributorWork/components/Rating';

interface RatingProps {
    onValueChange: (rating: string, value: string) => void;
}

export default {
    title: 'Contributor/Rating',
    component: Rating,
    argTypes: {
        onValueChange: { action: 'onValueChange' }
    },
    args: {}
} as Meta;

const Template: Story<RatingProps> = (args) => {
    return (
        <Rating
            {...args}
        />
    );
};

export const Primary = Template.bind({});
