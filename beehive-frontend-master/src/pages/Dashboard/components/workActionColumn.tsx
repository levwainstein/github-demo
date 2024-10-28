import { Fade, IconButton, InputAdornment, TextField, Tooltip, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import AssignmentIndIcon from '@material-ui/icons/AssignmentInd';
import AssignmentLateIcon from '@material-ui/icons/AssignmentLate';
import AssignmentTurnedInIcon from '@material-ui/icons/AssignmentTurnedIn';
import CancelIcon from '@material-ui/icons/Cancel';
import DoneIcon from '@material-ui/icons/Done';
import ErrorIcon from '@material-ui/icons/Error';
import { AsyncThunk } from '@reduxjs/toolkit';
import { FunctionComponent, useCallback, useState } from 'react';

import { useAppDispatch } from '../../../hooks';

const useStyles = makeStyles(theme => {
    return {
        inputTextField: {
            '& .MuiInputBase-input': {
                borderRadius: '8px',
                width: '100px',
                [theme.breakpoints.down('sm')]: {
                    width: '80px'
                }
            },
            '& .MuiOutlinedInput-notchedOutline': {
                borderRadius: '8px'
            },
            '& .MuiIconButton-root': {
                color: '#C7C7C7'
            },
            '& .MuiInputBase-root': {
                color: 'black'
            }
        },
        inputTextFieldLabel: {
            display: 'inherit',
            letterSpacing: '-0.04em',
            fontSize: '12px',
            fontStyle: 'italic'
        },
        errorAlert: {
            color: 'red'
        },
        valueTextField: {
            display: 'flex',
            alignItems: 'center'
        },
        cancelIcon: {
            verticalAlign: 'bottom'
        }
    };
});

type Props = {
    row: any;
    value?: string;
    onSubmitFunc: AsyncThunk<any, {workId: number, userId: string}, Record<string, unknown>>;
    onCancelFunc: AsyncThunk<any, {workId: number, userId: string}, Record<string, unknown>>;
    visible?: boolean;
    disableInput?: boolean;
};

const WorkActionColumn: FunctionComponent<Props> = ({
    row,
    value,
    onSubmitFunc,
    onCancelFunc,
    visible=true,
    disableInput=false
}: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();

    const [ submitted, setSubmitted ] = useState(false);
    const [ cancelled, setCancelled ] = useState(false);
    const [ isError, setIsError ] = useState<boolean>(false);
    const [ errorMessage, setErrorMessage ] = useState<string>('');

    const [ inputText, setInputText ] = useState<string>('');
    const [ staticText, setStaticText ] = useState<string | undefined>(value);

    // work row has an id column
    const workId = row.id;

    const handleSubmitClicked = useCallback((event) => {
        event.preventDefault();
        if (inputText && inputText.trim()) {
            dispatch(onSubmitFunc({ workId, userId: inputText }))
                .unwrap()
                .then(() => {
                    setSubmitted(true);
                    setStaticText(inputText);
                    setIsError(false);
                    setErrorMessage('');
                })
                .catch((error) => {
                    setSubmitted(true);
                    setInputText('');
                    setStaticText('');                    
                    setIsError(true);
                    if (error.status === 404) {
                        setErrorMessage('User not found');
                    } else if (error.status === 400) {
                        setErrorMessage('Work is not in correct status');
                    } else {
                        setErrorMessage('Unknown error has occurred');
                    }
                });
        } else {
            setErrorMessage('Please input a valid user id');
        }
    }, [ onSubmitFunc, workId, inputText ]);

    const handleCancelClicked = useCallback((event) => {
        event.preventDefault();
        if (staticText && staticText.trim()) {
            dispatch(onCancelFunc({ workId, userId: staticText }))
                .unwrap()
                .then((_: any) => {
                    setCancelled(true);
                    setInputText('');
                    setStaticText('');
                    setIsError(false);
                    setErrorMessage('');
                })
                .catch((error) => {
                    setCancelled(true);
                    setStaticText(staticText);
                    setIsError(true);
                    if (error.status === 404) {
                        setErrorMessage('User not found');
                    } else if (error.status === 400) {
                        setErrorMessage('Work is not in correct status');
                    } else {
                        setErrorMessage('Unknown error has occurred');
                    }
                });
        } else {
            setErrorMessage('Please input a valid user id');
        }
    }, [ onCancelFunc, workId, staticText ]);

    return (
        <>
            {visible && !staticText && (
                <div>
                    {isError && <p className={classes.errorAlert}> {errorMessage} </p>}
                    <TextField
                        id="outlined-basic"
                        className={classes.inputTextField}
                        variant="outlined"
                        margin="dense"
                        fullWidth
                        label="Enter contributor id"
                        InputLabelProps={{
                            className: classes.inputTextFieldLabel
                        }}
                        disabled={disableInput || (submitted && !isError && !cancelled)}
                        onChange={e => setInputText(e.target.value)}
                        value={inputText}
                        InputProps={{
                            endAdornment: (
                                <InputAdornment position="end">
                                    <Tooltip
                                        title={submitted ? 
                                            isError ? 
                                                'Error occurred' : 
                                                'Submitted successfuly' : 
                                            'Submit'}
                                        TransitionComponent={Fade}
                                    >
                                        <IconButton type="submit" onClick={(e) => handleSubmitClicked(e)} color="inherit">
                                            {submitted ? 
                                                isError ? (
                                                    <AssignmentLateIcon color="primary" />
                                                ) : (
                                                    <AssignmentTurnedInIcon color="primary" />
                                                ) : (
                                                    <AssignmentIndIcon color="primary" />
                                                )}
                                        </IconButton>
                                    </Tooltip>
                                </InputAdornment>
                            )
                        }}                
                    />

                </div>
            )}
            {staticText && (
                <div>
                    {isError && <p className={classes.errorAlert}> {errorMessage} </p>}
                    <div className={classes.valueTextField}>
                        <Typography color="textSecondary">
                            {staticText}
                        </Typography>
                        <Tooltip
                            title={cancelled ? 
                                isError ? 
                                    'Error while dismissing' : 
                                    'Dismissed successfully' : 
                                'Dismiss work from contributor'}
                            TransitionComponent={Fade}
                        >
                            <IconButton type="submit" onClick={(e) => handleCancelClicked(e)} color="inherit" className={classes.cancelIcon}>
                                {cancelled ? 
                                    isError ? 
                                        <ErrorIcon color="primary" /> :
                                        <DoneIcon color="primary" /> :
                                    <CancelIcon color="primary" />
                                }
                            </IconButton>
                        </Tooltip>
                    </div>
                </div>
            )}

        </>
    );
};

export default WorkActionColumn;
