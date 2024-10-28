const TsconfigPathsPlugin = require('tsconfig-paths-webpack-plugin');

module.exports = {
    "stories": [
        "../stories/**/*.stories.mdx",
        "../stories/**/*.stories.@(js|jsx|ts|tsx)"
    ],
    "addons": [
        "@storybook/addon-links",
        "@storybook/addon-essentials",
        "@storybook/addon-actions",
        "storybook-addon-material-ui"
    ],
    "webpackFinal": (config) => {
        // init plugins list if it is not initalized yet
        if (!config.resolve.plugins) {
            config.resolve.plugins = [];
        }

        // add tsconfig paths plugins so the root tsconfig.json file will be
        // used when building storybook
        config.resolve.plugins.push(new TsconfigPathsPlugin());

        return config;
    }
}
