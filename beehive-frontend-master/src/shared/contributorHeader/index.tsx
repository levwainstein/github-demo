import { Box, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Rating from '@mui/material/Rating';
import TextField from '@mui/material/TextField';
import { FunctionComponent, useState } from 'react';

import ContributorStatus from '../contributorStatus';

const useStyles = makeStyles(() => ({
    root: {
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        margin: 30,
        width: '55%',
        height: '125px',
        background: '#111218',
        '& .css-1c99szj-MuiRating-icon': {
            color: 'rgba(255, 255, 255, 0.07)'
        }
    },
    avatar: {
        width: '110px',
        height: '110px'
    },
    firstCol: {
        flex: 1,
        marginLeft: '24px'
    },
    name: {
        fontFamily: 'Inter',
        fontStyle: 'normal',
        fontWeight: 600,
        fontSize: '20px',
        lineHeight: '24px',
        color: 'rgba(255, 255, 255, 0.9)'
    },
    location: {
        display: 'flex',
        flexDirection: 'row',
        height: '23.31px',
        alignItems: 'center',
        marginTop: '10px',
        marginBottom: '10px'
    },
    country: {
        fontFamily: 'Inter',
        fontStyle: 'normal',
        fontWeight: 500,
        fontSize: '12px',
        lineHeight: '15px',
        color: 'rgba(255, 255, 255, 0.9)',
        marginLeft: '7px',
        marginRight: '12px'
    },
    time: {
        fontFamily: 'Inter',
        fontStyle: 'normal',
        fontWeight: 400,
        fontSize: '11px',
        lineHeight: '18px',
        color: 'rgba(255, 255, 255, 0.6)'
    },
    ratings: {
        display: 'flex',
        flexDirection: 'row',
        height: '18px',
        alignItems: 'center'
    },
    rating: {
        fontFamily: 'Inter',
        fontStyle: 'normal',
        fontWeight: 600,
        fontSize: '16px',
        lineHeight: '19px',
        background: 'linear-gradient(105.23deg, #FABB18 0%, #C48E02 100%)',
        marginLeft: '13.5px',
        marginRight: '12px',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent'
    },
    totalRatings: {
        fontFamily: 'Inter',
        fontStyle: 'normal',
        fontWeight: 400,
        fontSize: '11px',
        lineHeight: '18px',
        background: 'linear-gradient(105.23deg, rgba(250, 187, 24, 0.6) 0%, rgba(196, 142, 2, 0.6) 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        cursor: 'pointer'
    },
    secondCol: {
        flex: 1,
        marginTop: '25px'
    },
    row: {
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        marginTop: '10px'
    },
    label: {
        width: '63px',
        fontFamily: 'Inter',
        fontStyle: 'normal',
        fontWeight: 400,
        fontSize: '12px',
        lineHeight: '12px',
        display: 'flex',
        alignItems: 'center',
        color: 'rgba(255, 255, 255, 0.6)',
        marginRight: '23px'
    },
    status: {
        fontFamily: 'Inter',
        fontStyle: 'normal',
        fontWeight: 400,
        fontSize: '12px',
        lineHeight: '12px',
        display: 'flex',
        alignItems: 'center',
        color: 'rgba(255, 255, 255, 0.3)',
        paddingLeft: '12px'
    },
    hourlyRateBox: {
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        paddingLeft: '10px',
        width: '91px',
        height: '32px',
        background: '#1E202A',
        borderRadius: '16px',
        cursor: 'pointer'
    },
    hourlyRateText: {
        fontFamily: 'Inter',
        fontStyle: 'normal',
        fontWeight: 400,
        fontSize: '12px',
        lineHeight: '18px',
        color: 'rgba(255, 255, 255, 0.9)'
    },
    hourlyRateDialog: {
        '& .css-1t1j96h-MuiPaper-root-MuiDialog-paper': {
            width: '225px',
            background: '#111218',
            borderRadius: '10px'
        },
        '& .css-bdhsul-MuiTypography-root-MuiDialogTitle-root': {
            fontFamily: 'Inter',
            fontStyle: 'normal',
            fontWeight: 700,
            fontSize: '12px',
            lineHeight: '18px',
            display: 'flex',
            alignItems: 'center',
            color: '#FFFFFF'
        },
        '& .css-qfso29-MuiTypography-root-MuiDialogContentText-root': {
            fontFamily: 'Inter',
            fontStyle: 'normal',
            fontWeight: 400,
            fontSize: '12px',
            lineHeight: '18px',
            display: 'flex',
            alignItems: 'center',
            color: 'rgba(255, 255, 255, 0.8)'
        },
        '& .css-1z10yd4-MuiFormControl-root-MuiTextField-root': {
            '&:before, :after, :hover:not(.Mui-disabled):before': {
                borderBottom: 0
            },
            width: '35px',
            marginTop: '0px'
        },
        '& .css-1a1fmpi-MuiInputBase-root-MuiInput-root': {
            fontFamily: 'Inter',
            fontStyle: 'normal',
            fontWeight: 400,
            fontSize: '12px',
            lineHeight: '18px',
            display: 'flex',
            alignItems: 'center',
            textAlign: 'center',
            color: '#111218'
        },
        '& .css-hlj6pa-MuiDialogActions-root': {
            justifyContent: 'space-evenly',
            marginBottom: '10px'
        },
        '& .css-hlj6pa-MuiDialogActions-root > .cancel-btn': {
            padding: '10px 9px',
            width: '60px',
            height: '15px',
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '4px',
            fontFamily: 'Inter',
            fontStyle: 'normal',
            fontWeight: 600,
            fontSize: '10px',
            lineHeight: '12px',
            letterSpacing: '-0.04em',
            color: '#FFFFFF',
            textTransform: 'initial'
        },
        '& .css-hlj6pa-MuiDialogActions-root > .save-btn': {
            padding: '10px 9px',
            width: '60px',
            height: '15px',
            background: '#E6BB42',
            borderRadius: '4px',
            fontFamily: 'Inter',
            fontStyle: 'normal',
            fontWeight: 600,
            fontSize: '10px',
            lineHeight: '12px',
            letterSpacing: '-0.04em',
            color: '#FFFFFF',
            textTransform: 'initial'
        }
    },
    closeIcon: {
        position: 'absolute',
        right: '8.83px',
        cursor: 'pointer'
    },
    inputFieldBox: {
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'space-between',
        width: '175px',
        height: '25px',
        background: '#D9D9D9',
        borderRadius: '10px',
        marginTop: '12px',
        marginBottom: '12px'
    },
    inputFieldLabel: {
        fontFamily: 'Inter',
        fontStyle: 'normal',
        fontWeight: 400,
        fontSize: '12px',
        lineHeight: '18px',
        display: 'flex',
        alignItems: 'center',
        textAlign: 'center',
        color: '#111218',
        paddingLeft: '10px',
        paddingRight: '10px'
    }
}));

export type Props = {
    avatar?: string;
    name?: string;
    country?: string;
    time?: string;
    rating?: number;
    totalRatings?: string;
    statusOptions: string[];
    handleTotalRatingsClick?: () => void;
};

const ContributorHeader: FunctionComponent<Props> = ({
    avatar,
    name,
    country,
    time,
    rating,
    totalRatings,
    statusOptions,
    handleTotalRatingsClick
}: Props) => {
    const classes = useStyles();
    const [ status, setStatus ] = useState<string>('Inactive');
    const [ rateDialog, setRateDialog ] = useState<boolean>(false);
    const [ hourlyRate, setHourlyRate ] = useState<string>('40.50'); 

    const openRateDialog = () => {
        setRateDialog(true);
    };

    const closeRateDialog = () => {
        setRateDialog(false);
    };

    return (
        <Box className={classes.root}>
            <img src={avatar} className={classes.avatar} />
            <Box className={classes.firstCol}>
                <Typography className={classes.name}>{name}</Typography>
                <Box className={classes.location}>
                    <img src={country?.toLowerCase() + '.png'} />
                    <Typography className={classes.country}>{country}</Typography>
                    <Typography className={classes.time}>({time})</Typography>
                </Box>
                <Box className={classes.ratings}>
                    <Rating name="read-only" value={rating} readOnly precision={0.5} />
                    <Typography className={classes.rating}>{rating}</Typography>
                    <Typography className={classes.totalRatings} onClick={handleTotalRatingsClick}>({totalRatings} ratings)</Typography>
                </Box>
            </Box>
            <Box className={classes.secondCol}>
                <Box className={classes.row}>
                    <Typography className={classes.label}>Hourly rate</Typography>
                    <Box className={classes.hourlyRateBox} onClick={openRateDialog}>
                        <Typography className={classes.hourlyRateText}>${hourlyRate}</Typography>
                    </Box>
                </Box>
                <Box className={classes.row}>
                    <Typography className={classes.label}>Status</Typography>
                    <ContributorStatus
                        options={statusOptions}
                        value={status}
                        handleChange={(e) => setStatus(e.target.value)}
                    />
                    <Typography className={classes.status}>since 3/4/2019</Typography>
                </Box>
            </Box>
            <Dialog open={rateDialog} onClose={closeRateDialog} className={classes.hourlyRateDialog}>
                <DialogTitle>Set hourly rate <img src="close.png" className={classes.closeIcon} onClick={closeRateDialog} /></DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        You can set King David rate by changing the amount below.
                    </DialogContentText>
                    <Box className={classes.inputFieldBox}>
                        <Typography className={classes.inputFieldLabel}>$</Typography>
                        <TextField
                            autoFocus
                            margin="dense"
                            id="hourlyRate"
                            label=""
                            type="text"
                            fullWidth
                            variant="standard"
                            value={hourlyRate}
                            onChange={e => setHourlyRate(e.target.value)}
                        />
                        <Typography className={classes.inputFieldLabel}>/hr</Typography>
                    </Box>
                    <DialogContentText>
                        This is the rate you’ll be pay.
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={closeRateDialog} className="cancel-btn">Cancel</Button>
                    <Button onClick={closeRateDialog} className="save-btn">Save</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default ContributorHeader;
