export type BeehaveReview = {
    review: Record<string, BeehaveReviewCategory>
    prompt_version: string
};

export type BeehaveReviewCategory = {
    score:number,
    suggestions:string[]
};
