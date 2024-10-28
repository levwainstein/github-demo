import { Meta, Story } from '@storybook/react';
import React from 'react';

import FooterButtons, { Props } from '../../src/shared/FooterButtons';

export default {
    title: 'Shared/FooterButtons',
    component: FooterButtons,
    argTypes: {
    },
    args: {}
} as Meta;

const Template: Story<Props> = (args) => {
    return (
        <FooterButtons
            {...args}
        />
    );
};

export const Primary = Template.bind({});
