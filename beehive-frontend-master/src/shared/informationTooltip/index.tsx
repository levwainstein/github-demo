import { FunctionComponent, ReactElement } from 'react';

import { TooltipStyled } from './styled';

export type Props = {
    text: string | ReactElement;
    children: ReactElement;
};

const InformationTooltip: FunctionComponent<Props> = ({
    text,
    children
}: Props) => {

    return (
        <TooltipStyled title={text} arrow>
            {children}
        </TooltipStyled>
    );
};

export default InformationTooltip;
