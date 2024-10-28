import { Snackbar } from '@material-ui/core';
import Box from '@mui/material/Box';
import { FunctionComponent, useCallback, useEffect, useMemo, useState } from 'react';

import { useAppDispatch } from '../../../hooks';
import { loadUserProfile, UserSelectors } from '../../../reducers/user';
import { activateWork, analyzeWorkSolution, cancelWork, checkpointWork, clearWorkActionError, loadAvailableWork, skipWork, submitWorkFeedback, submitWorkSolution, WorkSelectors } from '../../../reducers/work';
import { durationSecondsAsString } from '../../../services/utils';
import { SelectModal } from '../../../shared';
import { ContributorWorkSteps } from '../../../types/contributorWork';
import { WorkItem, workMaxDurationMs } from '../../../types/work';
import { options } from '../../../types/workTypes'; 
import AddPullRequest from './AddPullRequest';
import CodeReview from './CodeReview';
import Description from './Description';
import Dialogs from './dialogs';
import FooterButtons from './FooterButtons';
import Header from './Header';
import { backwardsSupportParseFromDescription } from './helpers';
import { BG, Container, DescriptionTermsContainer, DescriptionWrapper } from './styled';
import TaskCompleted from './TaskCompleted';
import Terms from './Terms';

type Props = {
    work: WorkItem;
};

