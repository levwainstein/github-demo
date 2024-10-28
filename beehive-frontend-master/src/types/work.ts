import { BeehaveReview } from '../types/beehaveReview';
import { RatingSubject } from './rating';
import { Task, TaskTypeClassification } from './task';

export enum WorkType {
    CREATE_FUNCTION = 1,
    UPDATE_FUNCTION = 2,
    DESCRIBE_FUNCTION = 3,
    REVIEW_TASK = 4,
    OPEN_TASK = 5,
    CREATE_REACT_COMPONENT = 6,
    UPDATE_REACT_COMPONENT = 7,
    CHECK_REUSABILITY = 8,
    CUCKOO_CODING = 9,
    CUCKOO_ITERATION = 10,
    CUCKOO_COMMUNITY_REVIEW = 11
}

export enum WorkStatus {
    AVAILABLE = 1,
    UNAVAILABLE = 2,
    COMPLETE = 3,
    PENDING_PACKAGE = 4
}

export enum WorkReviewStatus {
    INADEQUATE = 1,
    REQUIRES_MODIFICATION = 2,
    ADEQUATE = 3
}

export enum WorkOutcome {
    REQUESTED_PACKAGE = 1,
    FEEDBACK = 2,
    SOLVED = 3,
    CANCELLED = 4,
    SKIPPED = 5,
    TASK_CANCELLED = 6
}

export const workMaxDurationMs = 10*60*60*1000;

export const isReviewWorkItem = (workType: WorkType): boolean => {
    return [
        WorkType.CUCKOO_COMMUNITY_REVIEW
    ].indexOf(workType) > -1;
};

export type TaskContext = {
    id: string;
    file: string;
    entity: string;
    potentialUse: string;
};

export type WorkItem = {
    id: number;
    created: string;
    taskId: string;
    taskType?: TaskTypeClassification;
    title?: string;
    repoName?: string;
    repoUrl?: string;
    branchName?: string; 
    skills: [string];
    context?: TaskContext[];
    task: Task;
    status: WorkStatus;
    workType: WorkType;
    priority: number;
    description: string;
    workInput: {[key: string]: any};
};

export type WorkRecord = {
    id: number;
    workId: number;
    work: WorkItem;
    startTimeEpochMs: number;
    durationSeconds: number;
    solutionFeedback: string;
    ratingSubjects: RatingSubject[];
    ratingAuthorizationCode: string;
    latestBeehaveReview: BeehaveReview;
};
