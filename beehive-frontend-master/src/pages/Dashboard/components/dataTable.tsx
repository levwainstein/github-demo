import { Link, Table, TableBody, TableCell, TableContainer, TableHead } from '@material-ui/core';
import { TablePagination, TableRow, Tooltip, Typography } from '@material-ui/core';
import LinearProgress from '@material-ui/core/LinearProgress';
import { makeStyles } from '@material-ui/core/styles';
import { ChangeEvent, FunctionComponent, useCallback } from 'react';

const useStyles = makeStyles((theme) => ({
    root: {
        width: '100%'
    },
    container: {
        height: '100%',
        overflowX: 'initial'
    },
    inlineValueContainer: {
        display: 'flex',
        placeItems: 'center'
    },
    paging: {
        color: theme.palette.text.secondary
    },
    linebreakValueContainer: {
        whiteSpace: 'pre-line'
    }
}));

export type DataTableColumn = {
    field: string,
    label: string,
    minWidth?: number,
    format?: (value: any) => string;
    viewType?: string;
    tooltipField?: string;
    tooltipHeader?: string;
    linkHash?: (value: string) => string;
    suffixComponent?: (value: any) => React.ReactElement;
    submittableComponent?: (row: any, value: string) => React.ReactElement;
};

type Props = {
    columns: DataTableColumn[];
    rows: {[key: string]: any}[];
    totalRows: number;
    currentPage: number;
    currentPageChanged: (newPage: number) => void;
    rowsPerPage: number;
    rowsPerPageChanged: (newRowsPerPage: number) => void;
    onLinkClicked?: (newHash: string) => void;
};

const DataTable: FunctionComponent<Props> = ({
    columns, rows, totalRows, currentPage, currentPageChanged, rowsPerPage, rowsPerPageChanged
}: Props) => {
    const classes = useStyles();

    const handleChangePage = useCallback(
        (_, newPage: number) => {
            currentPageChanged(newPage);
        },
        [ currentPageChanged ]
    );

    const handleChangeRowsPerPage = useCallback(
        (event: ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => {
            rowsPerPageChanged(+event.target.value);
            currentPageChanged(0);
        },
        [ currentPageChanged, rowsPerPageChanged ]
    );

    const getRowColumnValue = (row: {[key: string]: any}, columnId: string): string => {
        const nextSeparatorIndex = columnId.indexOf('|');
        if (nextSeparatorIndex > -1) {
            return getRowColumnValue(row[columnId.slice(0, nextSeparatorIndex)], columnId.slice(nextSeparatorIndex + 1));
        } else {
            return row[columnId];
        }
    };

    const getCellContent = (row: {[key: string]: any}, column: DataTableColumn) => {
        const value: string = getRowColumnValue(row, column.field);
        const formattedValue: string = column.format ? column.format(value) : value;

        let valueComponent = (
            <Typography color="textSecondary">
                {formattedValue}
            </Typography>
        );

        // wrap component with link if needed
        if (column.linkHash) {
            valueComponent = (
                <Link href={`#${column.linkHash(value)}`}>
                    {valueComponent}
                </Link>
            );
        }

        // wrap component with tooltip if needed
        if (column.tooltipField && getRowColumnValue(row, column.tooltipField) ) {
            valueComponent = (
                <Tooltip title={
                    <span className={classes.linebreakValueContainer}>
                        {getRowColumnValue(row, column.tooltipField)}
                    </span>
                }>
                    {valueComponent}
                </Tooltip>
            );
        }

        // add suffix component if needed
        if (column.suffixComponent) {
            valueComponent = (
                <span className={classes.inlineValueContainer}>
                    {valueComponent}
                    {column.suffixComponent(value)}
                </span>
            );
        }

        // add empty component if needed
        if (column.submittableComponent) {
            if (column.tooltipField && getRowColumnValue(row, column.tooltipField) ) {
                valueComponent = (
                    <Tooltip title={
                        <span className={classes.linebreakValueContainer}>
                            {getRowColumnValue(row, column.tooltipField)}
                        </span>
                    }>
                        <span className={classes.inlineValueContainer}>
                            {column.submittableComponent(row, formattedValue)}
                        </span>
                    </Tooltip>
                );
            } else {
                valueComponent = (
                    <span className={classes.inlineValueContainer}>
                        {column.submittableComponent(row, formattedValue)}
                    </span>
                );
            }
        }

        if (column.viewType === 'gauge') {
            valueComponent = <div>
                <LinearProgress variant="determinate" value={Number(value)} />
                <Typography variant="body2" color="primary">{`${formattedValue}%`}</Typography>
            </div>;
        }

        // return TableCell component with value
        return (
            <TableCell key={column.field}>
                {valueComponent}
            </TableCell>
        );
    };

    return (
        <>
            <TableContainer className={classes.container}>
                <Table stickyHeader>
                    <TableHead>
                        <TableRow>
                            {columns.map((column) => (
                                <Tooltip key={column.field} title={column.tooltipHeader ?? ''}>
                                    <TableCell
                                        key={column.field}
                                        style={{ minWidth: column.minWidth }}
                                    >
                                        {column.label}
                                    </TableCell>
                                </Tooltip>
                                
                            ))}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {rows.map((row, rowIndex) => {
                            return (
                                <TableRow
                                    hover
                                    role="checkbox"
                                    tabIndex={-1}
                                    key={`work-row-${rowIndex}`}
                                >
                                    {columns.map((column) => getCellContent(row, column))}
                                </TableRow>
                            );
                        })}
                    </TableBody>
                </Table>
            </TableContainer>
            <TablePagination
                className={classes.paging}
                rowsPerPageOptions={[ 25, 50, 100 ]}
                component="div"
                count={totalRows}
                rowsPerPage={rowsPerPage}
                page={currentPage}
                onChangePage={handleChangePage}
                onChangeRowsPerPage={handleChangeRowsPerPage}
            />
        </>
    );
};

export default DataTable;
