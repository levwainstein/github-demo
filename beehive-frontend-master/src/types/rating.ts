export type RatingSubject =
    'work_description' |
    'work_solution_match_requirements' |
    'work_solution_code_quality' |
    'work_review_qa_functionality' |
    'work_review_code_quality';

export type UserRating = {
    score: number;
    feedback?: string;
};

export type UserRatings = { [key in RatingSubject]: UserRating };

export const initUserRatings = (subjects: RatingSubject[]): UserRatings => {
    return Object.fromEntries(
        subjects.map((subject) => [
            subject, { score: 0, feedback: undefined }
        ])
    ) as UserRatings;
};

export const isRatingsCompleted = (ratings: UserRatings): boolean => {
    return Object.keys(getUnscoredRatingSubjects(ratings)).length === 0;
};

export const getUnscoredRatingSubjects = (ratings: UserRatings): UserRatings => {
    return ratings && Object.keys(ratings).length > 0 ? 
        Object.fromEntries(
            Object.entries(ratings).filter(
                ([ , rating ]) => rating.score === 0
            )
        ) as UserRatings
        : {} as UserRatings;
};
