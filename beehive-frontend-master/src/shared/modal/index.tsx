import CloseIcon from '@material-ui/icons/Close';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import IconButton from '@mui/material/IconButton';
import { FunctionComponent } from 'react';

import S from './styles';

export interface Props {
    open?: boolean;
    title?: string;
    children: React.ReactNode;
    onClose?: () => void;
    dialogStyle?: any;
    minHeight?: boolean;
    hasCrossIcon: boolean;
}

const Modal: FunctionComponent<Props> = ({
    open = false,
    title,
    children,
    onClose,
    dialogStyle,
    hasCrossIcon = true
}: Props) => (
    <Dialog
        open={open}
        onClose={onClose}
        sx={{ ...dialogStyle }}
        PaperProps={{
            sx: S.dialogPaperPropsSX
        }}
        fullWidth
    >
        {title && (
            <DialogTitle sx={S.modalTitle}>
                {title}
                {hasCrossIcon && (
                    <IconButton aria-label="close" onClick={onClose}>
                        <CloseIcon />
                    </IconButton>
                )}
            </DialogTitle>
        )}

        <DialogContent sx={S.modalContent}>{children}</DialogContent>
    </Dialog>
);

export default Modal;
