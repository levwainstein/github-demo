import { Box } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { Rating as MUIRating } from '@material-ui/lab';
import { FunctionComponent, useEffect, useState } from 'react';

const labels = {
    1: 'Useless',
    2: 'Requires modification',
    3: 'Great'
};

const useStyles = makeStyles({
    rating: {
        display: 'inline-flex',
        justifyContent: 'center'
    }
});

type Props = {
    rating: number | null;
    onRatingChange: (newRating: number | null) => void;
};

const Rating: FunctionComponent<Props> = ({
    rating, onRatingChange
}: Props) => {
    const classes = useStyles();

    const [ hover, setHover ] = useState(-1);
    const [ displayedLabel, setDisplayedLabel ] = useState<string | null>(null);

    useEffect(() => {
        if (hover > -1) {
            setDisplayedLabel(labels[hover]);
        } else if (rating !== null) {
            setDisplayedLabel(labels[rating]);
        } else {
            setDisplayedLabel(null);
        }
    }, [ rating, hover ]);

    return (
        <>
            <MUIRating
                className={classes.rating}
                size="large"
                max={3}
                value={rating}
                name="rating"
                onChange={(_, newValue) => {
                    onRatingChange(newValue);
                }}
                onChangeActive={(_, newValue) => {
                    setHover(newValue);
                }}
            />
            <Box>
                {displayedLabel ? displayedLabel : 'Please rate this work'}
            </Box>
        </>
    );
};

export default Rating;
