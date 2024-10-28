import styled from '@emotion/styled';
import { Box, Typography } from '@mui/material';

import { Colors } from '../../../../utils/Colors';

const S = {
    Container: styled(Box)({
        marginTop: '10px',
        backgroundColor: Colors.tealishBlue,
        alignItems: 'center',
        borderRadius: '4px',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        gap: 16
    }),
    Title: styled(Typography)({
        font: '600 14px Inter',
        lineHeight: '16.94px',
        color: Colors.white90
    }),
    Content: styled(Typography)({
        font: '400 13px Inter',
        lineHeight: '23px',
        color: Colors.white50
    }),
    RaitingContainer: styled(Box)({
        alignItems: 'center',
        padding: '0px',
        display: 'flex',
        flexDirection: 'column',
        gap: '7px'
    }),
    RatingText: styled(Typography)({
        font: '400 11px Inter',
        lineHeight: '18px',
        background: 'linear-gradient(105.23deg, rgba(250, 187, 24, 0.6) 0%, rgba(196, 142, 2, 0.6) 100%)',
        '-webkit-background-clip': 'text',
        '-webkit-text-fill-color': 'transparent'
    }),
    ImproveText: styled(Typography)({
        font: '400 13px Inter',
        lineHeight: '23px',
        color: Colors.white50,
        marginTop: '16px'
    }),
    TextField: {
        width: '100%',
        height: '102px',
        '& .MuiInputBase-root': {
            background: Colors.white07,
            color: Colors.white30,
            font: '400 12px Inter',
            lineHeight: '14.52px'
        },
        '& .Mui-focused': {
            '& fieldset': {
                borderColor: `${Colors.white90} !important`
            }
        }
    },
    StarIcon: { 
        color: '#65666E' 
    }
};

export default S;
