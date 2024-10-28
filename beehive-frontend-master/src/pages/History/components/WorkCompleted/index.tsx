import { FC, useEffect } from 'react';

import { useAppDispatch } from '../../../../hooks';
import { HistorySelectors, loadWorkHistory } from '../../../../reducers/history';
import Table from '../Table';

const WorkCompleted: FC = () => {
    const { completedWork } = HistorySelectors();
    const dispatch = useAppDispatch();

    useEffect(() => {
        dispatch(loadWorkHistory({}));
    }, []);

    return (
        <Table
            title="Work completed"
            subtitle="The following is the list of work completed by you in the last 30 days. Tap on each item to see the feedback you got from your reviewer."
            allRows={completedWork || []}
        />
    );
};

export default WorkCompleted;
