import { Box, Button, styled, Typography } from '@mui/material';

import { colors } from '../../../../theme';

export const Container = styled(Box)`
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-direction: column;
`;

export const ButtonsContainer = styled(Box)`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
`;

export const FooterButton = styled(Button)`
  color: ${colors.orangeyYellow};
  width: 130px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 100px;
  background-color: ${colors.novajoWhite10};
  text-transform: capitalize;
  &.Mui-disabled {
    color: ${colors.dimGray};
  }
`;

export const FooterText = styled(Typography)`
  color: ${colors.white50};
  margin-top: 16px;
  text-align: center;
  font-family: Inter;
  font-size: 11px;
  font-style: normal;
  font-weight: 400;
  line-height: 23px;
`;

export const ConfirmText = styled(Box)`
  color: ${colors.white50};
  margin-top: 16px;
  text-align: center;
  font-family: Inter;
  font-size: 11px;
  font-style: normal;
  font-weight: 400;
  line-height: 23px;
  flexGrow: 1;
  margin: '10px 0px 0px 0px';
`;
