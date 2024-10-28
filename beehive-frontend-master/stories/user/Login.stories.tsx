import { configureStore } from '@reduxjs/toolkit';
import { Meta, Story } from '@storybook/react';
import { Provider } from 'react-redux';
import { BrowserRouter as Router } from 'react-router-dom';

import LoginView from '../../src/pages/Login/components/loginForm';
import { test as storeTest } from '../../src/store';

interface LoginViewProps {
  onToggleResetPassword: (resetForm: boolean) => void;
  authError: string | null;
}

export default {
    title: 'User/LoginForm',
    component: LoginView,
    argTypes: {
    },
    decorators: [ (Story) => <Router><Story /></Router> ]
} as Meta;

const Template: Story<LoginViewProps> = (args) => <LoginView {...args} />;

const codingStore = configureStore({ ...storeTest.storeOptions });
export const LoginForm = Template.bind({});
LoginForm.decorators = [
    (Story) => (
        <Provider store={codingStore}>
            <Story />
        </Provider>
    )
];
LoginForm.args = {
    authError: ''
};

export const ErrorLoginForm = Template.bind({});
ErrorLoginForm.decorators = [
    (Story) => (
        <Provider store={codingStore}>
            <Story />
        </Provider>
    )
];
ErrorLoginForm.args = {
    authError: 'Login Failed'
};
