import { Box, styled } from '@mui/material';

import { Colors } from '../../../../utils/Colors';

export const Container = styled(Box)`
    background-color: ${Colors.tealishBlue};
    height: 700px;
    width: 100%;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
`;

export const TaskCompletedImage = {
    borderRadius: '15px'
};
