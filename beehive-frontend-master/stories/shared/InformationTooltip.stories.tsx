import { Meta, Story } from '@storybook/react';
import React from 'react';

import { InformationTooltip } from '../../src/shared';
import { Props } from '../../src/shared/informationTooltip';

export default {
    title: 'Shared/InformationTooltip',
    component: InformationTooltip,
    argTypes: {},
    args: {}
} as Meta;

const Template: Story<Props> = (args) => <InformationTooltip {...args}>
    <h1 style={{ color: 'white', width: 300, cursor: 'pointer' }}>Hover me</h1>
</InformationTooltip>;

export const Primary = Template.bind({});

Primary.args = {
    text: 'This work requires skills that aren\'t listed in your profile. We show the work anyways in case you want to give it a try. You can easily adjust your profile settings if you prefer to work exclusively within your skill set.'
};
