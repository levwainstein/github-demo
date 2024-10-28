import { configureStore } from '@reduxjs/toolkit';
import { Meta, Story } from '@storybook/react';
import { Provider } from 'react-redux';
import { BrowserRouter as Router } from 'react-router-dom';

import RatePage from '../../src/pages/Rate';
import { test as storeTest } from '../../src/store';

type RateProps = Record<string, never>;

export default {
    title: 'Other Pages/Rate',
    component: RatePage,
    argTypes: {},
    decorators: [ (Story) => <Router><Story /></Router> ]
} as Meta;

const Template: Story<RateProps> = (args) => <RatePage {...args} />;

const codingStore = configureStore({ ...storeTest.storeOptions });

export const Rate = Template.bind({});

Rate.decorators = [
    (Story) => (
        <Provider store={codingStore}>
            <Story />
        </Provider>
    )
];
