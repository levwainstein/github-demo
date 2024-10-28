import { Box } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import MenuItem from '@mui/material/MenuItem';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import { FunctionComponent } from 'react';

const useStyles = makeStyles(() => ({
    root: {
        '& .css-1yk1gt9-MuiInputBase-root-MuiOutlinedInput-root-MuiSelect-root': {
            background: '#1E202A',
            borderRadius: '16px',
            width: '101px',
            height: '32px'
        },
        '& .css-11u53oe-MuiSelect-select-MuiInputBase-input-MuiOutlinedInput-input': {
            width: '53px',
            height: '18px',
            fontFamily: 'Inter',
            fontStyle: 'normal',
            fontWeight: 400,
            fontSize: '12px',
            lineHeight: '18px',
            color: 'rgba(255, 255, 255, 0.9)'
        },
        '& .css-hfutr2-MuiSvgIcon-root-MuiSelect-icon': {
            color: 'rgba(255, 255, 255, 0.3)'
        },
        '& .css-bpeome-MuiSvgIcon-root-MuiSelect-icon': {
            color: 'rgba(255, 255, 255, 0.3)'
        },
        '& .black-russian': {
            background: '#1E202A !important'
        },
        '& .danger': {
            background: 'rgba(255, 167, 160, 0.1) !important'
        },
        '& .success': {
            background: 'rgba(147, 255, 120, 0.1) !important'
        },
        '& .black-russian > .css-11u53oe-MuiSelect-select-MuiInputBase-input-MuiOutlinedInput-input': {
            color: '#ffffff !important'
        },
        '& .danger > .css-11u53oe-MuiSelect-select-MuiInputBase-input-MuiOutlinedInput-input': {
            color: 'rgba(255, 167, 160, 0.9) !important'
        },
        '& .success > .css-11u53oe-MuiSelect-select-MuiInputBase-input-MuiOutlinedInput-input': {
            color: 'rgba(147, 255, 120, 0.9); !important'
        },
        '&  .black-russian > .css-hfutr2-MuiSvgIcon-root-MuiSelect-icon': {
            color: 'rgba(255, 255, 255, 0.3) !important'
        },
        '&  .danger > .css-hfutr2-MuiSvgIcon-root-MuiSelect-icon': {
            color: 'rgba(255, 167, 160, 0.4) !important'
        },
        '&  .success > .css-hfutr2-MuiSvgIcon-root-MuiSelect-icon': {
            color: 'rgba(147, 255, 120, 0.4) !important'
        },
        '&  .black-russian > .css-bpeome-MuiSvgIcon-root-MuiSelect-icon': {
            color: 'rgba(255, 255, 255, 0.3) !important'
        },
        '&  .danger > .css-bpeome-MuiSvgIcon-root-MuiSelect-icon': {
            color: 'rgba(255, 167, 160, 0.4) !important'
        },
        '&  .success > .css-bpeome-MuiSvgIcon-root-MuiSelect-icon': {
            color: 'rgba(147, 255, 120, 0.4) !important'
        }
    }
}));

export type Props = {
    options: string[];
    value: string;
    handleChange: (event: SelectChangeEvent) => void;
};

const ContributorStatus: FunctionComponent<Props> = ({
    options,
    value,
    handleChange
}: Props) => {
    const classes = useStyles();

    const getBgColor = () => {
        if (value === 'Inactive') {
            return 'black-russian';
        } else if (value === 'Unavailable') {
            return 'danger';
        } else {
            return 'success';
        }
    };

    return (
        <Box className={classes.root}>
            <Select
                value={value}
                onChange={handleChange}
                displayEmpty
                className={getBgColor()}
            >
                {
                    options?.map((item, index) => {
                        return <MenuItem value={item} key={index}>{item}</MenuItem>;
                    })
                }
            </Select>
        </Box>
    );
};

export default ContributorStatus;
