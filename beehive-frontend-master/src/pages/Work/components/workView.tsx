import { Box, Snackbar } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { FunctionComponent, useCallback, useEffect, useState } from 'react';
import { useResizeDetector } from 'react-resize-detector';
import {
    Fill,
    ResizeHandlePlacement,
    TopResizable,
    ViewPort
} from 'react-spaces';

import { useAppDispatch, useNoDefaultHotkeys } from '../../../hooks';
import {
    activateWork,
    analyzeWorkSolution,
    cancelWork,
    checkpointWork,
    clearWorkActionError,
    loadAvailableWork,
    setWorkActionError,
    skipWork,
    submitWorkFeedback,
    submitWorkRating,
    submitWorkSolution,
    submitWorkTypeCorrection,
    WorkSelectors
} from '../../../reducers/work';
import { isRatingsCompleted, RatingSubject, UserRatings } from '../../../types/rating';
import { isReviewWorkItem, WorkItem, WorkReviewStatus } from '../../../types/work';
import {
    Details,
    SolutionReview
} from './work';
import BeehaveReviewDisplay from './work/beehaveReviewDisplay';

const useStyles = makeStyles((theme) => {
    return {
        root: {
            backgroundColor: theme.palette.background.default,
            display: 'flex',
            flexGrow: 1,
            flexDirection: 'column'
        },
        workPanel: {
            width: 'auto',
            display: 'flex',
            flexDirection: 'column',
            flexGrow: 1
        },
        spacesViewPort: {
            // `top` style is copied from the theme toolbar mixin:
            // https://github.com/mui/material-ui/blob/b6b9314ac7f032bf87714dde36ad6dd6b43277c8/packages/mui-material/src/styles/createMixins.js#LL3C15-L3C15
            top: '56px !important',
            [theme.breakpoints.up('xs')]: {
                '@media (orientation: landscape)': {
                    top: '48px !important'
                }
            },
            [theme.breakpoints.up('sm')]: {
                top: '64px !important'
            },
            margin: theme.spacing(1)
        },
        detailsCollapse: {
            height: '100%',
            background: theme.palette.primary.dark,
            overflowY: 'scroll'
        },
        externalDetailsContainer: {
            flexGrow: 1,
            background: theme.palette.primary.dark,
            flexBasis: 0
        },
        markdownWrapper: {
            display: 'inline-block',
            textAlign: 'start',
            width: '100%',
            overflowY: 'scroll',
            flexGrow: 1,
            flexBasis: 0
        },
        reviewContainer: {
            flexGrow: 1,
            marginTop: theme.spacing(2),
            background: theme.palette.primary.dark
        }
    };
});

const formatErrorMessage = (error) => {
    switch (error) {
        case 'package_builtin':
            return 'This is a built in package. You can import it without installation.';
        case 'rating':
            return 'Error while submitting rating. Please try again';
        case 'rating_invalid':
            return 'Please fill in a rating score between 1-5.';
        case 'qa_toggle': 
            return 'Please choose further instructions in toggle button.';
        case 'analyze_no_changes':
            return 'Analyze skipped, no changes detected in PR since last analyze.';
        case 'analyze_unexpected_error':
            return 'Analyze failed due to unexpected error.';
        default:
            return 'Unknown error. Please try again';
    }
};

const renderResizeHandle = (props: {[key: string]: any}, orientation: 'vertical' | 'horizontal') => {
    const vertical = orientation === 'vertical';

    return (
        <div
            {...props}
            style={{
                display: 'flex',
                justifyContent: 'center',
                flexDirection: vertical ? 'row' : 'column'
            }}
        >
            <div
                style={{
                    position: 'absolute',
                    transform: vertical ? 'translateY(-50%)' : 'translateX(-50%)',
                    margin: 'auto',
                    borderRadius: 2,
                    width: vertical ? 24 : 4,
                    height: vertical ? 4 : 24,
                    backgroundColor: '#434252'
                }}
            />
        </div>
    );
};

