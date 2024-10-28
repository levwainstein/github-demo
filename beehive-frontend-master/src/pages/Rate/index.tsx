import { makeStyles } from '@material-ui/core/styles';
import { Box, Typography } from '@mui/material';
import clsx from 'clsx';
import { FunctionComponent, useCallback, useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

import { useAppDispatch } from '../../hooks';
import { setWorkRecordRatings, submitWorkRating, WorkSelectors } from '../../reducers/work';
import { Rating, ReportBug, Wrapper } from '../../shared';
import { initUserRatings, RatingSubject, UserRatings } from '../../types/rating';

const useStyles = makeStyles((theme) => ({
    root: {
        backgroundColor: theme.palette.background.default,
        width: '100vw',
        height: '100vh'
    },
    ratingContainer: {
        width: '90%',
        marginTop: theme.spacing(3),
        marginLeft: 'auto',
        marginRight: 'auto'
    },
    title: {
        textAlign: 'center',
        color: '#E9E9EA'
    },
    error: {
        color: theme.palette.error.dark
    }
}));

type Props = Record<string, never>;

const Rate: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();
    const location = useLocation();

    const [ codes, setCodes ] = useState<{subject: RatingSubject, code: string}[]>([]);
    const [ error, setError ] = useState<boolean>(false);
    const { workRecordRatings } = WorkSelectors();

    useEffect(() => {
        if (location) {
            const searchParams = new URLSearchParams(location.search.slice(1));

            const subjectsParam = searchParams.get('subjects');
            const codeParam = searchParams.get('code');
            
            if (!subjectsParam || !codeParam) {
                setError(true);
                return;
            }

            // if query contains tilde that represents different objects to rate, order of subjects correspond to order of codes
            const objectsSubjects = subjectsParam.split('~');
            const objectsCodes = codeParam.split('~');
            if (objectsSubjects.length !== objectsCodes.length) {
                setError(true);
                return;
            }

            // every rates object can contain multiple subjects
            let initialUserRatings = {} as UserRatings;
            for (let i = 0; i < objectsCodes.length; i++) {
                const subjects = objectsSubjects[i].split(',');
                const code = objectsCodes[i];

                initialUserRatings = { ...initialUserRatings, ...initUserRatings(subjects as RatingSubject[]) };
                 
                setCodes((currCodes) => [ ...currCodes, ...subjects.map((subject) => ({ subject: subject as RatingSubject, code: code })) ]);

            }

            if (Object.keys(initialUserRatings).length > 0) {
                dispatch(setWorkRecordRatings(initialUserRatings));
            }

        }
    }, [ location, dispatch, setWorkRecordRatings, initUserRatings, setCodes ]);

    const handleSubmit = useCallback(
        async (ratings: UserRatings) => {
            // execute requests in order to prevent a token race if the access
            // token needs to be refreshed
            for (const subject of Object.keys(ratings)) {
                const code = codes.filter((subjectCode) => subjectCode.subject === subject)[0].code;
                await dispatch(
                    submitWorkRating({
                        code: code,
                        subject: subject as RatingSubject,
                        rating: ratings[subject]
                    })
                ).unwrap();
            }
        },
        [ dispatch, submitWorkRating, codes ]
    );

    return (
        <Wrapper loading={false}>
            <Box className={classes.root}>
                <Box className={classes.ratingContainer}>
                    {error ? (
                        <Typography
                            className={clsx(classes.title, classes.error)}
                            mb={3}
                            fontSize="1rem"
                            fontWeight={600}
                        >
                            An unknown error has occurred
                        </Typography>
                    ) : (
                        <>
                            <Typography
                                className={classes.title}
                                mb={3}
                                fontSize="1rem"
                                fontWeight={600}
                            >
                                Rate this task solution
                            </Typography>
                            <Rating
                                ratings={workRecordRatings}
                                setRatings={setWorkRecordRatings}
                                onSubmit={handleSubmit}
                            />
                        </>
                    )}
                </Box>
                <ReportBug />
            </Box>
        </Wrapper>
    );
};

export default Rate;
