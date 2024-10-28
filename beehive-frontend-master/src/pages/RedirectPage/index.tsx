import { makeStyles } from '@material-ui/core/styles';
import { Box, Typography } from '@mui/material';
import clsx from 'clsx';
import { FunctionComponent, useEffect, useState } from 'react';
import { useSearchParam } from 'react-use';

import { useAppDispatch } from '../../hooks';
import { reviewWork, WorkSelectors } from '../../reducers/work';
import { ReportBug, Wrapper } from '../../shared';

const useStyles = makeStyles((theme) => ({
    root: {
        backgroundColor: theme.palette.background.default,
        width: '100vw',
        height: '100vh'
    },
    container: {
        width: '90%',
        marginTop: theme.spacing(3),
        marginLeft: 'auto',
        marginRight: 'auto'
    },
    title: {
        textAlign: 'center',
        color: '#E9E9EA'
    },
    error: {
        color: theme.palette.error.dark
    }
}));

type Props = Record<string, never>;

const RedirectPage: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();
    const { workRecordSolutionUrl, workActionError } = WorkSelectors();

    const workRecordIdSearchParam = useSearchParam('workRecordId');
    const workRecordId = workRecordIdSearchParam ? parseInt(workRecordIdSearchParam) : null;

    const [ error, setError ] = useState<boolean>(false);
 
    useEffect(() => {
        // load redirect url on mount
        if (!workRecordId) {
            setError(true);
            return;
        }
        dispatch(
            reviewWork({ workRecordId })
        ).catch(() => {
            setError(true);
        });
    }, []);

    useEffect(() => {
        if (workRecordSolutionUrl) {
            window.location.replace(workRecordSolutionUrl);
        }
    }, [ workRecordSolutionUrl, workActionError ]);

    return (
        <Wrapper loading={false}>
            <Box className={classes.root}>
                <Box className={classes.container}>
                    {error || workActionError ? (
                        <Typography
                            className={clsx(classes.title, classes.error)}
                            mb={3}
                            fontSize="1rem"
                            fontWeight={600}
                        >
                            { workActionError || 'An unknown error has occurred' }
                        </Typography>
                    ) : (
                        <>
                            <Typography
                                className={classes.title}
                                mb={3}
                                fontSize="1rem"
                                fontWeight={600}
                            >
                                Redirecting to url...
                            </Typography>
                        </>
                    )}
                </Box>
                <ReportBug />
            </Box>
        </Wrapper>
    );
};

export default RedirectPage;
