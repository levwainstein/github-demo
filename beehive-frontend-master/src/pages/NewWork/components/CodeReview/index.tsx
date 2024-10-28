import { Rating } from '@mui/material';
import { FC } from 'react';

import { BeehaveReview } from '../../../../types/beehaveReview';
import { ReviewPropsTypes } from '../../../../types/contributorWork';
import {
    // AutoImproveDocumentationBox,
    // AutoImproveDocumentationText,
    FeedbackStep,
    RatingName,
    RatingNumber,
    ReviewBox,
    ReviewHeader,
    Root,
    Title
} from './styled';

const Review: FC<ReviewPropsTypes> = ({ name, rating, feedback }) => (
    <ReviewBox>
        <ReviewHeader>
            <Title>{name}</Title>
            <Rating value={rating} readOnly size="small" />
            <RatingNumber>{rating}</RatingNumber>
            <RatingName>{rating2label[rating-1]}</RatingName>
            {/* {name === 'Documentation' && (
                <AutoImproveDocumentationBox>
                    <AutoImproveDocumentationText>
                        Auto improve documentation
                    </AutoImproveDocumentationText>
                </AutoImproveDocumentationBox>
            )} */}
        </ReviewHeader>
        {feedback.map((step, index) => (
            <FeedbackStep key={index}>• {step}</FeedbackStep>
        ))}
    </ReviewBox>
);

export type CodeReviewProps = {
    reviews: BeehaveReview;
};

const rating2label = [
    'Poor',
    'Below Average',
    'Average',
    'Good',
    'Excellent'
];

const CodeReview: FC<CodeReviewProps> = ({ reviews }) => {
    return (
        <Root>
            <Review 
                key={1} 
                name={'Functionality'} 
                rating={reviews['functionality_score']} 
                feedback= {reviews['functionality_improvements']} 
            />
            <Review 
                key={2} 
                name={'Code Quality'} 
                rating={reviews['code_quality_score']} 
                feedback= {reviews['code_quality_improvements']} 
            />
            <Review 
                key={3} 
                name={'Documentation'} 
                rating={reviews['documentation_score']} 
                feedback= {reviews['documentation_improvements']} 
            />
            <Review 
                key={4} 
                name={'Test Coverage'} 
                rating={reviews['test_coverage_score']} 
                feedback= {reviews['test_coverage_improvements']} 
            />
        </Root>
    );
};

export default CodeReview;
