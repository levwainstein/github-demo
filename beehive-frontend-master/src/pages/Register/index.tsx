import { Button, Slider, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { Field, Form, Formik } from 'formik';
import { CheckboxWithLabel, TextField } from 'formik-material-ui';
import { FunctionComponent, useCallback, useEffect } from 'react';
import { NavLink as Link, Redirect, useHistory, useLocation } from 'react-router-dom';

import { useAppDispatch } from '../../hooks';
import { AuthSelectors, clearAuthError, signUp } from '../../reducers/auth';
import { signedIn } from '../../services/auth';
import { ReportBug, Wrapper } from '../../shared';

function formatErrorMessage(error) {
    switch (error) {
        case 'email_exists':
            return 'Provided email is already registered';
        case 'invalid_registration_code':
            return 'Registration is currently not public. If you were invited and still see this message please contact us';
        default:
            return 'Unknown error. Please try again';
    }
}

type FormErrors = {
    email?: string;
    password?: string;
    password2?: string;
    acceptTerms?: string;
    githubUser?: string;
    pricePerHour?: string;
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
        marginBottom: theme.spacing(1)
    },
    formTextButton: {
        textDecoration: 'none'
    },
    formFieldInput: {
        color: theme.palette.text.secondary
    },
    noSpinnerInputStyle: {
        '&::-webkit-outer-spin-button, &::-webkit-inner-spin-button': {
            '-webkit-appearance': 'none',
            display: 'none'
        }
    },
    sliderLabel: {
        color: '#807e7e',
        marginTop: theme.spacing(1),
        marginBottom: theme.spacing(-1)
    },
    slider: {
        paddingTop: '10px'
    },
    sliderMarkLabel: {
        color: theme.palette.primary.light
    },
    sliderMarkLabelActive: {
        color: theme.palette.text.secondary
    },
    chip: {
        paddingTop: '10px'
    }
}));

type Props = Record<string, never>;

