import StarIcon from '@material-ui/icons/Star';
import { Rating as MuiRating, TextField } from '@mui/material';
import { FunctionComponent, useCallback, useState } from 'react';

import S from './styled';

type Props = {
    onValueChange: (rating: string, text: string) => void
};

const Rating: FunctionComponent<Props> = ({ onValueChange }: Props) => {
    const [ rating, setRating ] = useState<string>('');
    const [ text, setText ] = useState<string>('');
    const [ ratingText, setRatingText ] = useState<string>('');

    const handleChangeRating = useCallback((event) => {
        setRating(event.target.value);
        switch (event.target.value) {
            case '1':
            case '2':
                setRatingText('Below average');
                break;
            case '3':
                setRatingText('Good');
                break;
            case '4':
            case '5':
                setRatingText('Above average');
                break;
            default:
                setRatingText('');
        }
        onValueChange(event.target.value, text);
    }, [ text ]);

    const handleChangeText = useCallback((event) => {
        setText(event.target.value);
        onValueChange(rating, event.target.value);
    }, [ rating ]);

    return (
        <S.Container>
            <S.Title>
                Rate this work
            </S.Title>
            <S.Content>
                How would you rate the work description?
            </S.Content>
            <S.RaitingContainer>
                <MuiRating 
                    emptyIcon={
                        <StarIcon 
                            fontSize="inherit"
                            style={S.StarIcon}
                        />
                    }
                    size="small"
                    onChange={handleChangeRating}
                />
                <S.RatingText>
                    {ratingText}
                </S.RatingText>
            </S.RaitingContainer>
            <S.ImproveText>
                How can we improve?
            </S.ImproveText>
            <TextField
                id="filled-multiline-static"
                multiline
                placeholder="Write your feedback here..."
                rows={4}
                onChange={handleChangeText}
                sx={S.TextField}
            />
        </S.Container>
    );
};

export default Rating;
