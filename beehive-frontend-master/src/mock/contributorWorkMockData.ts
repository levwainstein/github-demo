
import { ReviewPropsTypes } from '../types/contributorWork';

export const mockReviews: ReviewPropsTypes[] = [
    {
        name: 'Test coverage',
        rating: 2,
        feedback: [
            'The code seems to be handling the functionality as described in the work.',
            'There is no error handling for the case when the "store" parameter is not provided in the request.',
            'The code does not seem to handle the case when the "sku" parameter is provided in the request but not used in the function. It would be better to handle these cases to avoid potential issues.'
        ]
    },
    {
        name: 'Code quality',
        rating: 2,
        feedback: [
            'The new functions and routes added in this PR are not documented.',
            'It would be helpful to add docstrings explaining what each function does, what parameters it expects, and what it returns.'
        ]
    },
    {
        name: 'Documentation',
        rating: 2,
        feedback: [
            'There are no tests included in this PR.',
            'It would be good to add tests that check if the new endpoint works as expected, and if the data manipulation operations produce the correct results.',
            'The tests should cover different scenarios, such as when all, some, or none of the optional parameters are provided in the request.'
        ]
    }
];
