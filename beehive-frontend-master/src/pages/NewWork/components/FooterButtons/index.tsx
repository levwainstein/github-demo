import { Checkbox } from '@material-ui/core';
import {
    CheckBox as CheckBoxIcon,
    CheckBoxOutlineBlank as CheckBoxOutlineBlankIcon
} from '@material-ui/icons';
import { FC } from 'react';

import { ButtonsContainer, ConfirmText, Container, FooterButton, FooterText } from './styled';

export type Props = {
  primaryButton: string;
  secondaryButton?: string;
  onClickPrimary: () => void;
  onClickSecondary?: () => void;
  primaryDisabled?: boolean;
  secondaryDisabled?: boolean;
  iReadChecked: boolean;
  setIReadChecked: (boolean) => void;
  didBeehave: boolean;
};

const FooterButtons: FC<Props> = ({
    onClickPrimary,
    primaryButton,
    onClickSecondary,
    primaryDisabled,
    secondaryButton,
    secondaryDisabled,
    iReadChecked,
    setIReadChecked,
    didBeehave
}: Props) => {
    return (
        <Container>
            <ButtonsContainer>
                <FooterButton onClick={onClickPrimary} disabled={primaryDisabled}>
                    {primaryButton}
                </FooterButton>
                {secondaryButton && onClickSecondary ? (
                    <FooterButton onClick={onClickSecondary} disabled={secondaryDisabled}>
                        {secondaryButton}
                    </FooterButton>
                ) : null}
            </ButtonsContainer>
            {didBeehave && 
                <ConfirmText>
                    <Checkbox
                        icon={<CheckBoxOutlineBlankIcon fontSize="small" />}
                        checkedIcon={<CheckBoxIcon fontSize="small" />}
                        style={{ marginRight: 8, color: '#AAAAAA' }}
                        checked={iReadChecked}
                        onChange={x => setIReadChecked(x.target.checked)}
                    />
                    {'I read the Automatic PR Feedback and wish to submit the PR'}
                </ConfirmText>
            }
            {didBeehave ? <FooterText>{'Update your PR and analyze again to improve your rating. When you are done you may submit your work.'}</FooterText> : null}
        </Container>
    );
};

export default FooterButtons;
