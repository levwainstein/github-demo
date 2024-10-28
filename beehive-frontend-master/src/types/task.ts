export enum TaskStatus {
    NEW = 1,
    PENDING = 2,
    PAUSED = 3,
    IN_PROCESS = 4,
    SOLVED = 5,
    ACCEPTED = 6,
    CANCELLED = 7,
    INVALID = 8,
    PENDING_CLASS_PARAMS = 9,
    PENDING_PACKAGE = 10,
    MODIFICATIONS_REQUESTED = 11
}

export enum TaskType {
    CREATE_FUNCTION = 1,
    UPDATE_FUNCTION = 2,
    DESCRIBE_FUNCTION = 3,
    REVIEW_TASK = 4,
    OPEN_TASK = 5,
    CREATE_REACT_COMPONENT = 6,
    UPDATE_REACT_COMPONENT = 7,
    CHECK_REUSABILITY = 8,
    CUCKOO = 9,
    CUCKOO_REVIEW = 10
}

export enum TaskTypeClassification {
    CREATE_COMPONENT = 'Create a component',
    MODIFY_COMPONENT = 'Modify/fix a component',
    CREATE_PAGE = 'Create a page/screen',
    MODIFY_PAGE = 'Modify/fix a page/screen',
    MODIFY_DESIGN = 'Change to match design',
    CREATE_ANIMATION = 'Creating an animation',
    CREATE_EVENT = 'Write events to Mixpanel/monitoring',
    CREATE_DATA_MODEL = 'Create/modify a data model',
    CREATE_ENDPOINT = 'Create/Modify an endpoint',
    CREATE_DJANGO_VIEW = 'Create a django view',
    MODIFY_DJANGO_VIEW = 'Modify/Fix a django view',
    CREATE_ALGORITHM = 'Write an algorithm / business logic',
    CREATE_SCRAPER = 'Scraping',
    CREATE_API_CONNECTOR = 'Connect a screen/component to an API/view/functionality',
    REFACTOR_CODE = 'Refactor existing code',
    CREATE_TEST_CASE = 'Write test cases',
    CREATE_AUTH = 'Authorization/Authentication',
    OTHER = 'Other',
    UNCERTAIN = 'Uncertain'
}

// Task type contains fields that are displayed in the account page (historic work records
// worked on by the logged in user)
export type Task = {
    id: string;
    functionName: string;
    status: TaskStatus;
};
