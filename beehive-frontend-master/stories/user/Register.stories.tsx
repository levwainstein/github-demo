import { configureStore } from '@reduxjs/toolkit';
import { Meta, Story } from '@storybook/react';
import { Provider } from 'react-redux';
import { BrowserRouter as Router } from 'react-router-dom';

import RegisteredView from '../../src/pages/Register';
import { test as storeTest } from '../../src/store';

interface RegisterViewProps {}

export default {
    title: 'User/Register',
    component: RegisteredView,
    argTypes: {},
    decorators: [ (Story) => <Router><Story /></Router> ]
} as Meta;

const Template: Story<RegisterViewProps> = (args) => <RegisteredView {...args} />;

const codingStore = configureStore({ ...storeTest.storeOptions });

export const Register = Template.bind({});

Register.decorators = [
    (Story) => (
        <Provider store={codingStore}>
            <Story />
        </Provider>
    )
];
