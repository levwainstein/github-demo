import { FunctionComponent, useCallback, useEffect, useState } from 'react';
import { Redirect } from 'react-router-dom';

import { useAppDispatch } from '../../hooks';
import { AuthSelectors, clearAuthError } from '../../reducers/auth';
import { signedIn } from '../../services/auth';
import { ReportBug, Wrapper } from '../../shared';
import { LoginForm, ResetPasswordForm, ResetPasswordSent } from './components';

type Props = Record<string, never>;

const Login: FunctionComponent<Props> = ({}: Props) => {
    const dispatch = useAppDispatch();

    const [ resetForm, setResetForm ] = useState<boolean>(false);
    const [ resetSuccess, setResetSuccess ] = useState<boolean>(false);

    const { authLoading, authError } = AuthSelectors();

    useEffect(() => {
        // clear auth error on component-did-mount
        dispatch(clearAuthError());
    }, [ clearAuthError ]);

    const handleToggleResetPassword = useCallback(
        (resetForm) => {
            setResetForm(resetForm);
        },
        [ setResetForm ]
    );

    const handleResetPasswordSuccess = useCallback(
        () => {
            setResetSuccess(true);
        },
        [ setResetSuccess ]
    );

    // if user is already signed in there's nothing to see here
    if (signedIn()) {
        return (
            <Redirect to="/" />
        );
    }

    return (
        <Wrapper loading={authLoading}>
            {resetForm ? (
                resetSuccess ? (
                    <ResetPasswordSent />
                ) : (
                    <ResetPasswordForm
                        onToggleResetPassword={handleToggleResetPassword}
                        onResetPasswordSuccess={handleResetPasswordSuccess}
                    />
                )
            ) : (
                <LoginForm
                    onToggleResetPassword={handleToggleResetPassword}
                    authError={authError}
                />
            )}

            <ReportBug />
        </Wrapper>
    );
};

export default Login;
