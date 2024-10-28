import { Button, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { Field, Form, Formik } from 'formik';
import { TextField } from 'formik-material-ui';
import { FunctionComponent, useCallback } from 'react';
import { Link, useHistory } from 'react-router-dom';

import { useAppDispatch } from '../../../hooks';
import { signIn } from '../../../reducers/auth';

function formatErrorMessage(error) {
    switch (error) {
        case 'unauthorized':
            return 'Wrong credentials';
        default:
            return 'Unknown error. Please try again';
    }
}

type FormErrors = {
    email?: string;
    password?: string;
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
    authError: string | null;
};

const LoginForm: FunctionComponent<Props> = ({
    authError,
    onToggleResetPassword
}: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();
    const history = useHistory();

    const handleValidate = useCallback(
        (values) => {
            const errors: FormErrors = {};

            if (!values.email) {
                errors.email = 'Required';
            } else if (!/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(values.email)) {
                errors.email = 'Invalid email address';
            } else if (!values.password) {
                errors.password = 'Required';
            }

            return errors;
        },
        []
    );

    const handleSubmit = useCallback(
        (values, { setSubmitting }) => {
            dispatch(
                signIn({
                    email: values.email,
                    pass: values.password
                })
            ).unwrap().then((result) => {
                if (result.activated) {
                    history.push('/');
                } else {
                    history.push(
                        '/register/success',
                        {
                            email: values.email,
                            token: result.accessToken
                        }
                    );
                }
            }).catch(() => {
                setSubmitting(false);
            });
        },
        [ dispatch, history, signIn ]
    );

    return (
        <Formik
            initialValues={{
                email: '',
                password: ''
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
                        Sign In
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
                    <Field
                        className={classes.formField}
                        component={TextField}
                        name="password"
                        type="password"
                        label="Password"
                        autoComplete="password"
                        InputProps={{
                            classes: {
                                root: classes.formFieldInput
                            }
                        }}
                    />
                    {authError && (
                        <Typography color="error">
                            {formatErrorMessage(authError)}
                        </Typography>
                    )}
                    <Button
                        className={classes.formButton}
                        type="submit"
                        variant="contained"
                        color="primary"
                        disabled={isSubmitting}
                    >
                        Sign In
                    </Button>
                    <Button color="primary" onClick={() => onToggleResetPassword(true)}>
                        I Forgot My Password
                    </Button>
                    <Link className={classes.formTextButton} to="/register">
                        <Button color="primary">
                            New user?
                        </Button>
                    </Link>
                </Form>
            )}
        </Formik>
    );
};

export default LoginForm;
