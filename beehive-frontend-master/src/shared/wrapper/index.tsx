import { AppBar, LinearProgress, Toolbar } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { FunctionComponent, useCallback, useMemo, useState } from 'react';
import { useHistory } from 'react-router-dom';

import { useAppDispatch } from '../../hooks';
import { signOut } from '../../reducers/auth';
import { parseAccessTokenClaims, signedIn } from '../../services/auth';
import { HotkeysDialog, NavBar } from './components';

const useStyles = makeStyles({
    content: {
        display: 'flex',
        flexDirection: 'column',
        width: '100%',
        minHeight: '100vh',
        maxHeight: '100vh'
        //alignItems: 'center'
    },
    progressBar: {
        width: '100%'
    }
});

type Props = {
    loading: boolean;
    children?: React.ReactNode;
};

const Wrapper: FunctionComponent<Props> = ({ loading, children }: Props) => {
    const classes = useStyles();
    const dispatch = useAppDispatch();
    const history = useHistory();

    const [ hotkeysDialogOpen, setHotkeysDialogOpen ] = useState<boolean>(false);

    const handleSignOut = useCallback(
        () => {
            dispatch(
                signOut({})
            ).unwrap().finally(() => {
                history.push('/');
            });
        },
        [ dispatch, history, signOut ]
    );

    const handleOpenHotkeysDialog = useCallback(
        () => {
            setHotkeysDialogOpen(true);
        },
        []
    );

    const handleCloseHotkeysDialog = () => {
        setHotkeysDialogOpen(false);
    };

    const isAdmin = useMemo(() => {
        if (!signedIn()) {
            return false;
        }

        const claims = parseAccessTokenClaims();
        return claims.admin;
    }, [ signedIn, parseAccessTokenClaims ]);

    return (
        <div className={classes.content}>
            <AppBar position="fixed">
                <NavBar
                    signedIn={signedIn()}
                    onSignOut={handleSignOut}
                    onOpenHotkeysDialog={handleOpenHotkeysDialog}
                    isAdmin={isAdmin}
                />
                <LinearProgress
                    className={classes.progressBar}
                    color="secondary"
                    style={{ display: loading ? 'block' : 'none' }}
                />
            </AppBar>

            {/*
                just a trick to prevent content from being rednered behind the appbar
                (see https://material-ui.com/components/app-bar/#fixed-placement)
            */}
            <Toolbar />

            {children}

            <HotkeysDialog
                dialogOpen={hotkeysDialogOpen}
                onDialogClose={handleCloseHotkeysDialog}
            />
        </div>
    );
};

export default Wrapper;
