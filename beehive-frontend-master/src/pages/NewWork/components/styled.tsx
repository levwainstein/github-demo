import { Box, Typography } from '@mui/material';
import { styled } from '@mui/system';

import { Colors } from '../../../utils/Colors';

export const BG = styled(Box)`
    background-color: ${Colors.cinder};
    min-height: 100vh;
    min-width: fit-content;
`;

export const Container = styled(Box)`
    background-color: ${Colors.cinder};
    padding: 20px;
    height: 100%;
`;

export const NextWorkButton = styled(Typography)`
    background-color: ${Colors.novajoWhite10};
    width: 138px;
    height: 40px;
    border-radius: 100px;
    position: relative;
    left: 50%;
    transform: translateX(-50%);
    color: ${Colors.mainGold};
    font: 500 14px 'Inter';
    display: flex;
    justify-content: center;
    align-items: center;
`;

export const DescriptionTermsContainer = styled(Box)`
    display: flex;
    align-items: stretch;
    justify-content: space-between;
    gap: 15px;
`;

export const DescriptionWrapper = styled(Box)`
    display: flex;
    flex-direction: column;
    flex: 1;
    justify-content: flex-start;
    gap: 5px;
`;

