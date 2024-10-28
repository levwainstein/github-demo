import { Button, Dialog, DialogActions, DialogContent } from '@material-ui/core';
import { DialogContentText, DialogTitle, FormControlLabel, FormLabel } from '@material-ui/core';
import { Box, Radio, RadioGroup, Snackbar, TextField, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import ReportIcon from '@material-ui/icons/Report';
import { FunctionComponent, useEffect, useState } from 'react';

import { useAppDispatch, useNoDefaultHotkeys } from '../../../../hooks';
import {
    clearReportBugError,
    clearReportBugSuccess,
    GeneralSelectors,
    sendBugReport
} from '../../../../reducers/general';
import { ActionButton } from '../../../../shared';

const useStyles = makeStyles((theme) => ({
    root: {
        width: 'calc(100% - 10px)',
        flexDirection: 'column',
        display: 'flex',
        justifyContent: 'center'
    },
    row: {
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'center'
    },
    questionsButton: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        color: 'white'
    },
    buttonsContainer: {
        width: '100%',
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'space-between'
    },
    button: {
        flexGrow: 1
    },
    feedbackDialogTitle: {
        color: theme.palette.text.secondary
    },
    feedbackDialogRadio: {
        color: theme.palette.text.secondary
    },
    feedbackDialogInput: {
        color: theme.palette.text.secondary
    },
    cancellationDialog: {
        width: '100%',
        height: '140px',
        flexDirection: 'column',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingBottom: '30px',
        paddingTop: '30px',
        backgroundColor: theme.palette.background.default
    },
    cancellationDialogButtonsContainer: {
        width: '70%',
        height: '30%',
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'space-between'
    },
    cancellationDialogText: {
        width: '85%',
        textAlign: 'center'
    },
    confirmCancelbutton: {
        flexGrow: 1,
        maxWidth: '170px'
    }
}));

type Props = {
    taskId: string;
    workActive: boolean;
    workLoading: boolean;
    onAcceptClick: () => void;
    onSkipClick: () => void;
    onSubmitFeedback: (feedback: string) => void;
    onCancelClick: () => void;
};

