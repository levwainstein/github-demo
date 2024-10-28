import { RatingSubject, UserRating } from '../types/rating';
import { WorkReviewStatus } from '../types/work';
import { accessToken as authAccessToken, refreshToken as authRefreshToken } from './auth';

const BASE_URL = `${process.env.REACT_APP_BACKEND_URL || ''}/`;

let controller: AbortController;
let signal: AbortSignal;

function _resetAbortController() {
    controller = new AbortController();
    signal = controller.signal;
}

// init controller and signal
_resetAbortController();

export function signUp(
    email: string,
    password: string,
    code: string,
    client: string,
    firstName?: string,
    lastName?: string,
    githubUser?: string,
    trelloUser?: string,
    upworkUser?: string,
    availabilityWeeklyHours?: number,
    pricePerHour?: number
): Promise<any> {
    return _callAPI('backend/api/v1/signup', false, 'POST', {
        email,
        password,
        code,
        client,
        firstName,
        lastName,
        githubUser,
        trelloUser,
        upworkUser,
        availabilityWeeklyHours,
        pricePerHour
    });
}

export function signIn(email: string, password: string): Promise<any> {
    return _callAPI('backend/api/v1/signin', false, 'POST', { email, password });
}

export function signOut(): Promise<any> {
    return _callAPI('backend/api/v1/signout', true, 'POST');
}

export function refreshToken(): Promise<any> {
    return _callAPI('backend/api/v1/auth/refresh', false, 'POST', undefined, true);
}

export function activateUser(activationToken: string): Promise<any> {
    return _callAPI('backend/api/v1/auth/activate', false, 'POST', { activationToken });
}

export function resendUserActivationEmail(unactivatedAccessToken: string): Promise<any> {
    return _callAPI('backend/api/v1/auth/resend', true, 'POST', undefined, false, false, unactivatedAccessToken);
}

export function resetPassword(email: string): Promise<any> {
    return _callAPI('backend/api/v1/auth/reset', false, 'POST', { email });
}

export function resetPasswordChange(code: string, newPassword?: string): Promise<any> {
    return _callAPI('backend/api/v1/auth/reset/change', false, 'POST', { code, newPassword });
}

export function fetchAvailableWork(currentWorkId?: number): Promise<any> {
    return _callAuthenticatedAPI(
        'backend/api/v1/work/available' + (!!currentWorkId ? `?currentWorkId=${currentWorkId}` : '')
    );
}

export function fetchSpecificWork(workId: number): Promise<any> {
    return _callAuthenticatedAPI(`backend/api/v1/work/available?specificWorkId=${workId}`);
}

export function startWork(
    workId: number,
    startTimeEpochMs: number,
    tzName: string
): Promise<any> {
    return _callAuthenticatedAPI('backend/api/v1/work/start', 'POST', { workId, startTimeEpochMs, tzName });
}

export function skipWork(
    workId: number,
    startTimeEpochMs: number,
    tzName: string
): Promise<any> {
    return _callAuthenticatedAPI('backend/api/v1/work/skip', 'POST', { workId, startTimeEpochMs, tzName });
}

export function checkpointWork(
    workId: number,
    durationSeconds: number
): Promise<any> {
    return _callAuthenticatedAPI(
        'backend/api/v1/work/checkpoint', 'POST', { workId, durationSeconds }
    );
}

export function finishWork(
    workId: number,
    durationSeconds: number,
    feedback?: string,
    reviewStatus?: WorkReviewStatus,
    reviewFeedback?: string,
    solutionUrl?: string
): Promise<any> {
    // undefined params (feedback / reviewStatus / ...)
    // will not be sent to the backend
    return _callAuthenticatedAPI(
        'backend/api/v1/work/finish',
        'POST',
        {
            workId,
            durationSeconds,
            feedback,
            reviewStatus,
            reviewFeedback,
            solutionUrl
        }
    );
}

export function analyzeWork(
    workId: number,
    solutionUrl: string
): Promise<any> {
    return _callAuthenticatedAPI(
        'backend/api/v1/work/analyze',
        'POST',
        {
            workId,
            solutionUrl
        }
    );
}

