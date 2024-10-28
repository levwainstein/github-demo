import { Button, Snackbar, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { FunctionComponent, useState } from 'react';
import { Redirect, useLocation } from 'react-router-dom';

import { useAppDispatch } from '../../hooks';
import { AuthSelectors, resendActivationEmail } from '../../reducers/auth';
import { ReportBug, Wrapper } from '../../shared';

const useStyles = makeStyles((theme) => ({
    content: {
        textAlign: 'center',
        margin: theme.spacing(3),
        width: '80%',
        alignSelf: 'center'
    },
    title: {
        marginTop: theme.spacing(2)
    },
    resendText: {
        marginTop: theme.spacing(2)
    },
    resendButton: {
        marginTop: theme.spacing(2)
    }
}));

type RegisteredLocationState = {
    email?: string;
    token?: string;
};

type Props = Record<string, unknown>;

const Registered: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();
    const location = useLocation<RegisteredLocationState>();

    const { authLoading } = AuthSelectors();

    const [ resendSuccess, setResendSuccess ] = useState<number | null>(null);
    const [ resendError, setResendError ] = useState<boolean>(false);

    if (!location.state || !location.state.email || !location.state.token) {
        return (
            <Redirect to="/" />
        );
    }

    const email = location.state.email;
    const token = location.state.token;

    const handleResendClicked = () => {
        dispatch(
            resendActivationEmail({ unactivatedAccessToken: token })
        ).unwrap().then(() => {
            setResendSuccess(Date.now());
        }).catch(() => {
            setResendError(true);
        });
    };

    return (
        <Wrapper loading={authLoading}>
            <div className={classes.content}>
                <Typography
                    variant="h3"
                    component="h1"
                    className={classes.title}
                >
                    Thank you for registering!
                </Typography>
                <Typography>
                    A confirmation email was sent to <i>{email}</i> !
                    <br />
                    Please use the enclosed link to activate your account.
                </Typography>
                <Typography className={classes.resendText}>
                    If you can&apos;t find the activation email in your inbox, try
                    <br />
                    looking in your spam folder. If it&apos;s not there either we
                    <br />
                    can send another one -
                </Typography>
                <Button
                    className={classes.resendButton}
                    disabled={authLoading || !!resendSuccess}
                    onClick={handleResendClicked}
                    color="primary"
                >
                    Resend
                </Button>
            </div>

            <Snackbar
                open={!!resendSuccess}
                autoHideDuration={6000}
                onClose={() => setResendSuccess(null)}
                message="Activation email was resent!"
            />
            <Snackbar
                open={resendError}
                autoHideDuration={6000}
                onClose={() => setResendError(false)}
                message="Woops! Not sure what happened there... Please try again"
            />

            <ReportBug />
        </Wrapper>
    );
};

export default Registered;
