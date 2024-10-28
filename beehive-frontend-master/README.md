# beehive-frontend

## Run

To run the project, you will need to make sure you have the backend running locally and then use `npm`, i.e.

```bash
$ npm install
$ npm start
```

If you don't have the backend installed, you may use [Storybook](https://storybook.js.org/) (see below).

### Communicating with backend services

React supports http-proxy-middleware to proxy requests from a local debug
execution to backend services. You can see the proxy configuration in the
`src/setupProxy.js` file. Note the ports we generally use for each service.

### Run Storybook

You can edit the components of the projects using [Storybook](https://storybook.js.org/). To run Storybook, please use

```bash
npm run storybook
```

## Git Hooks

To setup local git hooks run the script `scripts/setup_git_hooks.sh`.
After running the script every git action for which a hook was created will
execute the hook at the set time.

### Installed Hooks

* pre-commit - will execute before committing code and run lint to make sure
  source is pretty.

### Disable Hooks

To disable hooks permanently delete their files from `.git/hooks/` (eg.
`.git/hooks/pre-commit`). Commit hooks (and possibly others) can be disabled
a single time using:

```bash
$ git commit -n / --no-verify
```

## Run linter

```bash
npm run lint
```
