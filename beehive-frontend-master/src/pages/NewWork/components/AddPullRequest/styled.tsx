import styled from '@emotion/styled';
import { Box, Button } from '@mui/material';
import Chip from '@mui/material/Chip';

import { ReactComponent as ReviewSvg } from '../../../../assets/icons/in-review.svg';
import { ReactComponent as SuccessSvg } from '../../../../assets/icons/success.svg';
import { colors } from '../../../../theme';

const S = {
    Button: styled(Button)((props: {errorsUrl: string|undefined, valuesUrl: string}) => ({
        background: props.errorsUrl ? colors.blackRock: props.valuesUrl ? colors.yellowText: colors.lightOrangeYellow,
        width: '76px',
        height: '40px',
        borderRadius: '100px'
    })),
    Container: styled(Box)({
        height: '40px',
        display: 'flex',
        marginTop: '10px',
        justifyContent: 'space-between',
        alignItems: 'center',
        '& .Mui-focused': {
            '& fieldset': {
                borderColor: `${colors.lightDimYellowRgba} !important`
            }
        },
        '& .Mui-error': {
            '& fieldset': {
                borderColor: `${colors.red25} !important`
            }
        }
    }),
    Input: (error: string | undefined): Record<string, unknown> => ({
        width: '100%',
        height: '40px',
        marginBottom: '0px',
        marginRight: '10px',
        background: colors.white70,
        backgroundColor: colors.darkBluebg,
        borderRadius: '100px',
        '& fieldset': {
            borderColor: colors.white30
        },
        '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: colors.lightDimYellowRgba
        },
        '& input': {
            color: error ? colors.white50 : colors.white70,
            fontWeight: '400',
            lineHeight: '12px',
            fontFamily: 'Inter',
            fontSize: '12px'
        }
    }),
    Root: styled('div')({
        display: 'flex',
        height: '170px',
        justifyContent: 'center',
        alignItems: 'start',
        paddingLeft: '24px',
        backgroundColor: colors.black2,
        flexDirection: 'column',
        gap: '10px',
        marginTop: '10px',
        paddingTop: '10px'
    }),
    InputAdorment: (url: string, error: string | undefined): Record<string, unknown> => ({
        '& p': {
            background: error
                ? colors.errorRed2
                : url
                    ? colors.yellowText
                    : colors.yellowText2,
            '-webkit-background-clip': 'text',
            '-webkit-text-fill-color': 'transparent',
            fontWeight: '400',
            fontSize: '12px',
            fontFamily: 'Inter'
        }
    }),
    ButtonLabel: (url: string, error: string | undefined): Record<string, unknown> => ({
        background: error
            ? colors.white50
            : url
                ? colors.white90
                : colors.yellowText,
        '-webkit-background-clip': 'text',
        '-webkit-text-fill-color': 'transparent',
        fontWeight: '500',
        lineHeight: '16.94px',
        fontSize: '14px',
        fontFamily: 'Inter !important',
        pointerEvents: 'none'
    }),
    ErrorContainer: styled(Box)({
        width: '436px',
        height: '32px',
        display: 'flex',
        paddingBottom: '15px'
    }),
    ErrorChip: styled(Chip)({
        height: '32px',
        backgroundColor: colors.blackRock,
        color: colors.white50,
        fontWeight: '400',
        lineHeight: '20px',
        fontSize: '12px',
        fontFamily: 'Inter'
    }),
    ReviewSvg: styled(ReviewSvg)({
        '& stop': {
            stopColor: colors.errorRed
        }
    }),
    SuccessSvg: styled(SuccessSvg)({
        width: '40px',
        height: '40px'
    }),
    labelTitle: {
        width: '886px',
        height: '17px',
        marginTop: '14px',
        color: colors.white90,
        fontWeight: '600',
        fontFamily: 'Inter',
        fontSize: '14px',
        lineHeight: '16.94px'
    },
    labelInstructions: {
        color: colors.white30,
        fontWeight: '400',
        fontFamily: 'Inter',
        fontSize: '13px',
        lineHeight: '23px'
    }
};

export default S;
