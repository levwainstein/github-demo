import { makeStyles } from '@material-ui/core/styles';
import StarIcon from '@material-ui/icons/Star';
import {
    Box,
    Rating as MuiRating,
    Snackbar,
    TextField,
    Tooltip,
    Typography
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { ActionCreatorWithPayload } from '@reduxjs/toolkit';
import {
    FunctionComponent,
    useCallback,
    useMemo,
    useState
} from 'react';

import { useAppDispatch } from '../../hooks';
import { isRatingsCompleted, RatingSubject, UserRating, UserRatings } from '../../types/rating';
import { ActionButton } from '..';

const useStyles = makeStyles((theme) => ({
    root: {
        padding: theme.spacing(2),
        display: 'flex'
    },
    ratingsContainer: {
        alignItems: 'center',
        width: 'wrap-content',
        flexDirection: 'column'
    },
    subjectContainer: {
        display: 'flex',
        flexDirection: 'row',
        textAlign: 'center',
        alignItems: 'center',
        gap: theme.spacing(2),
        marginBottom: theme.spacing(2),
        width: '100%',
        [theme.breakpoints.down('sm')]: {
            flexDirection: 'column'
        }
    },
    feedbackContainer: {
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'center',
        textAlign: 'center',
        alignContent: 'center',
        marginBottom: theme.spacing(2)
    },
    ratingSubtitle: {
        color: theme.palette.text.hint
    },
    feedbackLabel: {
        color: theme.palette.text.hint,
        alignItems: 'center',
        display: 'flex',
        '&.MuiTypography-root': {
            fontSize: '0.75rem',
            marginRight: theme.spacing(1)
        }
    },
    stars: {
        alignItems: 'center'
    },
    starIconEmpty: {
        color: '#65666E'
    },
    actionContainer: {
        width: '126px',
        alignSelf: 'center'
    },
    doneButton: {
        height: '42px',
        widht: '126px',
        background: 'linear-gradient(105.23deg, #FABB18 0%, #C48E02 100%)'
    },
    ratingTitle: {
        color: theme.palette.text.primary,
        cursor: 'text',
        marginRight: theme.spacing(1)
    }
}));

const FeedbackField = styled(TextField)({
    backgroundColor: '#32343E',
    alignItems: 'center',
    display: 'flex',
    width: '100%',
    '& .MuiInputBase-root': {
        padding: '5px 14px',
        width: '100%'
    },
    '& .MuiInputBase-input': {
        fontSize: '0.75rem',
        color: '#ffffff'
    }
});

const subjectTitles = (subject: RatingSubject): { title: string, subtitle: string } => {
    switch (subject) {
        case 'work_description':
            return { title: 'Description rating', subtitle: 'How would you rate the task description?' };
        case 'work_solution_match_requirements':
            return { title: 'QA rating', subtitle: 'How well does the solution match the task requirements?' };
        case 'work_solution_code_quality':
            return { title: 'Code rating', subtitle: 'How would you rate the quality of this solution\'s code?' };
        case 'work_review_qa_functionality':
            return { title: 'Review QA functionality', subtitle: 'How well did the reviewer QA all the edge cases and identify all quality problems?' };
        case 'work_review_code_quality':
            return { title: 'Review code quality', subtitle: 'How well did the reviewer assess the code and ensure its quality?' };
    }
};

const ratingScoreTooltipDescription = (subject: RatingSubject, score: number) : {title: string, subtitle: string} => {
    switch (subject) {
        case 'work_description':
            switch (score) {
                case 1: return { title: 'Poor', subtitle: '' };
                case 2: return { title: 'Below average', subtitle: '' };
                case 3: return { title: 'Average', subtitle: '' };
                case 4: return { title: 'Good', subtitle: '' };
                case 5: return { title: 'Excellent', subtitle: '' };
                default: return { title: '', subtitle: '' };
            }
        case 'work_solution_match_requirements':
            switch (score) {
                case 1: return { title: 'Poor. ', subtitle: 'The solution poorly aligns with the task requirements, lacking crucial features and functionality.' };
                case 2: return { title: 'Below average. ', subtitle: 'The solution somewhat matches the task requirements but falls short in addressing key aspects.' };
                case 3: return { title: 'Average. ', subtitle: 'The solution meets many task requirements, but there is room for improvement and additional features.' };
                case 4: return { title: 'Good. ', subtitle: 'The solution effectively matches most task requirements, but there are a few minor changes required.' };
                case 5: return { title: 'Excellent. ', subtitle: 'The solution perfectly aligns with the task requirements in terms of features and usability.' };
                default: return { title: '', subtitle: '' };
            }
        case 'work_solution_code_quality':
            switch (score) {
                case 1: return { title: 'Poor ', subtitle: 'code quality, with numerous issues, bugs, and inconsistencies.' };
                case 2: return { title: 'Below average ', subtitle: 'code quality, with noticeable shortcomings and areas for improvement.' };
                case 3: return { title: 'Average ', subtitle: 'code quality is acceptable, meeting the basic requirements but may have some room for improvement and occasional issues.' };
                case 4: return { title: 'Good ', subtitle: 'code quality, with solid features and reliable performance.' };
                case 5: return { title: 'Excellent ', subtitle: 'code quality, showcasing readability, efficiency and implementation of best practices.' };
                default: return { title: '', subtitle: '' };
            }
        case 'work_review_qa_functionality':
            switch (score) {
                case 1: return { title: 'Poor', subtitle: 'The reviewer barely tested any edge cases and missed major quality issues, showing a lack of thoroughness and attention.' };
                case 2: return { title: 'Below average', subtitle: 'The reviewer did not test most edge cases and missed many critical quality problems, leading to potential issues being overlooked.' };
                case 3: return { title: 'Average', subtitle: 'The reviewer identified some edge cases but missed several important quality issues that could impact the functionality.' };
                case 4: return { title: 'Good', subtitle: 'The reviewer identified most edge cases and quality problems but missed a few minor issues that were not critical.' };
                case 5: return { title: 'Excellent', subtitle: 'The reviewer thoroughly tested all edge cases, identified all potential issues, and provided comprehensive feedback, demonstrating a deep understanding of the functionality and attention to detail.' };
                default: return { title: '', subtitle: '' };
            }
        case 'work_review_code_quality':
            switch (score) {
                case 1: return { title: 'Poor', subtitle: 'The reviewer failed to review the code adequately, missing major quality issues, and did not contribute to improving the code’s overall quality.​' };
                case 2: return { title: 'Below average', subtitle: 'The reviewer gave minimal feedback on code quality, missed many critical issues, and provided little guidance for improvement.' };
                case 3: return { title: 'Average', subtitle: 'The reviewer provided some feedback on code quality but missed several key areas that needed attention, leaving room for significant improvement.' };
                case 4: return { title: 'Good', subtitle: 'The reviewer identified most code quality issues and made helpful suggestions but missed a few areas that could have been improved.' };
                case 5: return { title: 'Excellent', subtitle: 'The reviewer provided an excellent code review, catching all code quality issues, suggesting meaningful improvements, and ensuring the code met all best practices and standards.' };
                default: return { title: '', subtitle: '' };
            }
    }
};

export type Props = {
    // ratings object from global state
    ratings: UserRatings; 
    // ratings dtate action setter
    setRatings: ActionCreatorWithPayload<UserRatings, string>;
    // method to call on submit, if this is not given the 'Done' button is not shown
    onSubmit?: (ratings: UserRatings) => Promise<any>;
    // indicates if to show a title for this component
    showTitle?: boolean;
};

const Rating: FunctionComponent<Props> = ({ ratings, setRatings, onSubmit, showTitle=false }: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();

    const [ loading, setLoading ] = useState<boolean>(false);
    const [ showFeedbackInput, setShowFeedbackInput ] = useState<boolean>(false);
    const [ helperMessage, setHelperMessage ] = useState<string | undefined>();
    const [ tooltip, setTooltip ] = useState<{title: string, subtitle: string}>({ title: '', subtitle: '' });

    const handleScoreChange = useCallback((subject: RatingSubject, newScore: number | null) => {
        dispatch(
            setRatings({
                ...ratings,
                [subject]: {
                    score: newScore === null ? 0 : newScore,
                    feedback: ratings[subject].feedback
                }
            })
        );
        setShowFeedbackInput(true);
    }, [ ratings ]);

    const handleFeedbackChange = useCallback((subject: RatingSubject, newFeedback?: string) => {
        dispatch(
            setRatings({
                ...ratings,
                [subject]: {
                    score: ratings[subject].score,
                    feedback: newFeedback
                }
            })
        );
    }, [ ratings ]);

    const handleDoneClick = useCallback(() => {
        setLoading(true);

        if (!onSubmit) {
            setHelperMessage('Cannot submit. Please try again');
            return;
        }
        if (!canSubmit) {
            setHelperMessage('Please validate your rating. Please try again');
            return;
        }
        onSubmit(ratings)
            .then(() => setHelperMessage('Thank you for rating'))
            .catch((err) => setHelperMessage(err))
            .finally(() => setLoading(false));
    }, [ ratings, onSubmit ]);

    const canSubmit = useMemo(() => {
        return isRatingsCompleted(ratings);
    }, [ isRatingsCompleted, ratings ]);

    return (
        <Box className={classes.root} display="flex" flexDirection="column">
            {showTitle && (
                <Typography
                    className={classes.ratingTitle}
                    variant="h6"
                    component="h1"
                >
                    Rate this task
                </Typography>
            )}

            <Box className={classes.ratingsContainer}>
                {(Object.entries(ratings) as [ RatingSubject, UserRating ][]).map(([ subject, userRating ]) => {
                    const titles = subjectTitles(subject);
                    if (!titles) {
                        console.log('unrecognized rating subject: '+subject);
                        return null;
                    }

                    return (
                        <div key={`rating-${subject}`}>
                            <Box
                                className={classes.subjectContainer}
                            >
                                <Box>
                                    <Typography
                                        className={classes.ratingSubtitle}
                                        display="inline"
                                        fontSize="0.75rem"
                                        fontWeight={700}
                                    >
                                        {titles.title}:&nbsp;
                                    </Typography>
                                    <Typography
                                        className={classes.ratingSubtitle}
                                        display="inline"
                                        fontSize="0.75rem"
                                    >
                                        {titles.subtitle}
                                    </Typography>
                                </Box>
                                <Box>
                                    <Tooltip 
                                        title={<>
                                            <b>{tooltip.title}</b>{tooltip.subtitle}
                                        </>}
                                    >
                                        <MuiRating
                                            className={classes.stars}
                                            value={userRating.score}
                                            emptyIcon={<StarIcon fontSize="inherit" className={classes.starIconEmpty} />}
                                            onChange={
                                                (_event, value) => handleScoreChange(
                                                    subject, value
                                                )
                                            }
                                            onChangeActive={(event, hoverValue) => {
                                                setTooltip(ratingScoreTooltipDescription(subject, hoverValue));
                                            }}
                                        />
                                    </Tooltip>
                                </Box>
                            </Box>
                            {(showFeedbackInput || userRating.feedback) && (
                                <Box className={classes.feedbackContainer}>
                                    <Typography className={classes.feedbackLabel}>
                                        Feedback<br/>(optional)
                                    </Typography>
                                    <FeedbackField
                                        value={userRating.feedback}
                                        multiline
                                        rows={2}
                                        onChange={
                                            (event) => handleFeedbackChange(
                                                subject, event.target.value
                                            )
                                        }
                                        inputProps={{
                                            maxlength: 512
                                        }}
                                    />
                                </Box>
                            )}
                        </div>
                    );
                })}
            </Box>
            {onSubmit && Object.entries(ratings).length > 0 && (
                <Box className={classes.actionContainer}>
                    <ActionButton
                        buttonClassName={classes.doneButton}
                        onClick={handleDoneClick}
                        variant="contained"
                        text="Done"
                        disabled={!canSubmit || loading}
                    />
                </Box>
            )}

            <Snackbar
                open={!!helperMessage}
                autoHideDuration={6000}
                onClose={() => setHelperMessage(undefined)}
                message={helperMessage}
            />
        </Box>
    );
};

export default Rating;
