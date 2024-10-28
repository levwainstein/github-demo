import { Box, Grid, InputAdornment, TextField, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import Avatar from '@mui/material/Avatar';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import { FunctionComponent, useState } from 'react';

import { setWorkRecordRatings, WorkSelectors } from '../../../../reducers/work';
import { Rating } from '../../../../shared';
import Github from './icons/github.png';

const useStyles = makeStyles(theme => {
    return {
        root: {
            backgroundColor: theme.palette.primary.dark,
            color: 'white',
            border: '1px solid #1E202A',
            borderRadius: '8px',
            padding: '0px 5px 0px 5px',
            height: '100%',
            textAlign: 'center',
            overflowY: 'scroll'
        },
        boxCard: {
            border: '1px solid #31333E',
            flexGrow: 1,
            background: theme.palette.primary.dark,
            flexBasis: 0,
            justifyContent: 'flex-end'
        },
        innerContainer: {
            width: '100%',
            padding: theme.spacing(1)
        },
        leftGridItem: {
            display: 'flex',
            justifyContent: 'flex-end',
            height: '100%',
            [theme.breakpoints.down('sm')]: {
                justifyContent: 'center'
            }
        },
        rightGridItem: {
            display: 'flex',
            justifyContent: 'flex-start',
            [theme.breakpoints.down('sm')]: {
                justifyContent: 'center'
            }
        },
        inputLabel: {
            display: 'flex',
            alignItems: 'center',
            margin: '18px',
            color: theme.palette.text.hint,
            letterSpacing: '-0.04em',
            fontSize: '14px'
        },
        toggleButton: {
            '&.MuiToggleButton-root': {
                backgroundColor: 'black',
                color: theme.palette.text.hint,
                borderRadius: '8px',
                border: '1px solid #414451'
            },
            '&.Mui-selected': {
                color: '#E5EAf2 !important',
                backgroundColor: '#414451 !important'
            },
            '&:hover': {
                color: theme.palette.secondary.main
            }
        }, 
        disabledTextField: {
            backgroundColor: theme.palette.primary.dark,
            borderRadius: '8px',
            border: '1px solid #414451',
            maxWidth: '400px',
            width: '100%',
            // these can't be set as InputProps.classes because that breaks the AutoComplete component
            '& .MuiInputBase-input': {
                color: theme.palette.secondary.main,
                letterSpacing: '-0.04em',
                fontSize: '12px',
                width: '100%'
            },
            '& .MuiOutlinedInput-notchedOutline': {
                borderRadius: '8px'
            },
            '& .MuiIconButton-root': {
                color: '#C7C7C7'
            },
            '& .MuiFormHelperText-root': {
                color: 'red'
            },
            '& .MuiOutlinedInput-input': {
                cursor: 'pointer'
            }
        },
        ratingContainer: {
            marginTop: '10px',
            margin: '0px 20px 0px 20px'
        }
    };
});

type Props = {
    solutionUrl: string | null;
    setReviewApproved: (isApproved: boolean | null) => void;
};

const SolutionReview: FunctionComponent<Props> = ({
    solutionUrl, setReviewApproved: setReviewApproved
}: Props) => {

    const classes = useStyles();
    const [ toggleValue, setToggleValue ] = useState<string>('');
    const { workRecordRatings } = WorkSelectors();
    
    const handleReviewToggleChange = ( _event, value ) => {
        setToggleValue(value);
        setReviewApproved(value === null ? null : value === 'approve');
    };

    return (
        <Box className={classes.root}>
            {solutionUrl && (
                <Grid container>
                    <Grid item sm={6} xs={12}> 
                        <Box className={classes.leftGridItem}>
                            <Typography className={classes.inputLabel}>
                                Pull Request (PR) Url:
                            </Typography>
                        </Box>
                    </Grid>
                    <Grid item sm={6} xs={12}>
                        <Box className={classes.rightGridItem}>
                            <TextField
                                id="outlined-basic"
                                className={classes.disabledTextField}
                                variant="outlined"
                                margin="dense"
                                fullWidth
                                InputProps={{
                                    endAdornment: (
                                        <InputAdornment position="end">
                                            <Avatar src={Github} sx={{ width: 24, height: 24 }} />
                                        </InputAdornment>
                                    )
                                }}
                                
                                type="url"
                                onClick={() => {
                                    window.open(`${solutionUrl}`);
                                }}
                                value={solutionUrl}
                            />
                        </Box>
                    </Grid>
                </Grid>
        
            )}
            <Grid container>
                <Rating 
                    ratings={workRecordRatings}
                    setRatings={setWorkRecordRatings}
                />
            </Grid>
            <Box>
                <Box className={classes.innerContainer}>
                    <ToggleButtonGroup
                        value={toggleValue}
                        exclusive
                        onChange={handleReviewToggleChange}
                        aria-label="Outcome"
                    >
                        <ToggleButton className={classes.toggleButton} value="modifications">Request Modifications</ToggleButton>
                        <ToggleButton className={classes.toggleButton} value="approve">Approve Solution</ToggleButton>
                    </ToggleButtonGroup>

                </Box>
            </Box>
        </Box>
    );
};

export default SolutionReview;
