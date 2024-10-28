/* eslint-disable @typescript-eslint/no-var-requires */
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
    app.use(
        '/backend',
        createProxyMiddleware({
            target: 'http://127.0.0.1:5000',
            changeOrigin: true,
            pathRewrite: { '^/backend': '' }
        })
    );

    app.use(
        '/praesepe',
        createProxyMiddleware({
            target: 'http://127.0.0.1:5002',
            changeOrigin: true,
            pathRewrite: { '^/praesepe': '' }
        })
    );

    app.use(
        '/pollinator/task-type',
        createProxyMiddleware({
            target: 'http://127.0.0.1:5053',
            changeOrigin: true,
            pathRewrite: { '^/pollinator/task-type': '' }
        })
    );
};
