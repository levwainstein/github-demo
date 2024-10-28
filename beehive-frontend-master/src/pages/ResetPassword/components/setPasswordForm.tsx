import { Button, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { Field, Form, Formik } from 'formik';
import { TextField } from 'formik-material-ui';
import { FunctionComponent, useCallback } from 'react';

function formatErrorMessage(error) {
    switch (error) {
        default:
            return 'Unknown error. Please try again';
    }
}

type FormErrors = {
    password?: string;
    password2?: string;
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
    onSetPassword: (newPassword: string) => Promise<void>;
    setPasswordError: string | null;
};

const SetPasswordForm: FunctionComponent<Props> = ({
    onSetPassword,
    setPasswordError
}: Props) => {
    const classes = useStyles();

    const handleValidate = useCallback(
        (values) => {
            const errors: FormErrors = {};

            if (!values.password) {
                errors.password = 'Required';
            } else if (values.password.length < 4) {
                errors.password = 'Too short';
            } else if (values.password !== values.password2) {
                errors.password2 = 'Passwords do not match';
            }

            return errors;
        },
        []
    );

    const handleSubmit = useCallback(
        (values, { setSubmitting }) => {
            onSetPassword(values.password).catch(() => setSubmitting(false));
        },
        [ onSetPassword ]
    );

    return (
        <Formik
            initialValues={{
                password: '',
                password2: ''
            }}
            validate={handleValidate}
            onSubmit={handleSubmit}
        >
            {({ isSubmitting } ) => (
                <Form className={classes.form}>
                    <Typography
                        className={classes.formTitle}
                        variant="h5"
                        component="h1"
                    >
                        Change Your Password
                    </Typography>
                    <Field
                        className={classes.formField}
                        component={TextField}
                        name="password"
                        type="password"
                        label="Password"
                        autoComplete="password"
                        required={true}
                        InputProps={{
                            classes: {
                                root: classes.formFieldInput
                            }
                        }}
                    />
                    <Field
                        className={classes.formField}
                        component={TextField}
                        name="password2"
                        type="password"
                        label="Repeat password"
                        autoComplete="new-password"
                        required={true}
                        InputProps={{
                            classes: {
                                root: classes.formFieldInput
                            }
                        }}
                    />
                    {setPasswordError && (
                        <Typography color="error">
                            {formatErrorMessage(setPasswordError)}
                        </Typography>
                    )}
                    <Button
                        className={classes.formButton}
                        type="submit"
                        variant="contained"
                        color="primary"
                        disabled={isSubmitting}
                    >
                        Change Password
                    </Button>
                </Form>
            )}
        </Formik>
    );
};

export default SetPasswordForm;
