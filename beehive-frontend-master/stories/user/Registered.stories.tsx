import { configureStore } from '@reduxjs/toolkit';
import { Meta, Story } from '@storybook/react';
import { Provider } from 'react-redux';
import { MemoryRouter as Router } from 'react-router-dom';

import RegisteredView from '../../src/pages/Registered';
import { test as storeTest } from '../../src/store';

interface RegisteredViewProps {}

export default {
    title: 'User/Registered',
    component: RegisteredView,
    argTypes: {},
    decorators: [ (Story) => <Router initialEntries={[
        {
            state: {
                email: 'test@email.nope',
                token: 'fake-token'
            }
        }
    ]}><Story /></Router> ]
} as Meta;

const Template: Story<RegisteredViewProps> = (args) => <RegisteredView {...args} />;

const codingStore = configureStore({ ...storeTest.storeOptions });

export const Registered = Template.bind({});

Registered.decorators = [
    (Story) => (
        <Provider store={codingStore}>
            <Story />
        </Provider>
    )
];
