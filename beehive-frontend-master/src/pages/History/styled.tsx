import { Box, styled, Tabs } from '@mui/material';

import { colors } from '../../theme';

export const Container = styled(Box)`
    padding: 60px 100px;
    height: 100vh;
    
    background: ${colors.black87};
    & .MuiBox-root {
        padding: 0;
    }
`;

export const StyledTabs = styled(Tabs)`
    & .MuiTab-root {
        color: ${colors.white90};
        text-transform: none;
        font: 500 12px/15px 'Inter', sans-serif;
    }
    & .MuiTab-root.Mui-selected {
        color: ${colors.lightningYellow};
    }
    & .MuiTabs-indicator {
        height: 1px;
        background-color: ${colors.lightningYellow};
    }
`;
