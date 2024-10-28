import { Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { FunctionComponent, useEffect, useState } from 'react';
import { NavLink as Link } from 'react-router-dom';
import { useSearchParam } from 'react-use';

import { useAppDispatch } from '../../hooks';
import { activateUser, AuthSelectors } from '../../reducers/auth';
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

type Props = Record<string, unknown>;

const ActivateUser: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();

    const activationToken = useSearchParam('c');

    const { authLoading } = AuthSelectors();

    // null = loading, false/true = activation failure/success
    const [ activationSuccess, setActivationSuccess ] = useState<boolean | null>(null);

    useEffect(() => {
        if (activationToken) {
            dispatch(
                activateUser({ activationToken })
            ).unwrap().then(() => {
                setActivationSuccess(true);
            }).catch(() => {
                setActivationSuccess(false);
            });
        } else {
            setActivationSuccess(false);
        }
    }, []);

    return (
        <Wrapper loading={authLoading}>
            <div className={classes.content}>
                {activationSuccess === true && (
                    <>
                        <Typography
                            variant="h3"
                            component="h1"
                            className={classes.title}
                        >
                            Your Account Has Been Activated!
                        </Typography>
                        <Typography>
                            You can now&nbsp;
                            <Link to={'/login'}>
                                login
                            </Link>
                            &nbsp;and begin contributing :)
                        </Typography>
                    </>
                )}
                {activationSuccess === false && (
                    <>
                        <Typography
                            variant="h3"
                            component="h1"
                            className={classes.title}
                        >
                            Account Activation Failed
                        </Typography>
                        <Typography>
                            There may be something wrong with the link you used to get here.
                        </Typography>
                        <Typography>
                            To receive a new link you can&nbsp;
                            <Link to={'/login'}>
                                login
                            </Link>
                            &nbsp;and request a resend.
                        </Typography>
                        <Typography>
                            If this problem persists please contact our support.
                        </Typography>
                    </>
                )}
            </div>

            <ReportBug />
        </Wrapper>
    );
};

export default ActivateUser;
