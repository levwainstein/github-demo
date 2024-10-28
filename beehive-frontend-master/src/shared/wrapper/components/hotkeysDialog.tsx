import { Dialog, DialogContent, DialogContentText, DialogTitle } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { FunctionComponent } from 'react';

const useStyles = makeStyles(theme => ({
    title: {
        color: theme.palette.text.secondary
    }
}));

type Props = {
    dialogOpen: boolean;
    onDialogClose: () => void;
};

const HotkeysDialog: FunctionComponent<Props> = ({ dialogOpen, onDialogClose }: Props) => {
    const classes = useStyles();

    return (
        <Dialog
            open={dialogOpen}
            aria-labelledby="form-dialog-title"
            onClose={onDialogClose}
        >
            <DialogTitle id="form-dialog-title" className={classes.title}>
                Beehive Keyboard Shortcuts
            </DialogTitle>
            <DialogContent>
                <DialogContentText>
                    <b><i>Ctrl + S</i></b> - skip work or refresh when no work is currently available
                </DialogContentText>
                <DialogContentText>
                    <b><i>Ctrl + E</i></b> - accept work
                </DialogContentText>
                <DialogContentText>
                    <b><i>Ctrl + Y</i></b> - cancel active work
                </DialogContentText>
            </DialogContent>
        </Dialog>
    );
};

export default HotkeysDialog;