export function fetchWorkHistory(): Promise<any> {
    return _callAuthenticatedAPI('backend/api/v1/work/history');
}

export function fetchDashboardActiveWork(page: number, resultsPerPage: number): Promise<any> {
    return _callAuthenticatedAPI(
        `backend/api/v1/stats/work/active?page=${page}&resultsPerPage=${resultsPerPage}`
    );
}

export function fetchDashboardPendingWork(page: number, resultsPerPage: number): Promise<any> {
    return _callAuthenticatedAPI(
        `backend/api/v1/stats/work/pending?page=${page}&resultsPerPage=${resultsPerPage}`
    );
}

export function fetchDashboardCompletedWork(
    page: number,
    resultsPerPage: number,
    filter?: {[key: string]: string}
): Promise<any> {
    let endpointUrl = `backend/api/v1/stats/work/completed?page=${page}&resultsPerPage=${resultsPerPage}`;

    if (filter) {
        for (const [ field, value ] of Object.entries(filter)) {
            endpointUrl = endpointUrl.concat(`&filter=${field}=${value}`);
        }
    }

    return _callAuthenticatedAPI(endpointUrl);
}

export function reserveWork(workId: number, userId: string): Promise<any> {
    return _callAuthenticatedAPI(`backend/api/v1/stats/work/${workId}/reserve/${userId}`, 'POST');
}

export function dismissWorkReservation(workId: number, userId: string): Promise<any> {
    return _callAuthenticatedAPI(`backend/api/v1/stats/work/${workId}/reserve/${userId}`, 'DELETE');
}

export function prohibitWork(workId: number, userId: string): Promise<any> {
    return _callAuthenticatedAPI(`backend/api/v1/stats/work/${workId}/prohibit/${userId}`);
}

export function dismissWorkProhibition(workId: number, userId: string): Promise<any> {
    return _callAuthenticatedAPI(`backend/api/v1/stats/work/${workId}/prohibit/${userId}`, 'DELETE');
}

export function fetchDashboardInvalidTasks(page: number, resultsPerPage: number): Promise<any> {
    return _callAuthenticatedAPI(
        `backend/api/v1/stats/task/invalid?page=${page}&resultsPerPage=${resultsPerPage}`
    );
}

export function fetchDashboardCommunity(page: number, resultsPerPage: number): Promise<any> {
    return _callAuthenticatedAPI(
        `backend/api/v1/stats/user?page=${page}&resultsPerPage=${resultsPerPage}`
    );
}

export function fetchDashboardHoneycombs(page: number, resultsPerPage: number): Promise<any> {
    return _callAuthenticatedAPI(
        `backend/api/v1/stats/honeycomb?page=${page}&resultsPerPage=${resultsPerPage}`
    );
}

export function fetchDashboardContributors(
    page: number,
    resultsPerPage: number,
    filter?: {[key: string]: string}
): Promise<any> {
    let endpointUrl = `backend/api/v1/stats/contributors?page=${page}&resultsPerPage=${resultsPerPage}`;

    if (filter) {
        for (const [ field, value ] of Object.entries(filter)) {
            endpointUrl = endpointUrl.concat(`&filter=${field}=${value}`);
        }
    }

    return _callAuthenticatedAPI(endpointUrl);
}

export function fetchDashboardContributorHistory(
    userId: string, 
    page: number,
    resultsPerPage: number
): Promise<any> {
    return _callAuthenticatedAPI(
        `backend/api/v1/stats/contributor/${userId}?page=${page}&resultsPerPage=${resultsPerPage}`
    );
}

export function sendBugReport(taskId: string, details: string): Promise<any> {
    return _callAuthenticatedAPI('backend/api/v1/general/report-bug', 'POST', { taskId, details, source: 'frontend' });
}

export function fetchUserProfile(): Promise<any> {
    return _callAuthenticatedAPI('backend/api/v1/user/profile');
}

export function updateUserProfile(
    email?: string,
    firstName?: string,
    lastName?: string,
    githubUser?: string,
    trelloUser?: string,
    upworkUser?: string,
    availabilityWeeklyHours?: number,
    pricePerHour?: number,
    skills?: string[]
): Promise<any> {
    return _callAuthenticatedAPI(
        'backend/api/v1/user/profile',
        'PUT',
        {
            email,
            firstName,
            lastName,
            githubUser,
            trelloUser,
            upworkUser,
            availabilityWeeklyHours,
            pricePerHour,
            skills
        }
    );
}

