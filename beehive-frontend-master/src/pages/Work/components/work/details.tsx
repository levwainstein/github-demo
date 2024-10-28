import { Box, Chip, Divider } from '@material-ui/core';
import { Grid, Typography } from '@material-ui/core';
import { makeStyles, Theme } from '@material-ui/core/styles';
import { FunctionComponent, useCallback, useEffect, useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';

import { setWorkRatings, WorkSelectors } from '../../../../reducers/work';
import { durationSecondsAsString, humanize } from '../../../../services/utils';
import { Rating } from '../../../../shared';
import { UserRatings } from '../../../../types/rating';
import { TaskTypeClassification } from '../../../../types/task';
import { isReviewWorkItem, workMaxDurationMs, WorkType } from '../../../../types/work';
import Actions from './actions';
import External from './external';
import WorkTitle from './title';

const useStyles = makeStyles<Theme>(theme => {
    return {
        root: {
            display: 'inline-block',
            height: '100%',
            width: '100%'
        },
        container: {
            borderRadius: '5px',
            color: theme.palette.text.primary,
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            overflowY: 'scroll'
        },
        detailsContainer: {
            display: 'flex',
            flexDirection: 'column',
            height: '100%'
        },
        descriptionTitleContainer: {
            display: 'flex',
            flexDirection: 'row',
            gap: 10,
            padding: theme.spacing(2),
            paddingBottom: theme.spacing(1)
        },
        gridContainer: {
            height: '100%',
            paddingLeft: theme.spacing(2),
            paddingRight: theme.spacing(2),
            paddingBottom: theme.spacing(1)
            // overflowY: 'scroll'
        },
        markdownWrapper: {
            display: 'inline-block',
            textAlign: 'start',
            width: '100%',
            // overflowY: 'scroll',
            flexGrow: 1,
            flexBasis: 0
        },
        markdown: {
            '& p > a': {
                color: theme.palette.secondary.main
            },
            '& p > a:visited': {
                color: theme.palette.secondary.dark
            }
        },
        warning: {
            color: 'red',
            paddingBottom: 7,
            textAlign: 'start'
        },
        normal: {
            color: 'white',
            paddingBottom: 7,
            textAlign: 'start'
        },
        actions: {
            display: 'flex',
            flexDirection: 'column',
            border: '1px solid #31333E',
            borderRadius: '5px',
            padding: theme.spacing(2),
            [theme.breakpoints.down('sm')]: {
                marginRight: theme.spacing(1),
                padding: theme.spacing(1)
            }
        },
        priority: {
            position: 'relative',
            left: '50%',
            transform: 'translateX(-50%)',
            color: 'white',
            backgroundColor: 'red',
            padding: 2,
            paddingLeft: 10,
            paddingRight: 10,
            textAlign: 'center',
            width: 'fit-content',
            borderRadius: '10px',
            marginBottom: 5
        },
        externalContainer: {
            marginTop: theme.spacing(2)
        },
        divider: {
            backgroundColor: '#31333E',
            margin: '2px 5px 2px 5px'
        }
        /*compensationActionsDivider: {
            marginTop: '7px',
            // margin: '7px -10px 0px -10px',
            backgroundColor: '#31333E'
        },
        taskCompensation: {
            fontSize: '14px'
        },
        compensationStack: {
            display: 'flex',
            flexDirection: 'row',
            justifyContent: 'space-between'
        }*/
    };
});

type Props = {
    workId: number;
    workType: WorkType;
    workPriority?: number;
    title?: string;
    description: string;
    branchName?: string;
    repoName?: string;
    repoUrl?: string;
    taskId?: string;
    taskTypeClassification?: TaskTypeClassification;
    skills?: [string];
    workLoading: boolean;
    workActive: boolean;
    workStartTimeEpochMs: number;
    workDone: boolean;
    handleActivateWork: () => void;
    handleSkipWork: () => void;
    handleNextWorkClick: () => void;
    handleCancelWork: () => void;
    handleSubmitWorkFeedback: (feedback: string) => void;
    handleSubmitUrlSolution: (url: string) => void;
    handleSubmitSolutionReview: () => void;
    handleAnalyzeUrlSolution: (url: string) => void;
    handleSubmitRating: (ratings: UserRatings) => Promise<any>;
    handleSubmitTaskClassificationCorrection: (predictedOutput: string, correctedOutput: string) => void;
    submitConditionsFulfilled: boolean;
};

const Details: FunctionComponent<Props> = ({
    workId,
    workType,
    workPriority,
    title,
    description,
    branchName,
    repoName,
    repoUrl,
    taskId,
    taskTypeClassification,
    skills,
    workLoading,
    workActive,
    workStartTimeEpochMs,
    workDone,
    handleActivateWork,
    handleSkipWork,
    handleNextWorkClick,
    handleCancelWork,
    handleSubmitWorkFeedback,
    handleSubmitUrlSolution,
    handleSubmitSolutionReview,
    handleAnalyzeUrlSolution,
    handleSubmitRating,
    handleSubmitTaskClassificationCorrection,
    submitConditionsFulfilled,
    ...other
}: Props) => {
    const classes = useStyles();

    function appendOrReplaceGithubData(description: string, branchName: string | undefined, repoName: string | undefined, repoUrl: string | undefined): string {
        const repoSlug = repoName && repoUrl ? '**Github repo:** [' + repoName + '](' + repoUrl + ') (an invite will be sent if you accept the task)\n\n' : null;
        const branchSlug = branchName ? '**Github branch for this task:** `' + branchName + '`' : null;

        // Helper function to replace or append a slug in the description
        const replaceOrAppend = (description: string, label: string, newSlug: string | null) => {
            const pattern = new RegExp(`${label}[^\\n]+`);
            if (newSlug) {
                if (description.match(pattern)) {
                    // Replace the existing slug with the new one
                    return description.replace(pattern, newSlug);
                } else {
                    // Append the new slug if not found
                    return description + '\n\n---\n\n' + newSlug;
                }
            }
            return description;
        };

        if (repoSlug) {
            description = replaceOrAppend(description, '\\*\\*Github repo:\\*\\* \\[', repoSlug);
        }
        if (branchSlug) {
            description = replaceOrAppend(description, '\\*\\*Github branch for this task:\\*\\* `', branchSlug);
        }

        return description;
    }

    const descriptionMarkdown = useMemo(
        () => appendOrReplaceGithubData(description, branchName, repoName, repoUrl).replace(/\n/gi, '  \n'),
        [ description ]
    );

    const [ currentTime, setCurrentTime ] = useState<number>(Date.now());
    const [ workRatingSubmitted, setWorkRatingSubmitted ] = useState<boolean>(false);

    const { workRatings } = WorkSelectors();

    const timeInProcess = useMemo(
        () => currentTime - workStartTimeEpochMs,
        [ currentTime, workStartTimeEpochMs ]
    );

    const targetDate = useMemo(
        () => new Date(workStartTimeEpochMs + workMaxDurationMs - (new Date().getTimezoneOffset() * 60000)).toISOString().slice(0, -8),
        [ workMaxDurationMs, workStartTimeEpochMs ]
    );

    const timeRemaining = useMemo(
        () => durationSecondsAsString(Math.max((workMaxDurationMs - timeInProcess) / 1000, 0)),
        [ workMaxDurationMs, timeInProcess ]
    );

    const isLessThan12Hours = useMemo(
        () => workMaxDurationMs - timeInProcess < 12 * 60 * 60 * 1000,
        [ workMaxDurationMs, timeInProcess ]
    );

    useEffect(() => {
        setCurrentTime(Date.now());

        // update the formatted time every 60 seconds
        const updateInterval = setInterval(() => {
            setCurrentTime(Date.now());
        }, 60000);

        return () => {
            clearInterval(updateInterval);
        };
    }, []);

    const onSubmitRating = useCallback(
        (ratings: UserRatings) => {
            setWorkRatingSubmitted(true);
            return handleSubmitRating(ratings);
        },
        [ handleSubmitRating, setWorkRatingSubmitted ]
    );

    return (
        <Box key={`details-${workId}`}
            className={classes.root}
            {...other}
        >
            <Box className={classes.container}>
                <Box className={classes.descriptionTitleContainer}>
                    <WorkTitle
                        taskTypeClassification={ taskTypeClassification }
                        onSubmit= {handleSubmitTaskClassificationCorrection}
                        defaultTitle={workType === WorkType.CUCKOO_COMMUNITY_REVIEW ? 'Community Review Task Description' : 'Task Description'}
                    />
                    {skills && skills.map((skill) => (
                        <Chip
                            key={`skill-chip-${skill}`}
                            label={humanize(skill)}
                            color="primary"
                            disabled={true}
                        />
                    ))}
                </Box>
                <Grid container className={classes.gridContainer} spacing={2}>
                    <Grid item xl={8} lg={8} md={7} sm={6} xs={6}>
                        <Box className={classes.detailsContainer}>
                            {title && 
                            <Typography
                                variant="h6"
                                component="p"
                                align="left"
                            >
                                {title}
                            </Typography>
                            }
                            <Box className={classes.markdownWrapper}>
                                <ReactMarkdown
                                    className={classes.markdown}
                                    source={descriptionMarkdown}
                                    linkTarget="_blank"
                                    transformLinkUri={(uri) => {
                                        const urlStr = ReactMarkdown.uriTransformer(uri);

                                        if (urlStr.indexOf(':') === -1) {
                                            return `https://${urlStr}`;
                                        } else {
                                            return urlStr;
                                        }
                                    }}
                                />
                            </Box>
                            <Divider className={classes.divider}/>

                            {!workActive && !workRatingSubmitted && (
                                <Box className={classes.markdownWrapper}>
                                    <Rating
                                        ratings={workRatings}
                                        setRatings={setWorkRatings}
                                        onSubmit={onSubmitRating}
                                    />
                                </Box>
                            )}

                        </Box>
                    </Grid>
                    <Grid item xl={4} lg={4} md={5} sm={6} xs={6}>
                        {(!workDone || workActive) && (
                            <Box className={classes.actions}>
                                {!workDone && (
                                    <>
                                        {(workPriority && workPriority > 2) && (
                                            <Typography
                                                variant="body2"
                                                component="p"
                                                align="center"
                                                className={classes.priority}
                                            >
                                                {'High Priority'}
                                            </Typography>
                                        )}
                                        <Typography
                                            variant="body2"
                                            component="p"
                                            align="center"
                                            className={
                                                workActive && !isLessThan12Hours
                                                    ? classes.normal
                                                    : classes.warning
                                            }
                                        >
                                            {workActive ? `Task deadline: ${targetDate} Time remaining: ${timeRemaining} hours` : 
                                                'Tasks are expected to be submitted within 10 hours and otherwise will be released back to the queue (unless you pre-approve it with our staff)'}
                                        </Typography>
                                        <Box display="flex" flexDirection="row" >
                                            <Actions
                                                data-testid="work-actions"
                                                taskId={taskId || ''}
                                                workActive={workActive}
                                                workLoading={workLoading}
                                                onCancelClick={handleCancelWork}
                                                onAcceptClick={handleActivateWork}
                                                onSkipClick={handleSkipWork}
                                                onSubmitFeedback={handleSubmitWorkFeedback}
                                            />
                                        </Box>
                                    </>
                                )}
                                {workActive && (
                                    <Box className={classes.externalContainer}>
                                        <External
                                            workActive={workActive}
                                            workDone={workDone}
                                            workLoading={workLoading}
                                            handleCancelWork={
                                                handleCancelWork
                                            }
                                            handleSubmitUrlSolution={
                                                handleSubmitUrlSolution
                                            }
                                            handleSubmitSolutionReview={
                                                handleSubmitSolutionReview
                                            }
                                            handleNextWorkClick={
                                                handleNextWorkClick
                                            }
                                            requirePRUrl={!isReviewWorkItem(workType)}
                                            handleAnalyzeUrlSolution={
                                                handleAnalyzeUrlSolution
                                            }
                                            submitConditionsFulfilled={submitConditionsFulfilled}
                                        />
                                    </Box>
                                )}
                            </Box>
                        )}
                    </Grid>
                </Grid>
            </Box>
        </Box>
    );
};

export default Details;
