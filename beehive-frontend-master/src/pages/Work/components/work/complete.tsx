import { makeStyles } from '@material-ui/core/styles';
import DoneIcon from '@material-ui/icons/Done';
import { Alert } from '@material-ui/lab';
import { FunctionComponent } from 'react';

import { ActionButton } from '../../../../shared';

const useStyles = makeStyles((theme) => ({
    root: {
        padding: theme.spacing(0.5)
    },
    nextButton: {
        padding: theme.spacing(1),
        display: 'flex',
        justifyContent: 'center'
    }
}));

type Props = {
    packageRequest: boolean;
    workActive: boolean;
    onNextWorkClick: () => void;
};

const Complete: FunctionComponent<Props> = ({
    packageRequest,
    workActive,
    onNextWorkClick,
    ...other
}: Props) => {
    const classes = useStyles();

    return (
        <div
            className={classes.root}
            {...other}
        >
            {packageRequest ? (
                <Alert
                    variant="filled"
                    severity="info"
                >
                    Your package request was sent. The task will resume once the package is available.
                </Alert>
            ) : (
                <Alert
                    variant="filled"
                    severity="success"
                >
                    Your {workActive ? 'solution' : 'feedback'} was submitted successfully! {!workActive ? 'The task will resume once your feedback is addressed.' : ''}
                </Alert>
            )}
            <div className={classes.nextButton}>
                <ActionButton
                    text="Next task"
                    icon={<DoneIcon />}
                    onClick={onNextWorkClick}
                />
            </div>
        </div>
    );
};

export default Complete;
