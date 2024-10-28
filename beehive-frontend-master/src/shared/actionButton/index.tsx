import { Button } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import clsx from 'clsx';
import { FunctionComponent, ReactElement } from 'react';

const useStyles = makeStyles((theme) => ({
    root: {
        paddingLeft: theme.spacing(1)
    },
    button: {
        borderRadius: theme.spacing(1),
        width: '100%',
        fontWeight: 'bold',
        textTransform: 'none',
        color: `${theme.palette.text.primary} !important`
    },
    disabledButton: {
        color: 'rgba(255, 255, 255, 0.4) !important'
    }
}));

type Props = {
    className?: string;
    buttonClassName?: string;
    text: string;
    disabled?: boolean;
    icon?: ReactElement;
    onClick?: () => void;
    size?: 'medium' | 'large' | 'small';
    color?: 'primary' | 'secondary' | 'inherit';
    variant?: 'text' | 'outlined' | 'contained';
};

const ActionButton: FunctionComponent<Props> = ({
    className,
    buttonClassName,
    text,
    disabled,
    icon,
    onClick,
    size,
    color='primary',
    variant='contained'
}: Props) => {
    const classes = useStyles();

    return (
        <div className={clsx(classes.root, className)}>
            <Button
                className={clsx(classes.button, buttonClassName)}
                variant={variant}
                color={color}
                disabled={disabled}
                onClick={onClick}
                startIcon={icon}
                size={size}
                classes={{
                    disabled: classes.disabledButton
                }}
            >
                {text}
            </Button>
        </div>
    );
};

export default ActionButton;
