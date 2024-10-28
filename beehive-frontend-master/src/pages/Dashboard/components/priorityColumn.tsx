import { Button, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { AsyncThunk } from '@reduxjs/toolkit';
import { FunctionComponent, useCallback } from 'react';

import { useAppDispatch } from '../../../hooks';

const useStyles = makeStyles(() => {
    return {
        container: { display: 'flex', flexDirection: 'row', allignItems: 'center', justifyContent: 'center' },
        label: { flexGrow: 1, textAlign: 'center', alignSelf: 'center' }
    };
});

type Props = {
    row: any;
    value?: string;
    onUpdatePriority: AsyncThunk<any, {workId: number, priority: number}, Record<string, unknown>>;
};

const PriorityColumn: FunctionComponent<Props> = ({
    row,
    value,
    onUpdatePriority
}: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();

    const handlePlusClicked = useCallback((event) => {
        event.preventDefault();
        dispatch(onUpdatePriority({ workId: row.id, priority: Number(value) + 1 }));
    }, [ onUpdatePriority, row, value ]);

    const handleMinusClicked = useCallback((event) => {
        event.preventDefault();
        dispatch(onUpdatePriority({ workId: row.id, priority: Number(value) - 1 }));
    }, [ onUpdatePriority, row, value ]);

    return (
        <div className={classes.container}>
            <Typography color="textSecondary" className={classes.label}>
                {value}
            </Typography>
            <div>
                <Button color="primary" variant="text" onClick={(e) => {
                    handlePlusClicked(e);
                }}>
                +
                </Button>
                <Button color="primary" variant="text" onClick={(e) => {
                    handleMinusClicked(e);

                }}>
                -
                </Button>
            </div>
        </div>
    );
};

export default PriorityColumn;
