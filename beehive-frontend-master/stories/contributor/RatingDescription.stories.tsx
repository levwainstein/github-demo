import { Meta, Story } from '@storybook/react';
import React, { useState } from 'react';

import DescriptionRating from '../../src/pages/ContributorWork/components/descriptionRating';
import { UserRating } from '../../src/types/rating';

interface RatingDescriptionProps {
    title: string;
    description: string;
    handleDoneClick: () => void;
    setUserRating: React.Dispatch<React.SetStateAction<UserRating>>;
    userRating: UserRating;
}

export default {
    title: 'Contributor/DescriptionRating',
    component: DescriptionRating,
    argTypes: {
        handleDoneClick: { action: 'handleDoneClick' }
    },
    args: {}
} as Meta;

const Template: Story<RatingDescriptionProps> = (args) => {
    const [ userRating, setUserRating ] = useState<UserRating>({
        score: 0,
        feedback: ''
    });
    return (
        <DescriptionRating
            {...args}
            setUserRating={setUserRating}
            userRating={userRating}
        />
    );
};

export const Primary = Template.bind({});
Primary.args = {
    title: 'Description rating',
    description: 'How would you rate the task description?'
};
