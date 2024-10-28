import SearchIcon from '@material-ui/icons/Search';
import { TextField } from '@mui/material';
import styled from 'styled-components';

import { colors } from '../../theme';

export const searchInputStyles = {
    searchLabelSX: {
        color: colors.white50,
        fontFamily: '"Inter",sans-serif',
        fontSize: 12,
        lineHeight: '18px'
    },
    searchInputSX: {
        color: colors.white50,
        fontFamily: '"Inter",sans-serif',
        fontSize: 12,
        lineHeight: '18px'
    }
};
export const SearchInput = styled(TextField)(
    (props: { width?: string }) => `
    && {
        border: 0.5px solid transparent;styled
        border-bottom: 0.5px solid ${colors.white30};
        width: ${props.width || '300px'};
    }
`
);

export const StyledSearchIcon = styled(SearchIcon)`
    color: ${colors.white70};
    width: 20px;
    height: 20px;
`;
