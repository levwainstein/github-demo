import { FunctionComponent, useCallback, useEffect, useState } from 'react';
import { Redirect, useLocation } from 'react-router-dom';

import { useAppDispatch } from '../../hooks';
import { resetPasswordChange, resetPasswordValidate } from '../../reducers/auth';
import { signedIn } from '../../services/auth';
import { ReportBug, Wrapper } from '../../shared';
import { InvalidCode, PasswordChanged, SetPasswordForm } from './components';

type Props = Record<string, never>;

const ResetPassword: FunctionComponent<Props> = ({}: Props) => {
    const dispatch = useAppDispatch();
    const location = useLocation();

    const [ loading, setLoading ] = useState<boolean>(false);
    const [ code, setCode ] = useState<string>('');
    const [ codeValid, setCodeValid ] = useState<boolean | null>(null);
    const [ passwordChanged, setPasswordChanged ] = useState<boolean>(false);
    const [ changePasswordError, setChangePasswordError ] = useState<string | null>(null);

    useEffect(() => {
        if (location) {
            const searchParams = new URLSearchParams(location.search.slice(1));
            const codeParam = searchParams.get('c');

            if (codeParam) {
                setCode(codeParam);
                setLoading(true);

                dispatch(
                    resetPasswordValidate({ code: codeParam })
                ).unwrap().then(() => {
                    setCodeValid(true);
                }).catch(() => {
                    setCodeValid(false);
                }).finally(() => {
                    setLoading(false);
                });
            } else {
                setCodeValid(false);
            }
        }
    }, [ location ]);

    const handleSetPassword = useCallback(
        (newPassword: string): Promise<void> => {
            setLoading(true);

            return dispatch(
                resetPasswordChange({ code, newPassword })
            ).unwrap().then(() => {
                setPasswordChanged(true);
                return Promise.resolve();
            }).catch((error) => {
                setChangePasswordError(error?.error || 'unknown');
                return Promise.reject();
            }).finally(() => {
                setLoading(false);
            });
        },
        [ code ]
    );

    // if user is already signed in there's nothing to see here
    if (signedIn()) {
        return (
            <Redirect to="/" />
        );
    }

    return (
        <Wrapper loading={loading}>
            {codeValid !== null && (
                codeValid === false ? (
                    <InvalidCode />
                ) : (
                    passwordChanged ? (
                        <PasswordChanged />
                    ) : (
                        <SetPasswordForm
                            onSetPassword={handleSetPassword}
                            setPasswordError={changePasswordError}
                        />
                    )
                )
            )}

            <ReportBug />
        </Wrapper>
    );
};

export default ResetPassword;