const ContributorWork: FunctionComponent<Props> = ({ work }: Props) => {
    const dispatch = useAppDispatch();
    const { workStartTimeEpochMs, workActive, activeWorkRecord, workLoading, workActionError } = WorkSelectors();
    const { profile } = UserSelectors();
    const [ currentIndex ] = useState(0); // todo remove
    const [ iReadChecked, setIreadChecked ] = useState<boolean>(false);
    const [ currentStep, setCurrentStep ] = useState<ContributorWorkSteps>(workActive ? ContributorWorkSteps.AnalyzePullRequest : ContributorWorkSteps.TaskAccept);
    const [ solutionUrl, setSolutionUrl ] = useState<string>('');
    const [ feedbackDialogOpen, setFeedbackDialogOpen ] = useState(false);
    const [ cancellationDialogOpen, setCancellationDialogOpen ] = useState(false);
    const [ feedbackAdded, setFeedbackAdded ] = useState<boolean>(false);
    const [ isVisible, setIsVisible ] = useState<boolean>(false);
    const [ didRunBeehave, setDidRunBeehave ] = useState<boolean>(false);

    const [ currentTime, setCurrentTime ] = useState<number>(Date.now());

    const timeInProcess = useMemo(
        () => currentTime - workStartTimeEpochMs,
        [ currentTime, workStartTimeEpochMs ]
    );
    
    const targetDate = useMemo(
        () => new Date((workStartTimeEpochMs || Date.now()) + workMaxDurationMs - (new Date().getTimezoneOffset() * 60000)).toISOString().slice(0, -8),
        [ workMaxDurationMs, workStartTimeEpochMs ]
    );

    const timeRemaining = useMemo(
        () => durationSecondsAsString(Math.max((workMaxDurationMs - timeInProcess) / 1000, 0)),
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

    const handleClose = () => {
        setIsVisible(false);
    };

    useEffect(() => {
        dispatch(loadUserProfile({}));
    }, []);

    const getVariant = () => { 
        if (workActive) {
            const backwardsSupport = backwardsSupportParseFromDescription(work.description, work.title, profile);
            return {
                type: 'Secondary',
                repositoryUrl: work.repoUrl || backwardsSupport.url,
                repositoryName: work.repoName || backwardsSupport.name,
                branchName: work.branchName || backwardsSupport.branch,
                context: work.context
            };
        }  
        return {
            type: 'Primary',
            workType: work.taskType || 'missing',
            skillsNeeded: work.skills,
            context: work.context,
            onAccept: handleActivateWork,
            onSkip: handleSkipWork
        };
    };

    const getPrimaryText = () => {
        if (currentStep === ContributorWorkSteps.AnalyzePullRequest) {
            return activeWorkRecord?.latestBeehaveReview ? 'Analyze Again' : 'Analyze';
        } 
        if (currentStep === ContributorWorkSteps.Done) {
            return 'Next Work';
        } 
        return '';
        
    };

    const getPrimaryDisabled = () => {
        if (workLoading) {
            return true;
        }
        if (currentStep === ContributorWorkSteps.AnalyzePullRequest) {
            return !solutionUrl;
        }
        if (currentStep === ContributorWorkSteps.DescriptionFeedback) {
            if (feedbackAdded) {
                return false;
            }
            return true;
        }
        return false;
    };

    const getSecondaryDisabled = () => {
        if (workLoading) {
            return true;
        }
        if (currentStep === ContributorWorkSteps.AnalyzePullRequest) {
            return !iReadChecked || !solutionUrl || (!activeWorkRecord?.latestBeehaveReview && !didRunBeehave);
        }
        return false;
    };

    const getSecondaryText = () => {
        if (currentStep === ContributorWorkSteps.AnalyzePullRequest || currentStep === ContributorWorkSteps.SubmitPullRequest) {
            return 'Submit';
        }
        return '';
    };
    
    const handlePrimaryClick = () => {
        if (currentStep === ContributorWorkSteps.AnalyzePullRequest) {
            handleAnalyzeUrlSolution();
        }
        if (currentStep === ContributorWorkSteps.Done) {
            dispatch(loadAvailableWork({ currentWorkId: work.id }));
            setCurrentStep(ContributorWorkSteps.TaskAccept);
        }
    };

    const handleSecondaryClick = () => {
        if (currentStep === ContributorWorkSteps.AnalyzePullRequest) {
            onSubmitClicked();
        }
    };
    
    const handleSelectWorkTypeSubmit = (workType: string, otherReason?: string) => {
        console.log(workType, otherReason);
        handleClose();
    };

    const _calculateDurationSeconds = () => {
        return Math.round((Date.now() - workStartTimeEpochMs) / 1000);
    };

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

    const handleSubmitWorkFeedback = useCallback(
        (feedback: string) => {
            dispatch(
                submitWorkFeedback({
                    workId: work.id,
                    feedback,
                    durationSeconds: _calculateDurationSeconds()
                })
            ).unwrap().then(() => {
                setFeedbackDialogOpen(false);
                dispatch(loadAvailableWork({ currentWorkId: work.id }));
            });
            
        },
        [ dispatch, submitWorkFeedback, work, _calculateDurationSeconds ]
    );

    const handleAnalyzeUrlSolution = useCallback(
        () => {
            dispatch(
                analyzeWorkSolution({
                    workId: work.id,
                    solutionUrl
                })
            ).unwrap().then(() => {
                setDidRunBeehave(true);
            }).catch(() => {
                setDidRunBeehave(true);
            });

        },
        [ solutionUrl, analyzeWorkSolution, dispatch, work, setDidRunBeehave ]
    );

    const handleSkipWork = useCallback(
        () => {
            const startTimeEpochMs = Date.now();
            const tzName = Intl.DateTimeFormat().resolvedOptions().timeZone;

            dispatch(skipWork({
                workId: work.id,
                startTimeEpochMs, 
                tzName 
            })).unwrap().then(() => {
                dispatch(loadAvailableWork({ currentWorkId: work.id }));
                setFeedbackAdded(false);
            });
        },
        [ dispatch, loadAvailableWork, work ]
    );

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
            ).unwrap().then((result) => {
                if (!result['error']) {
                    setCurrentStep(ContributorWorkSteps.AnalyzePullRequest);
                }
            });
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
            ).then(() => {
                // cancel work without waiting for checkpoint to be done
                dispatch(
                    cancelWork({
                        workId: work.id,
                        durationSeconds
                    })
                ).unwrap().then(() => {
                    setCancellationDialogOpen(false);
                    setFeedbackAdded(false);
                    setSolutionUrl('');
                    setCurrentStep(ContributorWorkSteps.TaskAccept);
                });
            });
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
        ).unwrap().then(() => {
            setCurrentStep(ContributorWorkSteps.Done);
            setSolutionUrl('');
            setFeedbackAdded(false);
        });
    };

    const onSubmitClicked = useCallback(
        () => {
            _handleSubmitWorkSolution(undefined, undefined, solutionUrl);
        },
        [ _handleSubmitWorkSolution, solutionUrl ]
    );
    
    return (
        <BG>
            <Container>
                {currentStep === ContributorWorkSteps.Done && <TaskCompleted />}
                {(currentStep !== ContributorWorkSteps.Done) && (
                    <>
                        <Header currentStep={currentStep} key={currentIndex} name={work.title} questionsOnClick={() => !workLoading && setFeedbackDialogOpen(true)} workInProgressOnClick={() => !workLoading && setCancellationDialogOpen(true)}/>
                        <>
                            <Box height={15} />
                        </>
                        <DescriptionTermsContainer>
                            {
                                <DescriptionWrapper>
                                    <Description
                                        key={currentIndex}
                                        content={work.description}
                                        currentStep={currentStep}
                                    />
                                    { (currentStep === ContributorWorkSteps.AnalyzePullRequest) && (
                                        <AddPullRequest 
                                            onSubmit={(url => {
                                                setSolutionUrl(url);
                                            })}
                                        /> 
                                    )}    
                                </DescriptionWrapper>
                            }
                            <Terms
                                priority={work.priority > 3 ? 'Urgent' : work.priority === 3 ? 'High' : work.priority === 2 ? 'Medium' : 'Low'}
                                datetime={`${targetDate} ${currentStep !== ContributorWorkSteps.TaskAccept ? timeRemaining : ''}`.replace('T', ' ')}
                                amount={null}
                                variant={getVariant()}
                                currentStep={currentStep}
                            />
                        </DescriptionTermsContainer>
                        <Box height={15} />
                        { currentStep === ContributorWorkSteps.AnalyzePullRequest && activeWorkRecord?.latestBeehaveReview && (
                            <>
                                <Box height={15} />
                                <CodeReview reviews={{ ...activeWorkRecord?.latestBeehaveReview }} />
                                <Box height={15} />
                            </>
                        )}
                    </>
                )}
                <Box height={15} />
                {(currentStep !== ContributorWorkSteps.TaskAccept) && (
                    <FooterButtons 
                        onClickPrimary={() => handlePrimaryClick()}
                        primaryButton={getPrimaryText()}
                        onClickSecondary={() => handleSecondaryClick()}
                        primaryDisabled={getPrimaryDisabled()}
                        secondaryButton={getSecondaryText()}
                        secondaryDisabled={getSecondaryDisabled()}
                        iReadChecked={iReadChecked}
                        setIReadChecked={setIreadChecked}
                        didBeehave={!!activeWorkRecord?.latestBeehaveReview || didRunBeehave}
                    />
                )}
                <SelectModal
                    isVisible={isVisible}
                    onSave={handleSelectWorkTypeSubmit}
                    onCancel={handleClose}
                    options={options}
                />
                <Dialogs 
                    taskId={''} 
                    feedbackDialogOpen={feedbackDialogOpen} 
                    cancellationDialogOpen={cancellationDialogOpen} 
                    onSubmitFeedback={handleSubmitWorkFeedback} 
                    onConfirmCancel={handleCancelWork} 
                    onCloseFeedbackDialog={() => setFeedbackDialogOpen(false)}
                    onCloseCancellationDialog={() => setCancellationDialogOpen(false)}
                ></Dialogs>
                {workActionError && (
                    <Snackbar
                        open={!!workActionError}
                        autoHideDuration={6000}
                        onClose={() => dispatch(clearWorkActionError())}
                        message={formatErrorMessage(workActionError)}
                    />
                )}
            </Container>
        </BG>
    );
};

export default ContributorWork;
