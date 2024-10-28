import { Fade, IconButton, Tooltip } from '@material-ui/core';
import AssignmentIcon from '@material-ui/icons/Assignment';
import AssignmentTurnedInIcon from '@material-ui/icons/AssignmentTurnedIn';
import React, { FunctionComponent, ReactElement, useState } from 'react';

type Props = {
    text: string;
    visible?: boolean;
    copyIcon?: ReactElement;
    copiedIcon?: ReactElement;
    copyTooltip?: string;
    copiedTooltip?: string;
};

const CopyButton: FunctionComponent<Props> = ({
    text,
    visible=true,
    copyIcon=<AssignmentIcon />,
    copiedIcon=<AssignmentTurnedInIcon />,
    copyTooltip='Copy to clipboard',
    copiedTooltip='Copied!'
}: Props) => {
    const [ copied, setCopied ] = useState(false);

    const handleClick = (e: React.MouseEvent) => {
        e.preventDefault();

        // copy text to clipboard
        navigator.clipboard.writeText(text).then(() => {
            setCopied(true);

            setTimeout(() => {
                setCopied(false);
            }, 2000);
        }, (err) => {
            console.error('failed to copy param: ', err);
        });
    };

    return (
        <>
            {visible && (
                <Tooltip
                    title={copied ? copiedTooltip : copyTooltip}
                    TransitionComponent={Fade}
                >
                    <IconButton onClick={handleClick} color="inherit">
                        {copied ? (
                            copiedIcon
                        ) : (
                            copyIcon
                        )}
                    </IconButton>
                </Tooltip>
            )}
        </>
    );
};

export default CopyButton;
