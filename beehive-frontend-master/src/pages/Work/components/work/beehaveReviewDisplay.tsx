import { Box, List, ListItem } from '@material-ui/core';
import { Grid, Typography } from '@material-ui/core';
import { makeStyles, Theme } from '@material-ui/core/styles';
import { Rating as MUIRating } from '@material-ui/lab';
import { Stack } from '@mui/material';
import { FunctionComponent } from 'react';

import { BeehaveReview } from '../../../../types/beehaveReview';

const useStyles = makeStyles<Theme>(theme => {
    return {
        root: {
            display: 'inline-block',
            height: '100%',
            width: '100%',
            backgroundColor: theme.palette.primary.dark,
            paddingLeft: theme.spacing(2),
            paddingBottom: theme.spacing(2)
        },
        container: {
            borderRadius: '5px',
            color: theme.palette.text.primary,
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
        },
        detailsContainer: {
            display: 'flex',
            flexDirection: 'column',
            height: '100%'
        },
        descriptionTitleContainer: {
            display: 'flex',
            flexDirection: 'row',
            gap: 10,
            paddingTop: theme.spacing(2)
        },
        gridContainer: {
            height: '100%'
        },
        markdownWrapper: {
            display: 'inline-block',
            textAlign: 'start',
            width: '100%',
            overflowY: 'scroll',
            flexGrow: 1,
            flexBasis: 0
        },
        markdown: {
            '& p > a': {
                color: theme.palette.secondary.main
            },
            '& p > a:visited': {
                color: theme.palette.secondary.dark
            }
        },
        warning: {
            color: 'red',
            paddingBottom: 7,
            textAlign: 'start'
        },
        normal: {
            color: 'white',
            paddingBottom: 7,
            textAlign: 'start'
        },
        actions: {
            display: 'flex',
            flexDirection: 'column',
            border: '1px solid #31333E',
            borderRadius: '5px',
            padding: theme.spacing(2),
            [theme.breakpoints.down('sm')]: {
                marginRight: theme.spacing(1),
                padding: theme.spacing(1)
            }
        },
        priority: {
            position: 'relative',
            left: '50%',
            transform: 'translateX(-50%)',
            color: 'white',
            backgroundColor: 'red',
            padding: 2,
            paddingLeft: 10,
            paddingRight: 10,
            textAlign: 'center',
            width: 'fit-content',
            borderRadius: '10px',
            marginBottom: 5
        },
        externalContainer: {
            marginTop: theme.spacing(2)
        },
        reviewScoreText: {
            color: theme.palette.secondary.main,
            paddingLeft: theme.spacing(1)
        },
        improvementsList: {
            listStyleType: 'disc',
            listStylePosition: 'inside'
        },
        improvementListItem: {
            display: 'list-item',
            opacity: 0.5,
            fontSize: theme.typography.pxToRem(15),
            paddingTop: theme.spacing(0.5),
            paddingBottom: theme.spacing(0.5)
        },
        categoryTitleContainer: {
            fontSize: theme.typography.pxToRem(15),
            paddingBottom: theme.spacing(1)
        },
        descriptionText: {
            opacity: 0.5
        }
    };
});

type Props = {
    workId: number;
    reviewResult: BeehaveReview;
};

const rating2label = [
    'Poor',
    'Below Average',
    'Average',
    'Good',
    'Excellent'
];

const categoryOrder = [
    'Functionality', 
    'Code Quality', 
    'Documentation', 
    'Test Coverage'
];

const BeehaveReviewDisplay: FunctionComponent<Props> = ({
    workId,
    reviewResult,
    ...other
}: Props) => {
    const classes = useStyles();

    const pollinatorBackwordsSupport = supportBackwordsPollinator(reviewResult);

    return (
        <Box key={`beehave-reviewe-display-${workId}`}
            className={classes.root}
            {...other}
        >
            <Box className={classes.container}>
                <Box className={classes.descriptionTitleContainer}>
                </Box>
                <Box>
                
                </Box>
                <Stack direction="column" spacing={2}>
                    <Box className={classes.detailsContainer}>
                        <Typography variant="h6" component="h1">
                            Automatic PR Feedback
                        </Typography>
                        <Typography variant="body2" component="p" className={classes.descriptionText}>
                        We recommend you improve your solution to get better solution ratings. Note that the feedback below is auto-generated, if you disagree with any feedback, you may ignore it for our human reviewers to check.
                        </Typography>
                    </Box>
                    {categoryOrder.map((categoryName) => {
                        const categoryData = pollinatorBackwordsSupport[categoryName];
                        return (<Stack direction="column" key={`container-${categoryName}`}>
                            <Grid xs={6} container direction="row" className={classes.categoryTitleContainer}>
                                <Grid item xs={3}>{categoryName}</Grid>
                                <Grid item xs={2}>
                                    <MUIRating
                                        className={classes.rating}
                                        size="small"
                                        max={5}
                                        value={categoryData.score}
                                        name="rating"
                                        readOnly={true}
                                    />
                                </Grid>
                                <Grid item xs={3} className={classes.reviewScoreText}>
                                    {rating2label[categoryData.score - 1]}
                                </Grid>
                            </Grid>
                            <List disablePadding={true} className={classes.improvementsList}>
                                {categoryData.suggestions.map((suggestion, i) => 
                                    (<ListItem key={`suggestion-${i}`} className={classes.improvementListItem}>
                                        {suggestion}
                                    </ListItem>)
                                )
                                }
                            </List>
                        </Stack>);
                    })}
                </Stack>
            </Box>
        </Box>
    );
};

export default BeehaveReviewDisplay;

function supportBackwordsPollinator(reviewResult: BeehaveReview) {

    // if the result can be parsed return it as is
    if (reviewResult[categoryOrder[0]]) {
        return reviewResult;
    }

    // other wise thranslate it from the new format to the format this component is expecting
    const scoreTranslationMap = {
        'Functionality': 'functionality_score',
        'Code Quality': 'code_quality_score',
        'Documentation': 'documentation_score',
        'Test Coverage': 'test_coverage_score'
    };

    const suggestionsTranslationMap = {
        'Functionality': 'functionality_improvements',
        'Code Quality': 'code_quality_improvements',
        'Documentation': 'documentation_improvements',
        'Test Coverage': 'test_coverage_improvements'
    };

    const translated = Object.fromEntries(categoryOrder.map((name) => ([ name, {
        score: reviewResult[scoreTranslationMap[name]],
        suggestions: reviewResult[suggestionsTranslationMap[name]]
    } ])));

    return translated;
}

