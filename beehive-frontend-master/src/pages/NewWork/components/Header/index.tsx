import { Box, Typography } from '@material-ui/core';
import { Button } from '@mui/material';
import { FunctionComponent } from 'react';

import { ContributorWorkSteps } from '../../../../types/contributorWork';
import { useStyles } from './styled';

export type Props = {
    name?: string;
    workInProgressOnClick?: () => void;
    questionsOnClick?: () => void;
    currentStep: ContributorWorkSteps;
};

const Header: FunctionComponent<Props> = ({
    name,
    workInProgressOnClick,
    questionsOnClick,
    currentStep
}: Props) => {
    const classes = useStyles();

    return (
        <Box className={classes.root}>
            <Box className={classes.titleContainer}>
                <Typography className={classes.title}>{name}</Typography>
                { (currentStep === ContributorWorkSteps.AnalyzePullRequest) && (
                    <Button
                        className="work-in-progress-btn"
                        onClick={workInProgressOnClick}
                    >
                        <img src="clock.svg" />
                        <Typography className={classes.workInProgressText}>
                            Work in progress
                        </Typography>
                        <Typography className={classes.cancelText}>Cancel</Typography>
                    </Button>
                )}
            </Box>
            { currentStep === ContributorWorkSteps.AnalyzePullRequest && 
                <Button className="questions-btn" onClick={questionsOnClick}>
                    <img src="chat.svg" />
                    <Typography className={classes.questionsText}>
                        Questions about this work?
                    </Typography>
                </Button>
            }
        </Box>
    );
};

export default Header;
