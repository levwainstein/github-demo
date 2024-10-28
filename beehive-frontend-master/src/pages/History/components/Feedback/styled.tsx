import { Box, styled } from '@mui/material';

import { colors } from '../../../../theme';

export const S = {
    modal: {
        marginTop: '40px'
    },
    title: {
        color: colors.white90,
        fontFamily: 'Inter',
        fontWeight: 600,
        fontSize: '16px',
        paddingBottom: '10px',
        lineHeight: '19px'
    },
    created: {
        color: colors.lightDimYellowRgba,
        fontFamily: 'Inter',
        fontSize: '12px',
        textDecoration: 'underline',
        paddingLeft: '5px',
        lineHeight: '12px'
    },
    createdTitle: {
        color: colors.white30,
        fontFamily: 'Inter',
        fontSize: '12px'
    },
    rating: {
        color: colors.lightningYellow,
        fontFamily: 'Inter',
        fontWeight: 600,
        fontSize: '12px',
        paddingLeft: '20px',
        lineHeight: '18px'
    },
    text: {
        color: colors.white70,
        fontFamily: 'Inter',
        fontSize: '12px',
        lineHeight: '24px'
    }
};

export const DescriptionBox = styled(Box)`
    display: flex;
    flex-direction: column;
`;

export const WrapperBox = styled(Box)`
    display: flex;
    flex-direction: column;
`;

export const HorizontalLine = styled(Box)`
    border: 1px solid ${colors.tuna};
    margin-top: 36px;
    margin-bottom: 36px;
`;

export const CreatedAt = styled(Box)`
    margin-bottom: 10px;
`;

export const RatingBox = styled(Box)`
    display: flex;
    align-items: center;
    margin-bottom: 10px;
`;
