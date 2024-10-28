import { Meta, Story } from '@storybook/react';
import React from 'react';

import Description, { Props } from '../../src/pages/ContributorWork/components/Description';

export default {
    title: 'Other Pages/Description',
    component: Description,
    argTypes: {},
    args: {}
} as Meta;

const Template: Story<Props> = (args) => <Description {...args} />;

export const Primary = Template.bind({});

const descriptionContent =
    'Create delete method in UserFoodView\n\
Add an option to aggregate all metrics on the advanced report by week or by year.\n\
The default setting will be by date but the user will be able to change it to a week or month from a radio button on the top of the date picker.\n\n\
The aggregation needs to be by a calendar week/month.\n\
A week is Monday to Sunday.\n\
A month is from the 1st of the month until the last day of the month (28/30/31).\n\n\
If a user selects a time range that includes incomplete periods (the time chosen doesn’t start on a Monday and ends on a Sunday / beginning and end of the month) then we will also include the complete period in the time frame.\n\n\
For example:\n\
If a user selects this time range: August 23rd - October 20.\n\
If the time will be aggregated by week then the time range will change to:\n\
If the time will be aggregated by week then the time range will change to: August 21st';

Primary.args = {
    content: descriptionContent
};
