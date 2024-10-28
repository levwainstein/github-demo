import { makeStyles } from '@material-ui/core/styles';
import StarIcon from '@material-ui/icons/Star';
import { Box, Rating as MuiRating, TextField } from '@mui/material';
import { FunctionComponent, useCallback } from 'react';

import { ActionButton } from '../../../shared';
import { UserRating } from '../../../types/rating';
import { DescriptionTitle, RatingTitle } from './Description/styled';

type Props = {
    title: string;
    description: string;
    handleDoneClick: (userRating: UserRating) => void;
    setUserRating: React.Dispatch<React.SetStateAction<UserRating>>;
    userRating: UserRating;
};

const useStyles = makeStyles((theme) => ({
    doneButton: {
        height: '42px',
        widht: '126px',
        background: 'linear-gradient(105.23deg, #FABB18 0%, #C48E02 100%)'
    },
    actionContainer: {
        width: '126px',
        marginLeft: '35px',
        marginTop: '20px'
    },
    text: {
        color: theme.palette.text.hint
    },
    starIconEmpty: {
        color: '#65666E'
    }
}));

const DescriptionRating: FunctionComponent<Props> = ({
    title,
    description,
    handleDoneClick,
    setUserRating,
    userRating
}) => {
    const classes = useStyles();
    const handleScoreChange = useCallback((newScore: number | null) => {
        setUserRating({
            ...userRating,
            score: newScore === null ? 0 : newScore
        });
    }, []);

    const handleOnChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
    ) => {
        setUserRating({
            ...userRating,
            feedback: e.target.value
        });
    };

    const onClick = () => {
        handleDoneClick(userRating);
    };

    return (
        <>
            <div>
                <RatingTitle>{title}</RatingTitle>
                <DescriptionTitle>
                    {userRating.score > 0
                        ? 'How can we improve? (optional)'
                        : description}
                </DescriptionTitle>

                {userRating.score > 0 ? (
                    <>
                        <TextField
                            id="outlined-basic"
                            variant="outlined"
                            margin="dense"
                            onChange={(e) => handleOnChange(e)}
                            sx={{
                                fieldset: { borderColor: '#1976d2 !important', borderWidth: 2 },
                                input: { color: '#fff' }
                            }}

                        />
                        <Box className={classes.actionContainer}>
                            <ActionButton
                                buttonClassName={classes.doneButton}
                                onClick={onClick}
                                variant="contained"
                                text="Done"
                            />
                        </Box>
                    </>
                ) : (
                    <MuiRating
                        emptyIcon={
                            <StarIcon
                                fontSize="inherit"
                                className={classes.starIconEmpty}
                            />
                        }
                        onChange={(_event, value) => handleScoreChange(value)}
                    />
                )}
            </div>
        </>
    );
};

export default DescriptionRating;
