import { Box, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { FunctionComponent } from 'react';

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

const ResetPasswordSent: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();

    return (
        <Box className={classes.content}>
            <Typography
                variant="h3"
                component="h1"
                className={classes.title}
            >
                Don&apos;t worry, we got your back!
            </Typography>
            <Typography className={classes.subtitle}>
                If we find an account registered using the email you provided we&apos;ll send an
                <br />
                email with instructions for resetting your password ASAP!
                <br />
                Please use the enclosed link to activate your account within 24 hours.
            </Typography>
            <Typography className={classes.subtitle}>
                If you can&apos;t find the email in your inbox, try looking in your spam
                <br />
                folder. If it&apos;s not there you can always try again
            </Typography>
            <Typography className={classes.subtitle}>
                Don&apos;t hesitate to contact us if you keep having issues accessing your account
            </Typography>
        </Box>
    );
};

export default ResetPasswordSent;
