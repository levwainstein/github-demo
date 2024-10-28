export type ReviewPropsTypes = {
    name: string;
    rating: 1 | 2 | 3 | 4 | 5;
    feedback: string[];
};

export type BeehaveReviewProps = {
    code_quality_improvements: string[];
    code_quality_score: 1 | 2 | 3 | 4 | 5;
    documentation_improvements: string[];
    documentation_score: 1 | 2 | 3 | 4 | 5;
    functionality_improvements: string[];
    functionality_score: 1 | 2 | 3 | 4 | 5;
    test_coverage_improvements: string[];
    test_coverage_score: 1 | 2 | 3 | 4 | 5;
};

export enum ContributorWorkSteps {
    TaskAccept = 'TASK_ACCEPT',
    AnalyzePullRequest = 'ANALYZE_PULL_REQUEST',
    SubmitPullRequest = 'SUBMIT_PULL_REQUEST', 
    DescriptionFeedback = 'DESCRIPTION_FEEDBACK',
    Done = 'DONE',
}
