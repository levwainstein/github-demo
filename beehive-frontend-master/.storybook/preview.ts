import { muiTheme } from 'storybook-addon-material-ui';

import theme from '../src/theme';

import './global.css';

export const parameters = {
    actions: { argTypesRegex: "^on[A-Z].*" },
    backgrounds: {
        default: 'beehive',
        values: [
            {
                name: 'beehive',
                value: '#111218'
            },
            {
                name: 'clear',
                value: '#ffffff'
            }
        ]
    }
};

export const decorators = [
    muiTheme([theme])
];
