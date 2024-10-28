import { Box, styled, Typography } from '@mui/material';

import { colors } from '../../../../theme';

export const Title = styled(Typography)`
    font: 600 14px 'Inter';
    color: ${colors.white90};
`;

export const Content = styled(Typography)`
    font: 13px/23px 'Inter';
    color: ${colors.white50};
    white-space: pre-wrap;
    height: 50vh;
    overflow-y: scroll;
`;

export const RatingTitle = styled(Typography)`
    font: 600 14px 'Inter';
    color: ${colors.white90};
    white-space: pre-wrap;
    margin-bottom: 16px;
    '*::-webkit-scrollbar': {
        width: '0.4em'
      },
      '*::-webkit-scrollbar-track': {
        '-webkit-box-shadow': 'inset 0 0 6px rgba(0,0,0,0.00)'
      },
      '*::-webkit-scrollbar-thumb': {
        backgroundColor: 'rgba(0,0,0,.1)',
        outline: '1px solid slategrey'
      };
`;

export const DescriptionTitle = styled(Typography)`
    font: 15px 'Inter';
    color: ${colors.white50};
    margin-bottom: 16px;
`;

export const ReadButton = styled(Box)`
    font: 13px/23px 'Inter';
    color: ${colors.orangeyYellow80};
    margin-left: 7px;
    text-decoration: underline;
    cursor: pointer;
`;

export const Container = styled(Box)`
    background-color: ${colors.tealishBlue};
    border-radius: 4px;
    padding: 24px;  
    display: flex;
    flex-direction: column;
    justify-content: space-between;
`;
