import { Task, TaskType } from './task';
import { WorkItem, WorkRecord } from './work';

/* dashboart types are extended normal types with fields only viewable to admins */

export type DashboardWorkItem = WorkItem & {
    workRecordsCount: number;
    workRecordsTotalDurationSeconds: number;
    workerId?: string;
};

export type DashboardWorkRecord = WorkRecord & {
    userId: string;
};

export type DashboardTask = Task & {
    delegatingUserId: string;
    taskType: TaskType;
    invalidCode: string;
    invalidDescription: string;
    feedback: string;
};

export type DashboardCommunityMember = {
    userId: string;
    email: string;
    name: string;
    github: string;
    trello: string;
    upwork: string;
    admin: boolean;
    availabilityWeeklyHours: number;
    tags: string[];
    skills: string[];
};

export type DashboardHoneycomb = {
    id: string;
    name: string;
    description: string;
    version: string;
    packageDependencies: string[];
    honeycombDependencies: string[];
};

export type DashboardContributorsItem = {
    id: string;
    name: string;
    activeWork: string;
    numberOfReservedPendingWorks: string;
    numberOfWorksInReview: string;
    numberOfCompletedWorks: string;
    numberOfTotalWorks: string;
    numberOfCanceledWorks: string;
    numberOfSkippedWorks: string;
    skippedTotalWorksRatio: string;
    timeSinceLastEngagement: number;
    timeSinceLastWork: number;
    billableHoursAvailabilityRatio: string;
    averageBillable: string;
    weeklyAvailability: string;
    averageGrossWorkDuration: number;
    averageNetWorkDuration: number;
    averageWorkPrice: number;
    averageIterationsPerTask: string;
    hourlyRate: string;
};

export type DashboardContributorHistoryItem = {
    id: number;
    workId: number;
    work: WorkItem;
    startTimeEpochMs: number;
    durationSeconds: number;
    solutionFeedback: string;
    ratings: [];
    outcome: string;
};
