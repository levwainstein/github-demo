import { makeStyles } from '@material-ui/core/styles';

import { colors } from '../../theme';

export const useStyles = makeStyles(() => ({
    container: {
        display: 'flex',
        flexDirection: 'column',
        borderRadius: '4px',
        background: colors.blackRock,
        padding: '15px',
        gap: '25px',
        width: '334px',
        boxSizing: 'border-box',
        '& .css-1yk1gt9-MuiInputBase-root-MuiOutlinedInput-root-MuiSelect-root': {
            background: colors.lightGrey,
            borderRadius: '16px',
            width: '100%',
            height: '32px',
            lineHeight: '32px',
            padding: '7px 10px'
        },
        '& .css-11u53oe-MuiSelect-select-MuiInputBase-input-MuiOutlinedInput-input':
      {
          fontFamily: 'Inter',
          fontStyle: 'normal',
          fontWeight: 400,
          fontSize: '12px',
          lineHeight: '18px',
          padding: 0,
          color: colors.white90
      },
        '& ul ': {
            backgroundColor: 'red'
        }
    },
    title: {
        color: colors.white90,
        fontFamily: 'Inter',
        fontStyle: 'normal',
        fontSize: '16px',
        fontWeight: 600
    },
    subtitle: {
        color: colors.white50,
        fontFamily: 'Inter',
        fontStyle: 'normal',
        fontSize: '12px',
        lineHeight: '18px',
        fontWeight: 400,
        marginBottom: '25px'
    },
    input: {
        width: '304px',
        padding: '14px 20px',
        borderRadius: '20px',
        boxSizing: 'border-box',
        border: `1px solid ${colors.goldenYellow}`,
        outline: 'none',
        '& .css-1t8l2tu-MuiInputBase-input-MuiOutlinedInput-input, & .css-dpjnhs-MuiInputBase-root-MuiOutlinedInput-root':
      {
          padding: 0,
          backgroundImage: colors.yellowText,
          '-webkit-background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
          height: '61px',
          display: 'flex',
          flexDirection: 'column',
          '& textarea': {
              flexGrow: 1,
              lineHeight: '12px',
              fontSize: '12px',
              caretColor: colors.goldenYellow,
              '&::placeholder': {
                  lineHeight: '12px',
                  fontSize: '12px',
                  backgroundImage: colors.yellowText,
                  '-webkit-background-clip': 'text',
                  '-webkit-text-fill-color': 'transparent'
              }
          }
      },
        '& .css-1d3z3hw-MuiOutlinedInput-notchedOutline': {
            border: 'none'
        }
    },
    select: {
        borderRadius: '16px',
        backgroundColor: colors.lightGrey,
        padding: '7px 10px'
    },
    selectIcon: {
        fill: colors.mattGold
    },
    selectItem: {
        borderRadius: '16px',
        backgroundColor: colors.lightGrey,
        padding: '7px 10px',
        marginBottom: '12px',
        color: colors.white70,
        '&.css-kk1bwy-MuiButtonBase-root-MuiMenuItem-root': {
            color: colors.white70
        },
        '&.css-kk1bwy-MuiButtonBase-root-MuiMenuItem-root.Mui-selected': {
            backgroundColor: colors.lightGrey,
            color: colors.white70
        }
    },
    buttonsContainer: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '0 12px'
    },
    button: {
        width: '130px',
        height: '40px',
        padding: '10px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: '100px',
        backgroundColor: colors.lightGrey
    },
    buttonText: {
        backgroundImage: colors.yellowText,
        '-webkit-background-clip': 'text',
        '-webkit-text-fill-color': 'transparent',
        fontWeight: 500,
        fontSize: '14px',
        textTransform: 'capitalize'
    }
}));

export const styles = {
    dialogPaper: {
        background: 'none',
        borderRadius: '4px'
    },
    selectMenu: {
        padding: '15px',
        borderRadius: '4px',
        backgroundColor: colors.blackRock
    }
};
