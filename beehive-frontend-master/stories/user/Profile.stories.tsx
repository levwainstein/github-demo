import { configureStore } from '@reduxjs/toolkit';
import { Meta, Story } from '@storybook/react';
import { Provider } from 'react-redux';
import { BrowserRouter as Router } from 'react-router-dom';

import ProfileView from '../../src/pages/UserProfile/components/profile';
import { test as storeTest } from '../../src/store';
import { UserProfile } from '../../src/types/user';

interface ProfileViewProps {
  profile: UserProfile | null;
  profileLoading: boolean;
  onProfileSubmit: (profileUpdateData: any) => Promise<void>;
  className?: string;
}

export default {
    title: 'User/Profile',
    component: ProfileView,
    argTypes: {
        onProfileSubmit: { action: 'profileSubmit' }
    },
    decorators: [ (Story) => <Router><Story /></Router> ]
} as Meta;

const Template: Story<ProfileViewProps> = (args) => <ProfileView {...args} />;

const codingStore = configureStore({ ...storeTest.storeOptions });
export const NewProfile = Template.bind({});
NewProfile.decorators = [
    (Story) => (
        <Provider store={codingStore}>
            <Story />
        </Provider>
    )
];
NewProfile.args = {

};

export const ExistingProfile = Template.bind({});
ExistingProfile.decorators = [
    (Story) => (
        <Provider store={codingStore}>
            <Story />
        </Provider>
    )
];
ExistingProfile.args = {
    profile: {
        email: 'test@gmail.com',
        firstName: 'test',
        lastName: 'xyz',
        githubUser: 'https://github.com/test-user',
        trelloUser: 'abc',
        upworkUser: 'def',
        availabilityWeeklyHours: 10,
        pricePerHour: 10.0,
        skills: [ 'Javascript' ]
    }
};

export const SubmittingProfile = Template.bind({});
SubmittingProfile.decorators = [
    (Story) => (
        <Provider store={codingStore}>
            <Story />
        </Provider>
    )
];
SubmittingProfile.args = {
    ...ExistingProfile.args,
    profileLoading: true
};
