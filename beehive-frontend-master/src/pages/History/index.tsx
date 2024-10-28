import { FC } from 'react';

import { HistorySelectors } from '../../reducers/history';
import { Wrapper } from '../../shared';
import {
    WorkCompleted
} from './components';
import { TabPanel } from './helpers';
import { Container } from './styled';

const History: FC = () => {
    const { historyLoading } = HistorySelectors();
    return (
        <Wrapper loading={historyLoading}>
            <Container>
                <TabPanel value={1} index={1} key={1}>
                    <WorkCompleted/>
                </TabPanel>
            </Container>
        </Wrapper>
    );
};

export default History;