const Register: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();
    const history = useHistory();
    const location = useLocation();

    const { authLoading, authError } = AuthSelectors();

    useEffect(() => {
        // clear auth error on component-did-mount
        dispatch(clearAuthError());
    }, [ clearAuthError ]);

    const handleValidate = useCallback(
        async (values) => {
            const errors: FormErrors = {};

            if (!values.email) {
                errors.email = 'Required';
            } else if (!/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(values.email)) {
                errors.email = 'Invalid email address';
            } else if (!values.password) {
                errors.password = 'Required';
            } else if (values.password.length < 4) {
                errors.password = 'Too short';
            } else if (values.password !== values.password2) {
                errors.password2 = 'Passwords do not match';
            } else if (!/^(?:\d{1,2}(?:\.\d{1,2})?|\.\d{1,2})$/.test(String(values.pricePerHour))) {
                errors.pricePerHour = 'Invalid price format';
            } else if (!values.acceptTerms) {
                errors.acceptTerms = 'Required';
            } 
            if (values.githubUser?.length > 0) {
                values.githubUser = values.githubUser.trim();
                // API rate limit may exceeded, in such a case the validation will miss an existant user
                await fetch(`https://api.github.com/users/${values.githubUser}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data && data.message === 'Not Found'){
                            errors.githubUser = 'User does not exist on GitHub';
                        }
                    });
            }
            
            return errors;
        },
        []
    );

    const handleSubmit = useCallback(
        (values, { setSubmitting }) => {
            dispatch(
                signUp({
                    email: values.email,
                    pass: values.password,
                    code: location.hash.slice(1),
                    firstName: values.firstName,
                    lastName: values.lastName,
                    githubUser: values.githubUser,
                    trelloUser: values.trelloUser,
                    upworkUser: values.upworkUser,
                    availabilityWeeklyHours: values.availabilityWeeklyHours,
                    pricePerHour: values.pricePerHour
                })
            ).unwrap().then((result: {accessToken: string}) => {
                history.push(
                    '/register/success',
                    {
                        email: values.email,
                        token: result.accessToken
                    }
                );
            }).catch(() => {
                setSubmitting(false);
            });
        },
        [ dispatch, history, signUp ]
    );

    // if user is already signed in there's nothing to see here
    if (signedIn()) {
        return (
            <Redirect to="/" />
        );
    }

    return (
        <Wrapper loading={authLoading}>
            <Formik
                initialValues={{
                    email: '',
                    password: '',
                    password2: '',
                    firstName: '',
                    lastName: '',
                    githubUser: '',
                    trelloUser: '',
                    upworkUser: '',
                    availabilityWeeklyHours: 50,
                    pricePerHour: 5.0,
                    acceptTerms: false
                }}
                validate={handleValidate}
                validateOnBlur={true}
                validateOnChange={false}
                onSubmit={handleSubmit}
            >
                {({ errors, touched, isSubmitting, setFieldValue }) => (
                    <Form className={classes.form}>
                        <img className={classes.beeImage} alt="logo" src="bee_icon.jpg" />
                        <Typography
                            className={classes.formTitle}
                            variant="h5"
                            component="h1"
                        >
                            Sign Up
                        </Typography>
                        <Field
                            className={classes.formField}
                            component={TextField}
                            name="email"
                            type="email"
                            label="E-mail"
                            autoComplete="email"
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
                            name="password"
                            type="password"
                            label="Password"
                            autoComplete="new-password"
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
                        <Field
                            className={classes.formField}
                            component={TextField}
                            name="firstName"
                            label="First name"
                            autoComplete="first-name"
                            InputProps={{
                                classes: {
                                    root: classes.formFieldInput
                                }
                            }}
                        />
                        <Field
                            className={classes.formField}
                            component={TextField}
                            name="lastName"
                            label="Last name"
                            autoComplete="family-name"
                            InputProps={{
                                classes: {
                                    root: classes.formFieldInput
                                }
                            }}
                        />
                        <Field
                            className={classes.formField}
                            type="number"
                            component={TextField}
                            name="pricePerHour"
                            label="$ per hour"
                            step="0.5"
                            InputProps={{
                                classes: {
                                    root: classes.formFieldInput,
                                    input: classes.noSpinnerInputStyle
                                }
                            }}
                        />
                        <Field
                            className={classes.formField}
                            component={TextField}
                            name="githubUser"
                            label="GitHub User"
                            autoComplete="github-user"
                            InputProps={{
                                classes: {
                                    root: classes.formFieldInput
                                }
                            }}
                        />
                        <Field
                            className={classes.formField}
                            component={TextField}
                            name="trelloUser"
                            label="Trello User"
                            autoComplete="trello-user"
                            InputProps={{
                                classes: {
                                    root: classes.formFieldInput
                                }
                            }}
                        />
                        <Field
                            className={classes.formField}
                            component={TextField}
                            name="upworkUser"
                            label="Upwork User"
                            autoComplete="upwork-user"
                            InputProps={{
                                classes: {
                                    root: classes.formFieldInput
                                }
                            }}
                        />
                        <Typography
                            id="availability-weekly-hours-label"
                            className={classes.sliderLabel}
                        >
                            Availability hours per week
                        </Typography>
                        <Field
                            className={classes.formField}
                            component={Slider}
                            name="availabilityWeeklyHours"
                            aria-labelledby="availability-weekly-hours-label"
                            valueLabelDisplay="auto"
                            marks={[
                                { value: 0, label: '0' },
                                { value: 20, label: '20' },
                                { value: 40, label: '40' },
                                { value: 60, label: '60' },
                                { value: 80, label: '80' },
                                { value: 100, label: '100' }
                            ]}
                            defaultValue={50}
                            min={0}
                            max={100}
                            onChange={(_, value) => setFieldValue('availabilityWeeklyHours', value)}
                            classes={{
                                markLabel: classes.sliderMarkLabel,
                                markLabelActive: classes.sliderMarkLabelActive
                            }}
                        />
                        {/*<div className={classes.chip}>
                            <Chip />
                        </div>*/}
                        <Field
                            component={CheckboxWithLabel}
                            name="acceptTerms"
                            type="checkbox"
                            Label={{
                                label: (
                                    <Typography
                                        color={
                                            touched.acceptTerms && !!errors.acceptTerms ?
                                                'error' : 'initial'
                                        }
                                    >
                                        I accept the&nbsp;
                                        <Link to="/terms-of-use" target="_blank">
                                            terms of use
                                        </Link>
                                        &nbsp;*
                                    </Typography>
                                )
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
                            Sign Up
                        </Button>
                        <Link className={classes.formTextButton} to="/login">
                            <Button color="primary" fullWidth>
                                Existing user?
                            </Button>
                        </Link>
                    </Form>
                )}
            </Formik>
            <ReportBug />
        </Wrapper>
    );
};

export default Register;
