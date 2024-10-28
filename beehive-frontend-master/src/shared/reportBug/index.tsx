import { Backdrop, Button, Dialog, DialogActions, DialogContent } from '@material-ui/core';
import { DialogContentText, DialogTitle, Snackbar, TextField } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { BugReport as BugReportIcon, Help as HelpIcon } from '@material-ui/icons';
import { SpeedDial, SpeedDialAction } from '@material-ui/lab';
import React, { FunctionComponent, useEffect, useState } from 'react';

import { useAppDispatch } from '../../hooks';
import { clearReportBugError, clearReportBugSuccess, GeneralSelectors } from '../../reducers/general';
import { sendBugReport } from '../../reducers/general';
import { useViewport } from '../../utils/viewport';

const useStyles = makeStyles((theme) => ({
    button: {
        position: 'fixed',
        margin: '30vh 0 auto',
        top: 0,
        bottom: 0,
        transform: 'rotate(-90deg)',
        height: '35px',
        right: '-45px',
        boxShadow: 'none',
        textTransform: 'none',
        fontWeight: 500,
        zIndex: 999,
        '&:hover': {
            textTransform: 'none',
            boxShadow: 'none'
        },
        '&:active': {
            textTransform: 'none',
            boxShadow: 'none'
        },
        '&:focus': {
            textTransform: 'none',
            boxShadow: 'none'
        }
    },
    speedDial: {
        position: 'fixed',
        bottom: theme.spacing(2),
        right: theme.spacing(2)
    },
    backdrop: {
        zIndex: 999
    },
    dialogTitle: {
        color: theme.palette.text.secondary
    },
    textFieldInput: {
        color: theme.palette.text.secondary
    }
}));

const useTooltipStyles = makeStyles({
    staticTooltipLabel: {
        width: 'max-content'
    }
});

type Props = {
    taskId?: string;
};

const ReportBug: FunctionComponent<Props> = ({
    taskId
}: Props) => {
    const classes = useStyles();
    const tooltipClasses = useTooltipStyles();
    const dispatch = useAppDispatch();

    const [ speedDialOpen, setSpeedDialOpen ] = useState(false);
    const [ dialogOpen, setDialogOpen ] = useState(false);
    const [ details, setDetails ] = useState('');

    const { isTablet } = useViewport();

    const { isReportBugError, isReportBugSuccess } = GeneralSelectors();

    const handleOpenDialog = () => {
        // trick to remove focus from fab (in mobile view), since keeping
        // the focus means that when the dialog closes the fab menu will
        // re-open automatically
        document.documentElement.focus();

        clearReportBugError();
        clearReportBugSuccess();
        setSpeedDialOpen(false);
        setDialogOpen(true);
    };

    const handleCloseDialog = () => {
        setDialogOpen(false);
        setDetails('');
    };

    const handleOpenSpeedDial = () => {
        setSpeedDialOpen(true);
    };

    const handleCloseSpeedDial = () => {
        setSpeedDialOpen(false);
    };

    const handleSend = () => {
        if (details.trim()) {
            dispatch(sendBugReport({ taskId: taskId || '', details }));
        } else {
            handleCloseDialog();
        }
    };

    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setDetails(event.target.value);
    };

    useEffect(() => {
        if (isReportBugSuccess && dialogOpen) {
            handleCloseDialog();
        }
    }, [ isReportBugSuccess, dialogOpen ]);

    return (
        <>
            {isTablet ? (
                <Button
                    className={classes.button}
                    onClick={handleOpenDialog}
                    variant="contained"
                    color="primary"
                    disableElevation
                    disableFocusRipple
                    disableRipple
                >
                    Report a bug
                </Button>
            ) : (
                <>
                    <Backdrop
                        className={classes.backdrop}
                        open={speedDialOpen}
                    />
                    <SpeedDial
                        ariaLabel="Help"
                        className={classes.speedDial}
                        icon={<HelpIcon />}
                        onClose={handleCloseSpeedDial}
                        onOpen={handleOpenSpeedDial}
                        open={speedDialOpen}
                    >
                        <SpeedDialAction
                            key="speed-dial-report-bug"
                            icon={<BugReportIcon />}
                            tooltipTitle="Report a Bug"
                            tooltipOpen
                            classes={tooltipClasses}
                            onClick={handleOpenDialog}
                        />
                    </SpeedDial>
                </>
            )}

            <Dialog
                open={dialogOpen}
                disableBackdropClick
                aria-labelledby="report-bug-dialog-title"
            >
                <DialogTitle id="report-bug-dialog-title" className={classes.dialogTitle}>
                    Report a Bug
                </DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Please write as many details as possible about the bug you encountered.
                        We may contact you via the email address you registered with to update you about the bug.
                    </DialogContentText>
                    <TextField
                        autoFocus
                        margin="dense"
                        id="details"
                        label="Details"
                        type="text"
                        fullWidth
                        multiline
                        rows={3}
                        value={details}
                        onChange={handleChange}
                        InputProps={{
                            classes: {
                                root: classes.textFieldInput
                            }
                        }}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog} color="primary">
                        Cancel
                    </Button>
                    <Button onClick={handleSend} color="primary">
                        Send
                    </Button>
                </DialogActions>
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
        </>
    );
};

export default ReportBug;