export function updateWorkPriority(
    workId?: number,
    priority?: number
): Promise<any> {
    return _callAuthenticatedAPI(
        `backend/api/v1/backoffice/work/priority/${workId}`,
        'PUT',
        {
            priority
        }
    );
}

export function fetchAvailableSkills(): Promise<any> {
    return _callAuthenticatedAPI('backend/api/v1/skill');
}

export function reviewWork(
    workRecordId: number
): Promise<any> {
    return _callAuthenticatedAPI(
        'backend/api/v1/work/review', 'POST', { workRecordId }
    );
}

// Praesepe rating api

export function updateRating(
    code: string, subject: RatingSubject, userRating: UserRating
): Promise<any> {
    const score = userRating.score;
    const text = userRating.feedback;
    return _callAuthenticatedAPI(
        'praesepe/api/v1/rating',
        'POST',
        {
            code,
            subject,
            score,
            text
        },
        undefined,
        undefined
    );
}

// Hive infer api

export function updateWorkTypeClassification(
    input: string, predictedOutput: string, correctedOutput: string
): Promise<any> {
    return _callAuthenticatedAPI(
        'pollinator/task-type/api/v1/correct',
        'POST',
        {
            input,
            predictedOutput,
            correctedOutput
        },
        undefined,
        undefined
    );
}

type MethodType = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'OPTIONS' | 'HEAD';

function _callAuthenticatedAPI(
    endpoint: string,
    method: MethodType = 'GET',
    body?: {[key: string]: any},
    refresh: boolean = false,
    abortable: boolean = false
): Promise<any> {
    return _callAPI(endpoint, true, method, body, refresh, abortable, undefined)
        .catch((error) => {
            // if this is not an unauthorized error cascade the failure right away
            if (error.status !== 401) {
                return Promise.reject(error);
            }

            // try refreshing the token and calling the api once again
            return authRefreshToken().then(() =>
                _callAPI(endpoint, true, method, body, refresh, abortable, undefined)
            );
        });
}

function _callAPI(
    endpoint: string,
    authenticated: boolean = false,
    method: MethodType = 'GET',
    body?: {[key: string]: any},
    refresh: boolean = false,
    abortable: boolean = false,
    overrideToken?: string
): Promise<any> {
    // Get the current user
    const accessToken = overrideToken || authAccessToken();
    const refreshToken = localStorage.getItem('refresh_token');

    // The header is assumed to be a JSON
    const config = {
        headers: {}
    };

    // Adding a method if needed (default is get)
    if (method) {
        config['method'] = method;
    }

    // Adding a body to the API request
    if (body) {
        config['headers'] = { 'Content-Type': 'application/json' };
        config['body'] = JSON.stringify(body);
    }

    // Adding authentication token for requests that require authentication
    if (authenticated && accessToken) {
        config['headers']['Authorization'] = `Bearer ${accessToken}`;
    }

    // Adding a refresh token is needs a token refresher...
    if (refresh && refreshToken) {
        config['headers']['Authorization'] = `Bearer ${refreshToken}`;
    }

    if (abortable) {
        config['signal'] = signal;
    }

    // And finally calling the request
    console.log(`calling ${endpoint}`);

    return fetch(BASE_URL + endpoint, config)
        .catch(err => {
            console.log(err);

            // reject with unknown error, but aborting an abortable request should be
            // distinguishable as it's not necessarily an erroneous path
            return Promise.reject({
                status: -1,
                aborted: abortable && err.name === 'AbortError'
            });
        })
        .then(response => response.json()
            .catch(err => {
                console.log(err);
                return Promise.reject({ status: response.status });
            })
            .then(responseBody => {
                if (response.ok && responseBody.status === 'ok') {
                    return Promise.resolve(responseBody.data);
                } else {
                    // error and description may not be available
                    return Promise.reject({
                        status: response.status,
                        error: responseBody.error,
                        description: responseBody.description
                    });
                }
            })
        );
}
