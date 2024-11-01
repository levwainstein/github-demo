import { defineConfig } from "cypress";

export default defineConfig({
  env: {
    db: {
      host: "127.0.0.1",
      user: "root",
      database: "beehive_test",
    },
  },

  e2e: {
    // We've imported your old cypress plugins here.
    // You may want to clean this up later by importing these.
    setupNodeEvents(on, config) {
      return require("./cypress/plugins/index.js")(on, config);
    },
  },

  component: {
    devServer: {
      framework: "create-react-app",
      bundler: "webpack",
    },
  },

  video: true,
  videoCompression: true,
});
