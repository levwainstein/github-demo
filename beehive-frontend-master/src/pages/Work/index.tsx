import { Snackbar } from '@material-ui/core';
import { FunctionComponent, useEffect, useState } from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { useSearchParam } from 'react-use';

import { useAppDispatch } from '../../hooks';
import {
    clearAvailableWorkError,
    loadAvailableWork,
    WorkSelectors
} from '../../reducers/work';
import { Wrapper } from '../../shared';
import { EmptyView, WorkView } from './components';

type Props = Record<string, never>;

const Work: FunctionComponent<Props> = ({}: Props) => {
    const dispatch = useAppDispatch();
    const history = useHistory();
    const location = useLocation();

    const workIdSearchParam = useSearchParam('workId');
    const specificWorkId = workIdSearchParam ? parseInt(workIdSearchParam) : undefined;

    const { work, workLoading, workError, workFetched } = WorkSelectors();

    const [ specificWorkError, setSpecificWorkError ] = useState<string | null>(null);

    useEffect(() => {
        // load initial work item
        dispatch(
            loadAvailableWork({ specificWorkId })
        ).unwrap().then((payload: any) => {
            // if a specific work item was requested and no work item was fetched
            // or a different item was fetched let the user know
            if (specificWorkId &&
                (payload.work === null || payload.work.id !== specificWorkId)) {
                if (!!payload.workRecord) {
                    setSpecificWorkError(
                        'You have in-process work. Finish or cancel it to access other work'
                    );
                } else {
                    setSpecificWorkError('The requested work item is currently unavailable');
                }
            }
        });
    }, []);

    useEffect(() => {
        if (specificWorkId && work && work.id !== specificWorkId) {
            // clear query params (resets specificWorkId)
            history.push(location.pathname);
        }
    }, [ specificWorkId, work ]);

    return (
        <Wrapper loading={workLoading}>
            {work !== null ? (
                <WorkView work={work} />
            ) : (
                workFetched && (
                    <>
                        <EmptyView />
                        <Snackbar
                            open={!!workError}
                            autoHideDuration={6000}
                            onClose={() => dispatch(clearAvailableWorkError())}
                            message="Woops! Not sure what happened there... Please try again"
                        />
                    </>
                )
            )}
            <Snackbar
                open={!!specificWorkError}
                autoHideDuration={6000}
                onClose={() => setSpecificWorkError(null)}
                message={specificWorkError}
            />
        </Wrapper>
    );
};

export default Work;
