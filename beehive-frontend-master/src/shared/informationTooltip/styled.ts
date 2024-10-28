import { withStyles } from '@material-ui/core/styles';
import Tooltip from '@mui/material/Tooltip';

import { colors } from '../../theme';

export const TooltipStyled = withStyles(() => ({
    arrow: {
        '&::before': {
            backgroundColor: `${colors.blackRock} !important`
        }
    },
    tooltip: {
        backgroundColor: `${colors.blackRock} !important`,
        boxShadow: '0px 1.11111px 5.07639px 0px rgba(0, 0, 0, 0.05), 0px 4.88889px 10.51111px 0px rgba(0, 0, 0, 0.08), 0px 12px 20.9625px 0px rgba(0, 0, 0, 0.10), 0px 23.11111px 41.08889px 0px rgba(0, 0, 0, 0.12), 0px 38.88889px 75.54861px 0px rgba(0, 0, 0, 0.15), 0px 60px 129px 0px rgba(0, 0, 0, 0.20)',
        color: `${colors.white70} !important`,
        fontSize: '11px !important',
        fontStyle: 'normal !important',
        lineHeight: 2,
        padding: '12px 18px !important',
        width: 'fit-content',
        whiteSpace: 'pre-line'
    }
}))(Tooltip);
