import { Meta, Story } from '@storybook/react';
import React from 'react';
import { Provider } from 'react-redux';

import EmptyView from '../../src/pages/Work/components/emptyView';
import store from '../../src/store';

interface EmptyViewProps {
}

export default {
    title: 'Work/EmptyView',
    component: EmptyView,
    argTypes: {
    },
    decorators: [ (Story) => <Provider store={store}><Story /></Provider> ]
} as Meta;

const Template: Story<EmptyViewProps> = (args) => <EmptyView {...args} />;

export const Primary = Template.bind({});
Primary.args = {
};
