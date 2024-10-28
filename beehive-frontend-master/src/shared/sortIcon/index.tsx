import ArrowDownwardIcon from '@material-ui/icons/ArrowDownward';
import ArrowUpwardIcon from '@material-ui/icons/ArrowUpward';
import { FunctionComponent } from 'react';

import { sortIconStyles } from './styles';

const SortIcon: FunctionComponent<{ sort: string }> = ({ sort }) => {
    if (sort === 'desc') {
        return <ArrowDownwardIcon style={sortIconStyles}/>;
    } else if (sort === 'asc') {
        return <ArrowUpwardIcon style={sortIconStyles}/>;
    } else {
        return <></>;
    }
};

export default SortIcon;
