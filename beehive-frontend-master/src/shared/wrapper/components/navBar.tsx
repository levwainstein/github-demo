import {
    Box,
    Button,
    Divider,
    IconButton,
    Link as MUILink,
    Menu,
    MenuItem,
    Toolbar,
    Tooltip
} from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import AccountCircleIcon from '@material-ui/icons/AccountCircle';
import DashboardIcon from '@material-ui/icons/Dashboard';
import HelpIcon from '@material-ui/icons/Help';
import KeyboardIcon from '@material-ui/icons/Keyboard';
import clsx from 'clsx';
import { FunctionComponent, useState } from 'react';
import { NavLink as Link } from 'react-router-dom';

import { colors } from '../../../theme';
import Logo from './logo';

const useStyles = makeStyles(theme => {
    return {
        toolbar: {
            display: 'flex',
            justifyContent: 'space-between',
            background: theme.palette.primary.dark
        },
        toolbarSide: {
            flex: 1
        },
        toolbarEnd: {
            display: 'flex',
            flexDirection: 'row',
            justifyContent: 'end'
        },
        navBarButton: {
            color: theme.palette.text.primary,
            margin: '0px 10px 0px 0px'
        },
        helpButton: {
            margin: '0px 10px 0px 0px'
        },
        helpIcon: {
            color: theme.palette.text.primary,
            borderRadius: '50%'
        },
        menuItem: {
            color: theme.palette.text.secondary
        },
        historyButton: {
            color: 'white',
            backgroundColor: colors.chineseGold,
            '&:hover': {
                backgroundColor: colors.chineseGold,
                color: colors.black87
            },
            borderRadius: 30
        }
    };
});

type Props = {
    signedIn: boolean;
    onSignOut: () => void;
    onOpenHotkeysDialog: () => void;
    isAdmin: boolean;
};

const NavBar: FunctionComponent<Props> = ({
    signedIn,
    onSignOut,
    onOpenHotkeysDialog,
    isAdmin
}: Props) => {
    const classes = useStyles();

    const [ anchorEl, setAnchorEl ] = useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);
  
    const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };
  
    const handleClose = () => {
        setAnchorEl(null);
    };

    return (
        <Toolbar className={classes.toolbar}>
            <Box className={classes.toolbarSide}>
                <Link to="/">
                    <Logo test-id="logo-image" />
                </Link>
            </Box>
            {signedIn && 
            <Box>
                <Link to="/history">
                    <Button
                        className={classes.historyButton}
                        variant="contained"
                        type="submit"
                        disabled={!signedIn}
                    >
                        History
                    </Button>
                </Link>
            </Box>
            }
            {signedIn && (
                <Box className={clsx(classes.toolbarSide, classes.toolbarEnd)}>
                    <MUILink href="https://docs.caas.ai/community">
                        <Tooltip
                            title="Help"
                        >
                            <IconButton
                                aria-label="help"
                                classes={{
                                    root: classes.helpButton
                                }}
                            >
                                <HelpIcon className={classes.helpIcon}/>
                            </IconButton>
                        </Tooltip>
                    </MUILink>
                    {isAdmin && (
                        <Link to="/dashboard">
                            <Tooltip
                                title="Admin dashboard"
                            >
                                <IconButton
                                    classes={{
                                        root: classes.navBarButton
                                    }}
                                    aria-label="admin-dashboard"
                                >
                                    <DashboardIcon />
                                </IconButton>
                            </Tooltip>
                        </Link>
                    )}
                    <Tooltip
                        title="Keyboard shortcuts"
                    >
                        <IconButton
                            classes={{
                                root: classes.navBarButton
                            }}
                            aria-label="keyboard-shortcuts"
                            onClick={onOpenHotkeysDialog}
                        >
                            <KeyboardIcon />
                        </IconButton>
                    </Tooltip>

                    <Link to="#">
                        <IconButton
                            aria-label="my-account"
                            aria-controls="menu-appbar"
                            aria-haspopup="true"
                            onClick={handleMenu}
                            classes={{
                                root: classes.navBarButton
                            }}
                        >
                            <AccountCircleIcon />
                        </IconButton>
                        <Menu
                            id="menu-appbar"
                            anchorEl={anchorEl}
                            getContentAnchorEl={null}
                            anchorOrigin={{
                                vertical: 'bottom',
                                horizontal: 'right'
                            }}
                            keepMounted
                            transformOrigin={{
                                vertical: 'top',
                                horizontal: 'right'
                            }}
                            open={open}
                            onClose={handleClose}
                        >
                            <MenuItem
                                className={classes.menuItem}
                                component={Link}
                                to="/profile"
                            >
                                Settings
                            </MenuItem>
                            <MenuItem
                                className={classes.menuItem}
                                component={Link}
                                to="/history"
                            >
                                History
                            </MenuItem>
                            <Divider />
                            <MenuItem
                                className={classes.menuItem}
                                onClick={onSignOut}
                            >
                                Sign out
                            </MenuItem>
                        </Menu>
                    </Link>
                </Box>
            )}
        </Toolbar>
    );
};

export default NavBar;
