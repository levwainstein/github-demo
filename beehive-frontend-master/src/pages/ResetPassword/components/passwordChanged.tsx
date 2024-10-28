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

const PasswordChanged: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();

    return (
        <Box className={classes.content}>
            <Typography
                variant="h3"
                component="h1"
                className={classes.title}
            >
                Your password was changed!
            </Typography>
            <Typography className={classes.subtitle}>
                You can now use your new password to&nbsp;
                <Link to={'/login'}>
                    login
                </Link>
                &nbsp;:)
            </Typography>
        </Box>
    );
};

export default PasswordChanged;
