/* copied from https://github.com/TeamWertarbyte/material-ui-search-bar/
 * since code has not been updated in years and has a peer dependency of
 * react v16
 */

import { IconButton, Input, Paper } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import ClearIcon from '@material-ui/icons/Clear';
import SearchIcon from '@material-ui/icons/Search';
import clsx from 'clsx';
import React from 'react';

const useStyles = makeStyles((theme) => ({
    root: {
        height: theme.spacing(6),
        display: 'flex',
        justifyContent: 'space-between'
    },
    iconButton: {
        color: theme.palette.action.active,
        transform: 'scale(1, 1)',
        transition: theme.transitions.create([ 'transform', 'color' ], {
            duration: theme.transitions.duration.shorter,
            easing: theme.transitions.easing.easeInOut
        })
    },
    iconButtonHidden: {
        transform: 'scale(0, 0)',
        '& > $icon': {
            opacity: 0
        }
    },
    searchIconButton: {
        marginRight: theme.spacing(-6)
    },
    icon: {
        transition: theme.transitions.create([ 'opacity' ], {
            duration: theme.transitions.duration.shorter,
            easing: theme.transitions.easing.easeInOut
        })
    },
    input: {
        width: '100%'
    },
    searchContainer: {
        margin: 'auto 16px',
        width: `calc(100% - ${theme.spacing(6 + 4)}px)` // 6 button + 4 margin
    }
}));

/**
 * Material design search bar
 * @see [Search patterns](https://material.io/archive/guidelines/patterns/search.html)
 */
const SearchBar = React.forwardRef(
    (
        {
            cancelOnEscape,
            className = '',
            closeIcon = <ClearIcon />,
            disabled = false,
            onCancelSearch,
            onRequestSearch,
            searchIcon = <SearchIcon />,
            style = null,
            value = '',
            placeholder = 'Search',
            onFocus,
            onBlur,
            onChange,
            onKeyUp,
            ...inputProps
        }: {
            cancelOnEscape?: boolean,
            className?: string,
            closeIcon?: React.ReactElement,
            disabled?: boolean,
            onCancelSearch?: () => void,
            onRequestSearch?: (value: string) => void,
            searchIcon?: React.ReactElement,
            style?: any,
            value?: string,
            placeholder?: string,
            onFocus?: React.FocusEventHandler<HTMLInputElement | HTMLTextAreaElement>,
            onBlur?: React.FocusEventHandler<HTMLInputElement | HTMLTextAreaElement>,
            onChange?: React.ChangeEventHandler<HTMLInputElement | HTMLTextAreaElement>,
            onKeyUp?: React.KeyboardEventHandler<HTMLInputElement | HTMLTextAreaElement>
        },
        ref
    ) => {
        const classes = useStyles();

        const inputRef = React.useRef<HTMLInputElement>();
        const [ currentValue, setCurrentValue ] = React.useState(value);

        React.useEffect(() => {
            setCurrentValue(value);
        }, [ value ]);

        const handleFocus = React.useCallback(
            (e) => {
                if (onFocus) {
                    onFocus(e);
                }
            },
            [ onFocus ]
        );

        const handleBlur = React.useCallback(
            (e) => {
                setCurrentValue((v) => v.trim());
                if (onBlur) {
                    onBlur(e);
                }
            },
            [ onBlur ]
        );

        const handleInput = React.useCallback(
            (e) => {
                setCurrentValue(e.target.value);
                if (onChange) {
                    onChange(e.target.value);
                }
            },
            [ onChange ]
        );

        const handleCancel = React.useCallback(() => {
            setCurrentValue('');
            if (onCancelSearch) {
                onCancelSearch();
            }
        }, [ onCancelSearch ]);

        const handleRequestSearch = React.useCallback(() => {
            if (onRequestSearch) {
                onRequestSearch(currentValue);
            }
        }, [ onRequestSearch, currentValue ]);

        const handleKeyUp = React.useCallback(
            (e) => {
                if (e.charCode === 13 || e.key === 'Enter') {
                    handleRequestSearch();
                } else if (
                    cancelOnEscape &&
                    (e.charCode === 27 || e.key === 'Escape')
                ) {
                    handleCancel();
                }
                if (onKeyUp) {
                    onKeyUp(e);
                }
            },
            [ handleRequestSearch, cancelOnEscape, handleCancel, onKeyUp ]
        );

        React.useImperativeHandle(ref, () => ({
            focus: () => {
                inputRef.current?.focus();
            },
            blur: () => {
                inputRef.current?.blur();
            }
        }));

        return (
            <Paper className={clsx(classes.root, className)} style={style}>
                <div className={classes.searchContainer}>
                    <Input
                        {...inputProps}
                        inputRef={inputRef}
                        onBlur={handleBlur}
                        value={currentValue}
                        onChange={handleInput}
                        onKeyUp={handleKeyUp}
                        onFocus={handleFocus}
                        fullWidth
                        className={classes.input}
                        disableUnderline
                        disabled={disabled}
                        placeholder={placeholder}
                    />
                </div>
                <IconButton
                    onClick={handleRequestSearch}
                    className={clsx(classes.iconButton, classes.searchIconButton, {
                        [classes.iconButtonHidden]: currentValue !== ''
                    })}
                    disabled={disabled}
                >
                    {React.cloneElement(searchIcon, {
                        classes: { root: classes.icon }
                    })}
                </IconButton>
                <IconButton
                    onClick={handleCancel}
                    className={clsx(classes.iconButton, {
                        [classes.iconButtonHidden]: currentValue === ''
                    })}
                    disabled={disabled}
                >
                    {React.cloneElement(closeIcon, {
                        classes: { root: classes.icon }
                    })}
                </IconButton>
            </Paper>
        );
    }
);

SearchBar.displayName = 'SearchBar';

export default SearchBar;