const Actions: FunctionComponent<Props> = ({
    taskId,
    workActive,
    workLoading,
    onAcceptClick,
    onSkipClick,
    onSubmitFeedback,
    onCancelClick,
    ...other
}: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();

    const [ reportDialogOpen, setReportDialogOpen ] = useState(false);
    const [ cancellationDialogOpen, setCancellationDialogOpen ] = useState(false);
    const [ feedback, setFeedback ] = useState('');
    const [ reportType, setReportType ] = useState('');
    const { isReportBugError, isReportBugSuccess } = GeneralSelectors();

    useNoDefaultHotkeys('ctrl + e', () => {
        if (!workActive) {
            onAcceptClick();
        }
    });
    useNoDefaultHotkeys('ctrl + s', () => {
        if (!workActive) {
            onSkipClick();
        }
    });

    const openReportDialog = () => {
        // if the work item has not been activated yet do so now
        if (!workActive) {
            onAcceptClick();
        }

        setReportDialogOpen(true);
    };

    const closeReportDialog = () => {
        setReportDialogOpen(false);
        setFeedback('');
    };

    const onSubmitFeedbackClick = () => {
        if (feedback.trim() && reportType) {
            if (reportType === 'task') {
                onSubmitFeedback(feedback);
            } else if (reportType === 'general') {
                dispatch(sendBugReport({ taskId, details: feedback }));
            }

            closeReportDialog();
        }
    };

    const onConfirmCancellationCLick = () => {
        setCancellationDialogOpen(false);
        onCancelClick();
    };

    const handleRadioChange = (e) => {
        setReportType(e.target.value);
    };

    useEffect(() => {
        if (isReportBugSuccess && reportDialogOpen) {
            closeReportDialog();
        }
    }, [ isReportBugSuccess, reportDialogOpen ]);

    return (
        <div
            className={classes.root}
            {...other}
        >
            <div className={classes.row}>
                {!workActive && (
                    <Box className={classes.buttonsContainer}>
                        <ActionButton
                            className={classes.button}
                            text="Skip"
                            disabled={workLoading}
                            onClick={onSkipClick}
                        />
                        <ActionButton
                            className={classes.button}
                            text="Accept"
                            disabled={workLoading}
                            onClick={onAcceptClick}
                            color="secondary"
                        />
                    </Box>
                )}
            </div>

            <div className={classes.questionsButton}>
                <ActionButton
                    text="Questions or issues?"
                    icon={<ReportIcon />}
                    onClick={openReportDialog}
                    size="small"
                    variant="text"
                    color="inherit"
                />
            </div>

            {/* report dialog */}
            <Dialog
                open={reportDialogOpen}
                onClose={closeReportDialog}
                aria-labelledby="form-dialog-title"
            >
                <DialogTitle id="form-dialog-title" className={classes.feedbackDialogTitle}>
                    Feedback
                </DialogTitle>
                <DialogContent>
                    <FormLabel component="legend">
                        What is your feedback or question about?
                    </FormLabel>
                    <RadioGroup
                        aria-label="reportType"
                        name="reportType"
                        value={reportType}
                        onChange={handleRadioChange}
                    >
                        <FormControlLabel
                            className={classes.feedbackDialogRadio}
                            value="task"
                            control={<Radio />}
                            label="This specific task"
                        />
                        <FormControlLabel
                            className={classes.feedbackDialogRadio}
                            value="general"
                            control={<Radio />}
                            label="The general platform"
                        />
                    </RadioGroup>
                    <DialogContentText>
                        Please be as detailed as you can about your feedback or question.
                        We appreciate your help!
                    </DialogContentText>
                    <TextField
                        autoFocus
                        margin="dense"
                        id="name"
                        label="Description"
                        type="description"
                        fullWidth
                        multiline
                        rowsMax={8}
                        helperText={reportType === 'task' ? 'After sending your feedback/question, the task will not be available until your feedback is addressed.' : ''}
                        onChange={e => setFeedback(e.target.value)}
                        InputProps={{
                            classes: {
                                root: classes.feedbackDialogInput
                            }
                        }}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={closeReportDialog} color="secondary">
                        Cancel
                    </Button>
                    <Button onClick={onSubmitFeedbackClick} color="secondary">
                        Send
                    </Button>
                </DialogActions>
            </Dialog>

            {/* cancellation dialog */}
            <Dialog
                open={cancellationDialogOpen}
                onClose={() => setCancellationDialogOpen(false)}
                aria-labelledby="form-dialog-title"
            >
                <div className={classes.cancellationDialog}>
                    <Box className={classes.cancellationDialogButtonsContainer}>
                        <ActionButton
                            className={classes.confirmCancelbutton}
                            text="Don't Cancel" 
                            onClick={() => setCancellationDialogOpen(false)}
                        />
                        <ActionButton
                            className={classes.confirmCancelbutton}
                            text="Cancel"
                            onClick={onConfirmCancellationCLick}
                            color="secondary"
                        />
                    </Box>
                    <Typography className={classes.cancellationDialogText} variant="subtitle1" component="h1">
                        Are you sure you want to cancel the task?
                    </Typography>
                    <Typography className={classes.cancellationDialogText} variant="subtitle2" component="h1">
                        If you made any progress on this task, please push your changes before canceling the task.
                    </Typography>
                </div>
            </Dialog>

            <Snackbar
                open={isReportBugError}
                autoHideDuration={4000}
                onClose={() => dispatch(clearReportBugError())}
                message="Woops! Not sure what happened there... Please try again"
            />
            <Snackbar
                open={isReportBugSuccess}
                autoHideDuration={4000}
                onClose={() => dispatch(clearReportBugSuccess())}
                message="Thank you for the help! We try to improve and this will definitely help us"
            />
        </div>
    );
};

export default Actions;
