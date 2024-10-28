import { Meta, Story } from '@storybook/react';
import React from 'react';

import { AdminNotes } from '../../src/shared';

interface AdminNotesProps {}

export default {
    title: 'Shared/AdminNotes',
    component: AdminNotes,
    argTypes: {},
    args: {}
} as Meta;

const Template: Story<AdminNotesProps> = (args) => <AdminNotes {...args} />;

export const Primary = Template.bind({});
