import { Button, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import RefreshIcon from '@material-ui/icons/Refresh';
import { FunctionComponent } from 'react';

import { useAppDispatch, useNoDefaultHotkeys } from '../../../hooks';
import { loadAvailableWork } from '../../../reducers/work';

const useStyles = makeStyles((theme) => {
    return {
        root: {
            display: 'flex',
            backgroundColor: theme.palette.background.default,
            flexDirection: 'column',
            width: '100%',
            alignItems: 'center',
            justifyContent: 'center',
            flexGrow: 1
        },
        coffee: {
            width: '300px',
            marginBottom: '20px'
        },
        text: {
            color: 'white',
            textAlign: 'center',
            alignItems: 'center'
        }
    };
});

type Props = Record<string, never>;

const EmptyView: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();

    const handleRefreshClick = () => {
        dispatch(loadAvailableWork({}));
    };

    // register hotkey to refresh work
    useNoDefaultHotkeys('ctrl + s', handleRefreshClick);

    return (
        <div className={classes.root}>
            <img className={classes.coffee} alt="Sad bee" src="bee.png" />
            <Typography variant="h4" component="h4" className={classes.text}>
                We&#39;re out of tasks
            </Typography>
            <Typography variant="h6" component="h6" className={classes.text}>
                Our team was notified and<br />will add tasks as soon as possible. <br /><br />Please check again later.
            </Typography><br />
            <Button
                color="secondary"
                startIcon={<RefreshIcon />}
                onClick={handleRefreshClick}
            >
                Refresh
            </Button>
        </div>
    );
};

export default EmptyView;
