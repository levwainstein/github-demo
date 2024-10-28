#!/bin/sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

tee $SCRIPT_DIR/../.git/hooks/pre-commit << EOF
#!/bin/sh

echo pre-commit hook is a-go!

# run lint
npm run lint

# exit with previous command exit code
exit $?

EOF

chmod a+x $SCRIPT_DIR/../.git/hooks/pre-commit
