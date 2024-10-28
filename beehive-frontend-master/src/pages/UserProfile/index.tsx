import { Card, Grid, Link, List, ListItem, ListItemText, Snackbar } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { FunctionComponent, useCallback, useEffect, useState } from 'react';

import { useAppDispatch } from '../../hooks';
import {
    loadAvailableSkills,
    loadUserProfile,
    updateUserProfile,
    UserSelectors
} from '../../reducers/user';
import { ReportBug, Wrapper } from '../../shared';
import { Billing, Profile, Skills } from './components';

function formatErrorMessage(error) {
    switch (error) {
        default:
            return 'Unknown error. Please try again';
    }
}

enum View {
    PROFILE,
    SKILLS,
    BILLING
}

const useStyles = makeStyles(theme => {
    return {
        root: {
            overflow: 'hidden',
            padding: 0
        },
        items: {
            height: '100vh',
            position: 'fixed',
            width: '15%',
            [theme.breakpoints.down('sm')]: {
                height: '40vh'
            }
        },
        activeItem: {
            paddingLeft: 20,
            paddingRight: 20,
            cursor: 'pointer',
            backgroundColor: '#262625',
            color: 'white',
            padding: '5px',
            borderRadius: '5px',
            textDecoration: 'none'
        },
        item: {
            paddingLeft: 20,
            cursor: 'pointer'
        },
        links: {
            textDecoration: 'none',
            color: '#000',
            fontWeight: 700
        },
        view: {
            marginTop: 25,
            marginRight: 25,
            padding: 30
        }
    };
});

type Props = Record<string, never>;

const UserProfile: FunctionComponent<Props> = ({ }: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();

    const [ profileError, setProfileError ] = useState<string | null>(null);
    const [ selectedView, setSelectedView ] = useState<View>(View.PROFILE);

    const { profile, profileLoading, availableSkills } = UserSelectors();

    useEffect(() => {
        // load user profile and available skills on mount
        dispatch(
            loadUserProfile({})
        ).unwrap().then(() => {
            return dispatch(loadAvailableSkills({}));
        }).catch((err) => {
            setProfileError(err.error);
        });
    }, []);

    const handleProfileSubmit = useCallback(
        (profileUpdateData) => {
            return dispatch(updateUserProfile(profileUpdateData)).unwrap().then(() => {
                // reload user profile
                dispatch(loadUserProfile({}));
            }).catch((err) => {
                setProfileError(err.error);
            });
        },
        [ dispatch, updateUserProfile, loadUserProfile, setProfileError ]
    );

    const handleSkillsSubmit = useCallback(
        (updatedSkills: string[]) => {
            return dispatch(updateUserProfile({
                skills: updatedSkills
            })).unwrap().then(() => {
                // reload user profile
                dispatch(loadUserProfile({}));
            }).catch((err) => {
                setProfileError(err.error);
            });
        },
        [ dispatch, updateUserProfile, loadUserProfile, setProfileError ]
    );

    return (
        <Wrapper loading={profileLoading}>
            <div className={classes.root}>
                <Grid container direction="row" spacing={2}>
                    <Grid item xl={2} lg={2} md={3} sm={12} xs={12}>
                        <div >
                            <Card className={classes.items}>
                                <List>
                                    <ListItem>
                                        <Link
                                            className={classes.links}
                                            onClick={() => setSelectedView(View.PROFILE)}
                                        >
                                            <ListItemText
                                                className={
                                                    selectedView === View.PROFILE ?
                                                        classes.activeItem : classes.item
                                                }
                                                primary="Profile"
                                            />
                                        </Link>
                                    </ListItem>
                                    <ListItem>
                                        <Link
                                            className={classes.links}
                                            onClick={() => setSelectedView(View.SKILLS)}
                                        >
                                            <ListItemText
                                                className={
                                                    selectedView === View.SKILLS ?
                                                        classes.activeItem : classes.item
                                                }
                                                primary="Skills"
                                            />
                                        </Link>
                                    </ListItem>
                                    <ListItem>
                                        <Link
                                            className={classes.links}
                                            onClick={() => setSelectedView(View.BILLING)}
                                        >
                                            <ListItemText
                                                className={
                                                    selectedView === View.BILLING ?
                                                        classes.activeItem : classes.item
                                                }
                                                primary="Billing"
                                            />
                                        </Link>
                                    </ListItem>
                                </List>
                            </Card>
                        </div>
                    </Grid>
                    <Grid item xl={10} lg={10} md={9} sm={12} xs={12}>
                        {selectedView === View.PROFILE && (
                            <Profile
                                className={classes.view}
                                profile={profile}
                                profileLoading={profileLoading}
                                onProfileSubmit={handleProfileSubmit}
                            />
                        )}
                        {selectedView === View.SKILLS && (
                            <Skills
                                className={classes.view}
                                skills={profile?.skills}
                                availableSkills={availableSkills}
                                profileLoading={profileLoading}
                                onSkillsSubmit={handleSkillsSubmit}
                            />
                        )}
                        {selectedView === View.BILLING && (
                            <Billing
                                className={classes.view}
                            />
                        )}
                    </Grid>
                </Grid>
            </div>

            {profileError && (
                <Snackbar
                    open={!!profileError}
                    autoHideDuration={6000}
                    onClose={() => setProfileError(null)}
                    message={formatErrorMessage(profileError)}
                />
            )}

            <ReportBug />
        </Wrapper>
    );
};

export default UserProfile;
