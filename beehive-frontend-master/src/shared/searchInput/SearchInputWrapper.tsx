import { SearchInput, searchInputStyles, StyledSearchIcon } from './styles';

export interface SearchInputWrapperProps {
    search: string;
    handleSearch: (event: React.ChangeEvent<HTMLInputElement>) => void;
    width?: string;
}

const SearchInputWrapper = ({
    search,
    handleSearch,
    width
}: SearchInputWrapperProps): JSX.Element => {
    return (
        <SearchInput
            label="Search"
            InputProps={{
                endAdornment: <StyledSearchIcon />,
                sx: searchInputStyles.searchInputSX
            }}
            InputLabelProps={{
                sx: searchInputStyles.searchLabelSX
            }}
            variant="standard"
            value={search}
            onChange={handleSearch}
            width={width}
        />
    );
};

export default SearchInputWrapper;
