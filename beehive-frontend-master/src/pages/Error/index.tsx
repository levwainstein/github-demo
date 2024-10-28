import { Button, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import RefreshIcon from '@material-ui/icons/Refresh';
import { FunctionComponent } from 'react';
import { useHistory } from 'react-router-dom';

import { ReportBug, Wrapper } from '../../shared';

const useStyles = makeStyles({
    content: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        flexGrow: 1
    }
});

type Props = Record<string, never>;

const Error: FunctionComponent<Props> = ({}: Props) => {
    const classes = useStyles();
    const history = useHistory();

    return (
        <Wrapper loading={false}>
            <div className={classes.content}>
                <Typography variant="h4" component="h4">
                    Oops, not sure what happened here
                </Typography>
                <Typography variant="h6" component="h6">
                    You can try again in a couple minutes
                </Typography><br />
                <Button
                    color="secondary"
                    startIcon={<RefreshIcon />}
                    onClick={() => {
                        history.push('/');
                    }}
                >
                    Or go back to the main page
                </Button>
            </div>

            <ReportBug />
        </Wrapper>
    );
};

export default Error;
