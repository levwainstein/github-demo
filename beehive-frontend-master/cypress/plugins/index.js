/// <reference types="cypress" />
// ***********************************************************
// This example plugins/index.js can be used to load plugins
//
// You can change the location of this file or turn off loading
// the plugins file with the 'pluginsFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/plugins-guide
// ***********************************************************

// This function is called when a project is opened or re-opened (e.g. due to
// the project's config changing)

const mysql = require('mysql2');

// based on code here: https://gist.github.com/fityanos/0a345e9e9de498b6c629f78e6b2835f5
function queryTestDb(options, config) {
    const { query, args } = options;

    // connect to mysql using credentials from cypress.json env
    const connection = mysql.createConnection(config.env.db);
    connection.connect();

    // return promise which is rejected on error or resolved with result after querying
    // and closing the connection
    return new Promise((resolve, reject) => {
        connection.query(query, args, (error, results) => {
            if (error) {
                reject(error);
            } else {
                connection.end();
                return resolve(results);
            }
        });
    });
}

/**
 * @type {Cypress.PluginConfig}
 */
// eslint-disable-next-line no-unused-vars
module.exports = (on, config) => {
    // `on` is used to hook into various events Cypress emits
    // `config` is the resolved Cypress config

    // Usage: cy.task('queryTestDb', { query, args })
    on('task', {
        queryTestDb: (options) => {
            return queryTestDb(options, config);
        }
    });
};
