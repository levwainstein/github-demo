import { Button, Dialog, DialogActions, DialogContent, Tooltip } from '@material-ui/core';
import { DialogContentText, DialogTitle, MenuItem, Select, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import EditIcon from '@material-ui/icons/Edit';
import { FunctionComponent, useCallback, useState } from 'react';

import { TaskTypeClassification } from '../../../../types/task';

const useStyles = makeStyles((theme) => ({
    content: {
        display: 'flex',
        flexDirection: 'row'
    },
    suggestClassificationButton: {
        backgroundColor: theme.palette.text.secondary
    },
    dialogTitle: {
        color: theme.palette.text.secondary
    },
    selectTaskType: {
        color: theme.palette.text.secondary
    },
    taskTypeMenuItem: {
        color: theme.palette.text.secondary
    },
    textFieldInput: {
        color: theme.palette.text.secondary
    },
    descriptionTitle: {
        cursor: 'text',
        marginRight: theme.spacing(1)
    }
}));

type Props = {
    taskTypeClassification?: TaskTypeClassification;
    onSubmit: (predictedOutput: string, correctedOutput: string) => void;
    defaultTitle?: string;
};

const WorkTitle: FunctionComponent<Props> = ({
    taskTypeClassification, onSubmit, defaultTitle
}: Props) => {
    const classes = useStyles();

    const [ dialogOpen, setDialogOpen ] = useState(false);
    const [ suggestedClassification, setSuggestedClassification ] = useState<TaskTypeClassification | undefined>(taskTypeClassification);

    const openSuggestDialog = useCallback(
        () => {
            setDialogOpen(true);
        },
        [ setDialogOpen ]
    );

    const closeSuggestDialog = () => {
        setDialogOpen(false);
    };

    const onSubmitClick = () => {
        if (taskTypeClassification && suggestedClassification) {
            onSubmit(taskTypeClassification.toString(), suggestedClassification.toString());
            closeSuggestDialog();
        }
    };

    if (taskTypeClassification) {
        return (
            <div className={classes.content}>
                <Typography
                    className={classes.descriptionTitle}
                    variant="h6"
                    component="h1"
                >
                    { taskTypeClassification }
                </Typography>   
                <Tooltip title="Suggest a new task type">
                    <Button
                        color="secondary"
                        onClick={openSuggestDialog}
                        startIcon={<EditIcon />}
                    />
                </Tooltip>
                <Dialog
                    open={dialogOpen}
                    onClose={closeSuggestDialog}
                    aria-labelledby="form-dialog-title"
                    disableEnforceFocus
                >
                    <DialogTitle id="form-dialog-title" className={classes.dialogTitle}>
                        Help us improve!
                    </DialogTitle>
                    <DialogContent>
                        <DialogContentText>
                            Please choose the type you think is more suitable
                        </DialogContentText>
                        <Select
                            className={classes.selectTaskType}
                            value={suggestedClassification}
                            onChange={(e) => setSuggestedClassification(e.target.value as TaskTypeClassification)}
                            displayEmpty
                        >
                            {Object.entries(TaskTypeClassification).map(
                                ([ key, value ]) => {
                                    return <MenuItem className={classes.taskTypeMenuItem} value={value} key={key}>{value}</MenuItem>;
                                }
                            )}
                        </Select>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={closeSuggestDialog} color="secondary">
                            Cancel
                        </Button>
                        <Button
                            className={classes.suggestClassificationButton}
                            onClick={onSubmitClick}
                        >
                            Submit
                        </Button>
                    </DialogActions>
                </Dialog>

            </div>
        );
    } else {
        return (
            <Typography
                className={classes.descriptionTitle}
                variant="h6"
                component="h1"
            >
                { defaultTitle }
            </Typography>
        );
    }
};

export default WorkTitle;
