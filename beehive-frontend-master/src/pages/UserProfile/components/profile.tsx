import { Avatar, Button, Card, Grid, Slider, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { Field, Form, Formik } from 'formik';
import { TextField } from 'formik-material-ui';
import { FunctionComponent, useCallback } from 'react';

import { UserProfile } from '../../../types/user';
import Pic from './profile.jpg';

const useStyles = makeStyles(theme => {
    return {
        sizeAvatar: {
            height: '120px',
            width: '120px'
        },
        form: {
            paddingTop: '50px'
        },
        formFieldInput: {
            color: theme.palette.text.secondary
        },
        formFieldLabel: {
            color: '#807e7e'
        },
        sliderLabel: {
            color: '#807e7e',
            marginTop: theme.spacing(1),
            marginBottom: theme.spacing(-1)
        },
        sliderMarkLabel: {
            color: theme.palette.primary.light
        },
        sliderMarkLabelActive: {
            color: theme.palette.text.secondary
        },
        formButton: {
            marginTop: theme.spacing(1),
            marginRight: theme.spacing(1)
        },
        noSpinnerInputStyle: {
            '&::-webkit-outer-spin-button, &::-webkit-inner-spin-button': {
                '-webkit-appearance': 'none',
                display: 'none'
            }
        }
    };
});

type FormErrors = {
    pricePerHour?: string;
};

type Props = {
    profile: UserProfile | null;
    profileLoading: boolean;
    onProfileSubmit: (profileUpdateData: any) => Promise<void>;
    className?: string;
};

const Profile: FunctionComponent<Props> = ({
    profile,
    profileLoading,
    onProfileSubmit,
    className
}: Props) => {
    const classes = useStyles();

    const handleSubmit = useCallback(
        (values, { setSubmitting }) => {
            onProfileSubmit({
                firstName: values.firstName || 'null',
                lastName: values.lastName || 'null',
                githubUser: values.githubUser || 'null',
                trelloUser: values.trelloUser || 'null',
                upworkUser: values.upworkUser || 'null',
                availabilityWeeklyHours: values.availabilityWeeklyHours || -1,
                pricePerHour: values.pricePerHour || -1
            }).finally(() => {
                setSubmitting(false);
            });
        },
        [ onProfileSubmit ]
    );

    const handleValidate = useCallback(
        async (values) => {
            const errors: FormErrors = {};

            if (!/^(?:\d{1,2}(?:\.\d{1,2})?|\.\d{1,2})$/.test(String(values.pricePerHour))) {
                errors.pricePerHour = 'Invalid price format';
            }
            
            return errors;
        },
        []
    );

    return (
        <Card className={className}>
            <Grid container direction="row">
                <Grid item xl={2} lg={2} md={2} sm={4} xs={4}>
                    <Avatar className={classes.sizeAvatar} src={Pic} />
                </Grid>
                <Grid item xl={8} lg={8} md={8} sm={6} xs={6}>
                    <Typography variant="h4" color="primary">Profile</Typography>
                    <Formik
                        initialValues={{
                            email: profile?.email ?? '',
                            firstName: profile?.firstName ?? '',
                            lastName: profile?.lastName ?? '',
                            githubUser: profile?.githubUser ?? '',
                            trelloUser: profile?.trelloUser ?? '',
                            upworkUser: profile?.upworkUser ?? '',
                            availabilityWeeklyHours: profile?.availabilityWeeklyHours ?? 0,
                            pricePerHour: profile?.pricePerHour ? parseFloat(profile.pricePerHour) : 0
                        }}
                        enableReinitialize
                        validate={handleValidate}
                        onSubmit={handleSubmit}
                    >
                        {({ isSubmitting, setFieldValue, values }) => (
                            <Form className={classes.form}>
                                <Field
                                    component={TextField}
                                    name="firstName"
                                    label="First Name"
                                    autoComplete="first-name"
                                    fullWidth
                                    disabled={profileLoading || isSubmitting}
                                    InputProps={{
                                        classes: {
                                            root: classes.formFieldInput
                                        }
                                    }}
                                    InputLabelProps={{
                                        classes: {
                                            root: classes.formFieldLabel
                                        }
                                    }}
                                />
                                <Field
                                    component={TextField}
                                    name="lastName"
                                    label="Last Name"
                                    autoComplete="last-name"
                                    fullWidth
                                    disabled={profileLoading || isSubmitting}
                                    InputProps={{
                                        classes: {
                                            root: classes.formFieldInput
                                        }
                                    }}
                                    InputLabelProps={{
                                        classes: {
                                            root: classes.formFieldLabel
                                        }
                                    }}
                                />
                                <Field
                                    component={TextField}
                                    name="email"
                                    label="E-mail"
                                    type="email"
                                    autoComplete="email"
                                    fullWidth
                                    disabled
                                    InputProps={{
                                        classes: {
                                            root: classes.formFieldInput
                                        }
                                    }}
                                    InputLabelProps={{
                                        classes: {
                                            root: classes.formFieldLabel
                                        }
                                    }}
                                />
                                <Field
                                    component={TextField}
                                    name="githubUser"
                                    label="Github User"
                                    autoComplete="github-user"
                                    fullWidth
                                    disabled={profileLoading || isSubmitting}
                                    InputProps={{
                                        classes: {
                                            root: classes.formFieldInput
                                        }
                                    }}
                                    InputLabelProps={{
                                        classes: {
                                            root: classes.formFieldLabel
                                        }
                                    }}
                                />
                                <Field
                                    component={TextField}
                                    name="trelloUser"
                                    label="Trello User"
                                    autoComplete="trello-user"
                                    fullWidth
                                    disabled={profileLoading || isSubmitting}
                                    InputProps={{
                                        classes: {
                                            root: classes.formFieldInput
                                        }
                                    }}
                                    InputLabelProps={{
                                        classes: {
                                            root: classes.formFieldLabel
                                        }
                                    }}
                                />
                                <Field
                                    component={TextField}
                                    name="upworkUser"
                                    label="Upwork User"
                                    autoComplete="upwork-user"
                                    fullWidth
                                    disabled={profileLoading || isSubmitting}
                                    InputProps={{
                                        classes: {
                                            root: classes.formFieldInput
                                        }
                                    }}
                                    InputLabelProps={{
                                        classes: {
                                            root: classes.formFieldLabel
                                        }
                                    }}
                                />
                                
                                <Field
                                    component={TextField}
                                    name="pricePerHour"
                                    label="$ per hour"
                                    type="number"
                                    value={values.pricePerHour}
                                    step="0.5"
                                    min={0.0}
                                    max={99.9}
                                    InputProps={{
                                        classes: {
                                            root: classes.formFieldInput,
                                            input: classes.noSpinnerInputStyle
                                        }
                                    }}
                                    InputLabelProps={{
                                        classes: {
                                            root: classes.formFieldLabel
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
                                    //className={classes.formField}
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
                                    value={values.availabilityWeeklyHours}
                                    classes={{
                                        markLabel: classes.sliderMarkLabel,
                                        markLabelActive: classes.sliderMarkLabelActive
                                    }}
                                />
                                <Button
                                    className={classes.formButton}
                                    variant="contained"
                                    type="reset"
                                    disabled={profileLoading || isSubmitting}
                                >
                                    Cancel
                                </Button>
                                <Button
                                    className={classes.formButton}
                                    color="primary"
                                    variant="contained"
                                    type="submit"
                                    disabled={profileLoading || isSubmitting}
                                >
                                    Save
                                </Button>
                            </Form>
                        )}
                    </Formik>
                </Grid>
                <Grid item xl={2} lg={2} md={2} sm={2} xs={2}>
                </Grid>
            </Grid>
        </Card>
    );
};

export default Profile;
