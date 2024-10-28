import { Avatar, Box, Checkbox, Link, TextField, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import {
    CheckBox as CheckBoxIcon,
    CheckBoxOutlineBlank as CheckBoxOutlineBlankIcon
} from '@material-ui/icons';
import { Done as DoneIcon } from '@material-ui/icons';
import { FunctionComponent, useCallback, useEffect, useState } from 'react';

import { setWorkRatings, WorkSelectors } from '../../../../reducers/work';
import { ActionButton, Rating } from '../../../../shared';
import { isRatingsCompleted } from '../../../../types/rating';
import Github from './icons/github.png';
import Vector from './icons/Vector.png';

const useStyles = makeStyles(theme => {
    return {
        root: {
            overflow: 'hidden',
            padding: 0,
            backgroundColor: theme.palette.primary.dark,
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center'
        },
        boxCard: {
            background: '#232530',
            border: '1px solid #31333E',
            borderRadius: '5px',
            width: '100%',
            maxWidth: '399px',
            display: 'flex',
            flexDirection: 'row',
            justifyContent: 'center',
            marginLeft: 'auto',
            marginRight: 'auto',
            color: theme.palette.text.primary,
            overflowY: 'scroll'
        },
        innerContainer: {
            width: '100%',
            padding: theme.spacing(1)
        },
        title: {
            textAlign: 'center',
            marginBottom: theme.spacing(1)
        },
        githubIcon: {
            display: 'flex',
            flexDirection: 'row',
            justifyContent: 'center',
            marginLeft: 'auto',
            marginRight: 'auto',
            cursor: 'pointer'
        },
        icons: {
            marginRight: theme.spacing(1)
        },
        searchTextField: {
            // these can't be set as InputProps.classes because that breaks the AutoComplete component
            '& .MuiInputBase-input': {
                backgroundColor: theme.palette.primary.main,
                borderRadius: '8px',
                color: '#C7C7C7',
                width: '100%'
            },
            '& .MuiOutlinedInput-notchedOutline': {
                borderRadius: '8px'
            },
            '& .MuiIconButton-root': {
                color: '#C7C7C7'
            },
            '& .MuiOutlinedInput-root': {
                width: '98%',
                margin: '0 auto'
            },
            '& .MuiFormHelperText-root': {
                color: 'red'
            }
        },
        searchTextFieldLabel: {
            display: 'inherit',
            color: '#C7C7C7 !important',
            letterSpacing: '-0.04em',
            fontSize: '12px',
            fontStyle: 'italic'
        },
        borderRotate: {
            border: '1px solid #414451',
            height: '20px'
        },
        urlHere: {
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            margin: '-10px 0px 0px 0px'
        },
        buttonsContainer: {
            marginTop: '10px'
        },
        buttonsBox: {
            width: '100%',
            display: 'flex',
            flexDirection: 'row',
            justifyContent: 'space-around',
            margin: '0px 25px 0px 0px'
        },
        buttonsBoxWithCheckbox: {
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-around',
            margin: '0px 25px 0px 0px'
        },
        button: {
            flexGrow: 1,
            maxWidth: '100px'
        },
        checkBox: {
            flexGrow: 1,
            margin: '10px 0px 0px 0px'
        },
        link: {
            color: '#E6BB42'
        }
    };
});

type Props = {
    workActive: boolean;
    workDone: boolean;
    workLoading: boolean;
    handleSubmitUrlSolution: (url: string) => void;
    handleSubmitSolutionReview: () => void;
    handleCancelWork: () => void;
    handleNextWorkClick: () => void;
    requirePRUrl?: boolean;
    handleAnalyzeUrlSolution: (url: string) => void;
    submitConditionsFulfilled: boolean;
};

const External: FunctionComponent<Props> = ({
    workActive,
    workDone,
    workLoading,
    handleSubmitUrlSolution,
    handleSubmitSolutionReview,
    handleCancelWork,
    handleNextWorkClick,
    handleAnalyzeUrlSolution,
    submitConditionsFulfilled,
    requirePRUrl=true
}: Props) => {
    const classes = useStyles();

    const [ solutionUrl, setSolutionUrl ] = useState<string>('');
    const [ submitErrorMessage, setSubmitErrorMessage ] = useState<string>('');
    const { workRatings } = WorkSelectors();
    const [ workRatingSubmitted, setWorkRatingSubmitted ] = useState<boolean>(false);
    const [ didReadBeehave, setDidReadBeehave ] = useState<boolean>(false);

    const onSubmitClicked = useCallback(
        () => {
            if (solutionUrl.trim()) {
                handleSubmitUrlSolution(solutionUrl);
            } else {
                handleSubmitSolutionReview();
            }

            setWorkRatingSubmitted(true);
        },
        [ handleSubmitUrlSolution, handleSubmitSolutionReview, solutionUrl ]
    );

    const onCancelClicked = useCallback(
        () => {
            setSolutionUrl('');
            handleCancelWork();
        },
        [ handleCancelWork ]
    );

    const onNextWorkClicked = useCallback(
        () => {
            setSolutionUrl('');
            handleNextWorkClick();
        },
        [ handleNextWorkClick ]
    );

    const onAnalyzeClicked = useCallback(
        () => {
            if (solutionUrl.trim()) {
                handleAnalyzeUrlSolution(solutionUrl);
            }
        },
        [ handleAnalyzeUrlSolution, solutionUrl ]
    );

    useEffect(
        () => {
            setWorkRatingSubmitted(
                isRatingsCompleted(workRatings)
            );

            if (!solutionUrl) {
                return;
            }

            const isUrlValid = solutionUrl.toLocaleLowerCase().match(/^https:\/\/(www\.)?github.com\/.*\/.*\/pull\/[0-9]*\/?$/);

            if (!isUrlValid) {
                setSubmitErrorMessage('format should be: https://[www.]github.com/<org-name>/<repo>/pull/<pull-request-number>');
            } else {
                setSubmitErrorMessage('');
            }
        },
        [ setWorkRatingSubmitted, isRatingsCompleted, workRatings, solutionUrl, setSubmitErrorMessage ]
    );
    
    return (
        <Box className={classes.root}>
            <Box className={classes.boxCard}>
                <Box className={classes.innerContainer}>
                    {requirePRUrl && !workDone && (
                        <>
                            <Avatar src={Github} className={classes.githubIcon}/>
                            <Typography className={classes.title}>
                                Pull Request (PR) URL
                            </Typography>
                            <Typography className={classes.title}>
                                Please make sure to follow our&nbsp;
                                <Link
                                    className={classes.link}
                                    href="https://docs.caas.ai/community/working_with_github"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    coding and GitHub standards
                                </Link>
                                , otherwise your work will be rejected. In&nbsp;
                                particular, only use your designated branch, do&nbsp;
                                not merge code yourself, and always do PR changes&nbsp;
                                requests on the same branch.
                            </Typography>
                            <TextField
                                id="outlined-basic"
                                className={classes.searchTextField}
                                variant="outlined"
                                margin="dense"
                                helperText={submitErrorMessage}
                                fullWidth
                                label={
                                    <div className={classes.urlHere}>
                                        <img src={Vector} className={classes.icons} />
                                        <div className={classes.borderRotate} />
                                        URL here
                                    </div>
                                }
                                InputLabelProps={{
                                    className: classes.searchTextFieldLabel
                                }}
                                disabled={!workActive}
                                onChange={e => {
                                    setSolutionUrl(e.target.value);
                                    //validateSolutionUrl(e.target.value);
                                }}
                                value={solutionUrl}
                            />
                        </>
                    )}
                    <Box className={classes.buttonsContainer}>
                        <Box className={classes.buttonsBox}>
                            {workDone ? (
                                <div>
                                    <Rating 
                                        ratings={workRatings}
                                        setRatings={setWorkRatings}
                                        showTitle 
                                    />
                                    <ActionButton
                                        text="Next task"
                                        disabled={!workRatingSubmitted}
                                        icon={<DoneIcon />}
                                        onClick={onNextWorkClicked}
                                    />
                                </div>
                            ) : 
                                (
                                    <div className={classes.buttonsBoxWithCheckbox}>
                                        <div className={classes.buttonsBox}>
                                            <ActionButton
                                                className={classes.button}
                                                text="Cancel"
                                                disabled={!workActive || workLoading}
                                                onClick={onCancelClicked}
                                            />
                                            <ActionButton
                                                className={classes.button}
                                                text="Analyze"
                                                color="secondary"
                                                disabled={!workActive || !solutionUrl || workLoading || submitErrorMessage !== '' || !requirePRUrl}
                                                onClick={onAnalyzeClicked}
                                            />
                                            <ActionButton
                                                className={classes.button}
                                                text="Submit"
                                                color="secondary"
                                                disabled={!workActive || (requirePRUrl && !solutionUrl) || submitErrorMessage !== '' || !submitConditionsFulfilled || (requirePRUrl && !didReadBeehave)}
                                                onClick={onSubmitClicked}
                                            />
                                        </div>
                                        {submitConditionsFulfilled && requirePRUrl && 
                                            <Box className={classes.checkBox}>
                                                <Checkbox
                                                    icon={<CheckBoxOutlineBlankIcon fontSize="small" />}
                                                    checkedIcon={<CheckBoxIcon fontSize="small" />}
                                                    style={{ marginRight: 8 }}
                                                    checked={didReadBeehave}
                                                    onChange={x => setDidReadBeehave(x.target.checked)}
                                                />
                                                {'I read the Automatic PR Feedback below and wish to submit the PR'}
                                            </Box>
                                        }
                                    </div>
                                )
                            }
                        </Box>
                    </Box>
                </Box>
            </Box>
        </Box>
    );
};

export default External;
