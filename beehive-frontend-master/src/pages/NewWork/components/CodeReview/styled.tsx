import { Box, styled, Typography } from '@mui/material';

import { colors } from '../../../../theme';

export const Root = styled(Box)`
    padding: 24px;
    border-radius: 4px;
    background-color: ${colors.darkBlue};
`;

export const ReviewBox = styled(Box)`
    border-bottom: 1px solid ${colors.blackRock};
    padding-bottom: 20px;
    margin-bottom: 20px;
    &:last-of-type {
        border-bottom: none;
        padding-bottom: 0px;
        margin-bottom: 0;
    }
`;

export const ReviewHeader = styled(Box)`
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 13.5px;
    & .MuiRating-iconEmpty svg {
        fill: ${colors.white10};
    }
`;

export const Title = styled(Typography)`
    font: 500 12px 'Inter';
    color: ${colors.white90};
    width: 110px;
`;

export const RatingNumber = styled(Typography)`
    font: 600 12px/18px 'Inter';
    background: ${colors.yellowText};
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
`;

export const RatingName = styled(Typography)`
    font: 11px/18px 'Inter';
    background: ${colors.yellowText2};
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
`;

export const AutoImproveDocumentationBox = styled(Box)`
    padding: 10px 24px;
    cursor: pointer;
    border-radius: 100px;
    background-color: ${colors.lightOrangeYellow};
`;

export const AutoImproveDocumentationText = styled(Typography)`
    font: 500 14px 'Inter';
    background: ${colors.yellowText};
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
`;

export const FeedbackStep = styled(Typography)`
    font: 13px/23px 'Inter';
    color: ${colors.white50};
`;