type Props = {
    work: WorkItem;
};

const WorkView: FunctionComponent<Props> = ({ work }: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();

    // global state
    const {
        workLoading,
        workActionError,
        workActive,
        workDone,
        workStartTimeEpochMs,
        workRatings,
        workRatingAuthorizationCode,
        workRecordRatings,
        workRecordRatingAuthorizationCode,
        activeWorkRecord
    } = WorkSelectors();

    const [ detailsResizableSize, setDetailsResizabeSize ] = useState<number>(380);
    const [ solutionReviewApproved, setSolutionReviewApproved ] = useState<boolean | null>(null);
    const [ wasBeehaveReviewed, setWasBeehaveReviewed ] = useState(Boolean(activeWorkRecord?.latestBeehaveReview));

    const {
        height: detailsCollapsibleHeight
    } = useResizeDetector();

    useEffect(() => {
        // reset work-specific values when work changes
        setWasBeehaveReviewed(Boolean(activeWorkRecord?.latestBeehaveReview));
        setSolutionReviewApproved(null);
    }, [ work, activeWorkRecord ]);

    useEffect(() => {
        if (isReviewWorkItem(work.workType) && workActive) {
            setDetailsResizabeSize(300);
        }        
    }, [ isReviewWorkItem, work, workActive, setDetailsResizabeSize ]);

    const _calculateDurationSeconds = () => {
        return Math.round((Date.now() - workStartTimeEpochMs) / 1000);
    };

    const handleSkipWork = useCallback(
        () => {
            const startTimeEpochMs = Date.now();
            const tzName = Intl.DateTimeFormat().resolvedOptions().timeZone;

            dispatch(skipWork({
                workId: work.id,
                startTimeEpochMs, 
                tzName 
            }));
            dispatch(loadAvailableWork({ currentWorkId: work.id }));
        },
        [ dispatch, loadAvailableWork, work ]
    );

    const handleNextWork = () => {
        if (!isRatingsCompleted(workRatings)) {
            dispatch(setWorkActionError('rating_invalid'));
            return;
        }
        
        submitRatings(workRatings, workRatingAuthorizationCode)
            .catch(payload => {
                console.log('error rating', payload);
            }).then(() => {
                dispatch(loadAvailableWork({ currentWorkId: work.id }));
            });
    };

    const handleActivateWork = useCallback(
        () => {
            const workStartTimeEpochMs = Date.now();
            const tzName = Intl.DateTimeFormat().resolvedOptions().timeZone;

            dispatch(
                activateWork({
                    workId: work.id,
                    workType: work.workType,
                    startTimeEpochMs: workStartTimeEpochMs,
                    tzName
                })
            );
        },
        [ activateWork, dispatch, work ]
    );

    const handleCancelWork = useCallback(
        () => {
            const durationSeconds = _calculateDurationSeconds();

            // checkpoint work before cancelling
            dispatch(
                checkpointWork({
                    workId: work.id,
                    durationSeconds
                })
            );

            // cancel work without waiting for checkpoint to be done
            dispatch(
                cancelWork({
                    workId: work.id,
                    durationSeconds
                })
            );
        },
        [
            _calculateDurationSeconds,
            cancelWork,
            checkpointWork,
            dispatch,
            work
        ]
    );

    const _handleSubmitWorkSolution = (
        reviewStatus?: number, reviewFeedback?: string, solutionUrl?: string
    ) => {
        const durationSeconds = _calculateDurationSeconds();

        dispatch(
            submitWorkSolution({
                workId: work.id,
                durationSeconds,
                reviewStatus,
                reviewFeedback,
                solutionUrl
            })
        );
    };

    const handleSubmitSolutionReview = () => {
        if (!isRatingsCompleted(workRecordRatings)) {
            dispatch(setWorkActionError('rating_invalid'));
            return;
        }
        if (solutionReviewApproved === null) {
            dispatch(setWorkActionError('qa_toggle'));
            return;
        }
        const reviewStatus = solutionReviewApproved ? WorkReviewStatus.ADEQUATE : WorkReviewStatus.INADEQUATE;

        submitRatings(workRecordRatings, workRecordRatingAuthorizationCode)
            .catch(payload => {
                console.log('error rating', payload);
            }).then(() => {
                _handleSubmitWorkSolution(reviewStatus);
            });
    };

    const handleSubmitWorkFeedback = useCallback(
        (feedback: string) => {
            dispatch(
                submitWorkFeedback({
                    workId: work.id,
                    feedback,
                    durationSeconds: _calculateDurationSeconds()
                })
            );
        },
        [ dispatch, submitWorkFeedback, work, _calculateDurationSeconds ]
    );

    const handleSubmitUrlSolution = useCallback(
        (solutionUrl?: string) => {
            _handleSubmitWorkSolution(undefined, undefined, solutionUrl);
        },
        [ _handleSubmitWorkSolution ]
    );

    const handleAnalyzeUrlSolution = useCallback(
        (solutionUrl: string) => {
            dispatch(
                analyzeWorkSolution({
                    workId: work.id,
                    solutionUrl
                })
            ).then(() => {
                setWasBeehaveReviewed(true);
            });
        },
        [ analyzeWorkSolution, dispatch, work ]
    );

    const submitRatings = useCallback(
        (ratings: UserRatings, authorizationCode: string) => {
            return Promise.all(
                Object.keys(ratings).map((subject) => {
                    if (ratings[subject].score === 0) {
                        return Promise.reject();
                    }
                    return dispatch(
                        submitWorkRating({
                            code: authorizationCode,
                            subject: subject as RatingSubject,
                            rating: ratings[subject]
                        })
                    ).unwrap();
                })
            ).catch(function (err) {
                console.log('An error while rating work: ', err);
                dispatch(setWorkActionError('rating'));
            });
        },
        [ dispatch, submitWorkRating ]
    );

    const handleSubmitWorkRatings = useCallback(
        (ratings: UserRatings) => {
            if (!isRatingsCompleted(ratings)) {
                dispatch(setWorkActionError('rating_invalid'));
                return Promise.reject();
            }
            
            return submitRatings(ratings, workRatingAuthorizationCode)
                .catch(payload => {
                    console.log('error rating: ', payload);
                });
        },
        [ dispatch, isRatingsCompleted, submitRatings ]
    );

    const handleSubmitTaskClassificationCorrection = useCallback(
        (predictedOutput, correctedOutput) => {
            dispatch(
                submitWorkTypeCorrection({
                    input: {
                        'description': work.description,
                        'skills': work.skills
                    },
                    predictedOutput: predictedOutput,
                    correctedOutput: correctedOutput
                })
            );
        },
        [ dispatch, work ]
    );

    // hotkeys
    useNoDefaultHotkeys('ctrl + y', () => {
        if (workActive && !workDone) {
            handleCancelWork();
        }
    });

    return (
        <Box className={classes.root}>
            {workActive && !workDone && isReviewWorkItem(work.workType) ? (
                <div className={classes.workPanel}>
                    <ViewPort className={classes.spacesViewPort}>
                        <TopResizable
                            size={
                                detailsCollapsibleHeight
                                    ? Math.min(
                                        detailsResizableSize,
                                        detailsCollapsibleHeight + 5
                                    )
                                    : detailsResizableSize
                            }
                            handlePlacement={ResizeHandlePlacement.Inside}
                            handleRender={
                                (props) =>
                                    renderResizeHandle(props, 'vertical')
                            }
                            onResizeEnd={
                                (newSize) =>
                                    newSize &&
                                    typeof newSize === 'number' &&
                                    setDetailsResizabeSize(newSize)
                            }
                        >
                            <Box
                                className={classes.detailsCollapse}
                                style={{ display: 'block' }}
                            >
                                <Details
                                    data-testid="work-details"
                                    workId={work.id}
                                    workType={work.workType}
                                    workPriority={work.priority}
                                    description={work.description}
                                    taskId={work.taskId}
                                    taskTypeClassification={work.taskType}
                                    skills={work.skills}
                                    workLoading={workLoading}
                                    workActive={workActive}
                                    workStartTimeEpochMs={workStartTimeEpochMs}
                                    workDone={workDone}
                                    handleActivateWork={handleActivateWork}
                                    handleCancelWork={handleCancelWork}
                                    handleSkipWork={handleSkipWork}
                                    handleNextWorkClick={handleNextWork}
                                    handleSubmitWorkFeedback={handleSubmitWorkFeedback}
                                    handleSubmitUrlSolution={handleSubmitUrlSolution}
                                    handleSubmitSolutionReview={handleSubmitSolutionReview}
                                    handleSubmitRating={handleSubmitWorkRatings}
                                    handleSubmitTaskClassificationCorrection={handleSubmitTaskClassificationCorrection}
                                    handleAnalyzeUrlSolution={handleAnalyzeUrlSolution}
                                    submitConditionsFulfilled={solutionReviewApproved !== null}
                                />
                            </Box>
                        </TopResizable>
                        <Fill>
                            <Box
                                className={classes.detailsCollapse}
                                style={{ display: 'block' }}
                            >
                                <Box className={classes.markdownWrapper}>
                                    <SolutionReview
                                        solutionUrl={work.workInput ? work.workInput.solution_url : null}
                                        setReviewApproved={setSolutionReviewApproved}
                                    />
                                </Box>
                            </Box>
                        </Fill>
                    </ViewPort>
                </div>
            ) : (
                <Box className={classes.externalDetailsContainer}>
                    <Details
                        data-testid="work-details"
                        workId={work.id}
                        workType={work.workType}
                        workPriority={work.priority}
                        title={work.title}
                        description={work.description}
                        branchName={work.branchName}
                        repoName={work.repoName}
                        repoUrl={work.repoUrl}
                        taskId={work.taskId}
                        taskTypeClassification={work.taskType}
                        skills={work.skills}
                        workLoading={workLoading}
                        workActive={workActive}
                        workStartTimeEpochMs={workStartTimeEpochMs}
                        workDone={workDone}
                        handleActivateWork={handleActivateWork}
                        handleCancelWork={handleCancelWork}
                        handleSkipWork={handleSkipWork}
                        handleNextWorkClick={handleNextWork}
                        handleSubmitWorkFeedback={handleSubmitWorkFeedback}
                        handleSubmitUrlSolution={handleSubmitUrlSolution}
                        handleSubmitSolutionReview={handleSubmitSolutionReview}
                        handleSubmitRating={handleSubmitWorkRatings}
                        handleSubmitTaskClassificationCorrection={handleSubmitTaskClassificationCorrection}
                        handleAnalyzeUrlSolution={handleAnalyzeUrlSolution}
                        submitConditionsFulfilled={wasBeehaveReviewed}
                    />
                </Box>
            )}
            {/* error snackbar */}
            {workActionError && (
                <Snackbar
                    open={!!workActionError}
                    autoHideDuration={6000}
                    onClose={() => dispatch(clearWorkActionError())}
                    message={formatErrorMessage(workActionError)}
                />
            )}
            {activeWorkRecord?.latestBeehaveReview &&
                <Box className={classes.reviewContainer}>
                    <BeehaveReviewDisplay workId={work.id} reviewResult={activeWorkRecord?.latestBeehaveReview} />
                </Box>}
            {/* error snackbar */}
            {workActionError && (
                <Snackbar
                    open={!!workActionError}
                    autoHideDuration={6000}
                    onClose={() => dispatch(clearWorkActionError())}
                    message={formatErrorMessage(workActionError)}
                />
            )}
        </Box>
    );
};

export default WorkView;
