import { Box, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { FunctionComponent } from 'react';
import { Link } from 'react-router-dom';

const useStyles = makeStyles((theme) => ({
    content: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        flexGrow: 1
    },
    title: {
        margin: theme.spacing(2),
        textAlign: 'center'
    },
    subtitle: {
        marginTop: theme.spacing(2),
        textAlign: 'center'
    }
}));

type Props = Record<string, never>;

const InvalidCode: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();

    return (
        <Box className={classes.content}>
            <Typography
                variant="h3"
                component="h1"
                className={classes.title}
            >
                Whoops, your reset code does not seem valid...
            </Typography>
            <Typography className={classes.subtitle}>
                Remember that password reset codes can only be used once, and are
                <br />
                only valid for a certain period after which they cannot be used.
            </Typography>
            <Typography className={classes.subtitle}>
                You can always request a new password reset code at the&nbsp;
                <Link to={'/login'}>
                    login
                </Link>
                &nbsp;page!
            </Typography>
        </Box>
    );
};

export default InvalidCode;
