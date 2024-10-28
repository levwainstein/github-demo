import { makeStyles, Theme } from '@material-ui/core/styles';
import { Box } from '@mui/material';
import { FC, useCallback, useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';

import { useAppDispatch } from '../../../../hooks';
import { setWorkActionError, setWorkRatings, submitWorkRating, WorkSelectors } from '../../../../reducers/work';
import { Rating } from '../../../../shared';
import { ContributorWorkSteps } from '../../../../types/contributorWork';
import { isRatingsCompleted, RatingSubject, UserRatings } from '../../../../types/rating';
import { Container, Content, Title } from './styled';

export type Props = {
    content: string;
    currentStep: ContributorWorkSteps;
};

const useStyles = makeStyles<Theme>(theme => {
    return {
        markdown: {
            '& p > a': {
                color: theme.palette.secondary.main
            },
            '& p > a:visited': {
                color: theme.palette.secondary.dark
            }
        }
    };
});

const Description: FC<Props> = ({ content, currentStep }) => {
    const { workRatings, workRatingAuthorizationCode } = WorkSelectors();
    const [ workRatingSubmitted, setWorkRatingSubmitted ] = useState<boolean>(false);
    const dispatch = useAppDispatch();
    const classes = useStyles();

    const contentnMarkdown = useMemo(
        () => content.replace(/\n/gi, '  \n'),
        [ content ]
    );

    const submitRatings = useCallback(
        (ratings: UserRatings, authorizationCode: string) => {
            return Promise.all(
                Object.keys(ratings).map((subject) => {
                    if (ratings[subject].score === 0) {
                        return Promise.reject();
                    }
                    return dispatch(
                        submitWorkRating({
                            code: authorizationCode,
                            subject: subject as RatingSubject,
                            rating: ratings[subject]
                        })
                    ).unwrap();
                })
            ).catch(function (err) {
                console.log('An error while rating work: ', err);
                dispatch(setWorkActionError('rating'));
            });
        },
        [ dispatch, submitWorkRating ]
    );

    const onSubmitRating = useCallback(
        (ratings: UserRatings) => {
            setWorkRatingSubmitted(true);
            if (!isRatingsCompleted(ratings)) {
                dispatch(setWorkActionError('rating_invalid'));
                return Promise.reject();
            }
            
            return submitRatings(ratings, workRatingAuthorizationCode)
                .catch(payload => {
                    console.log('error rating: ', payload);
                });
        },
        [ setWorkRatingSubmitted ]
    );

    return (
        <Container minHeight={currentStep === ContributorWorkSteps.AnalyzePullRequest ? '408px' : (currentStep === ContributorWorkSteps.SubmitPullRequest || currentStep === ContributorWorkSteps.DescriptionFeedback) ? '230px' : '528px'}>
            <div style={{ flexGrow: 100 }}>
                <Title>Work description</Title>
                <Box height={16} />
                <Content>
                    <ReactMarkdown
                        className={classes.markdown}
                        source={contentnMarkdown}
                        linkTarget="_blank"
                        transformLinkUri={(uri) => {
                            const urlStr = ReactMarkdown.uriTransformer(uri);

                            if (urlStr.indexOf(':') === -1) {
                                return `https://${urlStr}`;
                            } else {
                                return urlStr;
                            }
                        }}
                    />
                </Content>
                
            </div>
            <Box height={20}/>
            {(currentStep === ContributorWorkSteps.TaskAccept) && !workRatingSubmitted && (
                <Rating
                    ratings={workRatings} 
                    setRatings={setWorkRatings}
                    onSubmit={onSubmitRating}/>
            )}
            
        </Container>
    );
};

export default Description;
