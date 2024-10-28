import { Button, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { Field, Form, Formik } from 'formik';
import { TextField } from 'formik-material-ui';
import { FunctionComponent, useCallback, useState } from 'react';
import { useHistory } from 'react-router-dom';

import { useAppDispatch } from '../../../hooks';
import { resetPassword } from '../../../reducers/auth';

function formatErrorMessage(error) {
    switch (error) {
        default:
            return 'Unknown error. Please try again';
    }
}

type FormErrors = {
    email?: string;
};

const useStyles = makeStyles((theme) => ({
    form: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        flexGrow: 1
    },
    beeImage: {
        width: '100px'
    },
    formTitle: {
        textAlign: 'center'
    },
    formField: {
        textAlign: 'center',
        width: '200px'
    },
    formButton: {
        width: '200px',
        flexBasis: 'max-content',
        margin: theme.spacing(1)
    },
    formTextButton: {
        textDecoration: 'none'
    },
    formFieldInput: {
        color: theme.palette.text.secondary
    }
}));

type Props = {
    onToggleResetPassword: (resetForm: boolean) => void;
    onResetPasswordSuccess: () => void;
};

const ResetPasswordForm: FunctionComponent<Props> = ({
    onToggleResetPassword,
    onResetPasswordSuccess
}: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();
    const history = useHistory();

    const [ resetPasswordError, setResetPasswordError ] = useState<string | null>(null);

    const handleValidate = useCallback(
        (values) => {
            const errors: FormErrors = {};

            if (!values.email) {
                errors.email = 'Required';
            } else if (!/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(values.email)) {
                errors.email = 'Invalid email address';
            }

            return errors;
        },
        []
    );

    const handleSubmit = useCallback(
        (values, { setSubmitting }) => {
            dispatch(
                resetPassword({
                    email: values.email
                })
            ).unwrap().then(() => {
                onResetPasswordSuccess();
            }).catch((error) => {
                setResetPasswordError(error.error || 'unknown');
                setSubmitting(false);
            });
        },
        [ dispatch, history, resetPassword ]
    );

    return (
        <Formik
            initialValues={{
                email: ''
            }}
            validate={handleValidate}
            onSubmit={handleSubmit}
        >
            {({ isSubmitting } ) => (
                <Form className={classes.form}>
                    <img className={classes.beeImage} alt="logo" src="bee_icon.jpg" />
                    <Typography
                        className={classes.formTitle}
                        variant="h5"
                        component="h1"
                    >
                        Reset Password
                    </Typography>
                    <Field
                        className={classes.formField}
                        component={TextField}
                        name="email"
                        type="email"
                        label="E-mail"
                        autoComplete="email"
                        InputProps={{
                            classes: {
                                root: classes.formFieldInput
                            }
                        }}
                    />
                    {resetPasswordError && (
                        <Typography color="error">
                            {formatErrorMessage(resetPasswordError)}
                        </Typography>
                    )}
                    <Button
                        className={classes.formButton}
                        type="submit"
                        variant="contained"
                        color="primary"
                        disabled={isSubmitting}
                    >
                        Reset Password
                    </Button>
                    <Button color="primary" onClick={() => onToggleResetPassword(false)}>
                        I Know My Password
                    </Button>
                </Form>
            )}
        </Formik>
    );
};

export default ResetPasswordForm;
