import { FC } from 'react';

import TaskCompletedImageSource from '../../../../assets/images/task-completed.png';
import { Container, TaskCompletedImage } from './styled';

type Props = Record<string, never>;

const TaskCompleted: FC<Props> = ({}: Props) => {
    return (
        <Container>
            <img src={TaskCompletedImageSource} style={TaskCompletedImage} />
        </Container>
    );
};

export default TaskCompleted;
