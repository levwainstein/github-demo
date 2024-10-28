import StarIcon from '@material-ui/icons/Star';
import StarBorderIcon from '@material-ui/icons/StarBorder';
import {
    Box,
    Rating,
    Table,
    TableCell,
    TablePagination,
    TableRow
} from '@mui/material';
import dayjs from 'dayjs';
import duration from 'dayjs/plugin/duration';
import relativeTime from 'dayjs/plugin/relativeTime';
import utc from 'dayjs/plugin/utc';
import lodash from 'lodash';
import { ChangeEvent, FC, useEffect, useState } from 'react';

import { Label, SearchInputWrapper } from '../../../../shared';
import SortIcon from '../../../../shared/sortIcon';
import { HistoryElement, HistoryTableProps } from '../../../../types/history';
import Feedback from '../Feedback';
import * as S from './styled';

// load dayjs duration and dependent plugin
dayjs.extend(duration);
dayjs.extend(relativeTime);
dayjs.extend(utc);

const TasksTable: FC<HistoryTableProps> = ({
    title,
    subtitle,
    allRows
}) => {
    const [ page, setPage ] = useState<number>(0);
    const [ rowsPerPage, setRowsPerPage ] = useState<number>(5);
    const [ rowsState, setRowsState ] = useState<HistoryElement[]>(allRows);
    const pageStart = page * rowsPerPage;
    const pageEnd = (page + 1) * rowsPerPage;
    const rowsStatePaginated = (rowsState).slice(pageStart, pageEnd);
    const [ feedbackIndex, setFeedbackIndex ] = useState(null);
        
    const TABLE_HEADER_CELLS = { project: 'Project',
        created: 'Time created',
        name: 'Task name',
        rating: 'Rating',
        duration: 'Net working time',
        description: 'Description & Feedback' };

    const handleChangePage = (_: any, _page: number) => setPage(_page);

    const handleChangeRowsPerPage = (event: ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(Number(event.target.value));
        setPage(0);
    };

    const [ sortType, setSortType ] = useState<string>('desc');
    const [ sortBy, setSortBy ] = useState<string>('');
    const handleSort = (_sortBy: string) => {
        setSortBy(_sortBy);
        const _sortType = sortType === 'asc' ? 'desc' : 'asc';
        setSortType(_sortType);
        const _rows = JSON.parse(JSON.stringify(rowsState));
        _rows.sort((a: HistoryElement, b: HistoryElement) => {
            const _a = a[_sortBy as keyof HistoryElement];
            const _b = b[_sortBy as keyof HistoryElement];
            return _sortType === 'asc' ? (_a > _b ? 1 : -1) : _b > _a ? 1 : -1;
        });
        setRowsState(_rows.sort((a: HistoryElement, b: HistoryElement) => {
            const _a = a[_sortBy as keyof HistoryElement];
            const _b = b[_sortBy as keyof HistoryElement];
            if (_sortBy === 'duration') {
                return _sortType === 'asc' ? (Number(_a) > Number(_b) ? 1 : -1) : Number(_b) > Number(_a) ? 1 : -1;
            }
            return _sortType === 'asc' ? (_a > _b ? 1 : -1) : _b > _a ? 1 : -1;
        }));
    };

    const [ search, setSearch ] = useState<string>('');
    const handleSearch = (event: ChangeEvent<HTMLInputElement>) => {
        const input = event.target.value;
        setSearch(input);
        if (input) {
            setRowsState(
                allRows.filter((mod) =>
                    mod.name && mod.name.toLowerCase().includes(input.toLowerCase())
                )
            );
        } else {
            setRowsState(allRows);
        }
    };

    const feedBackClicked = (index) => {
        setFeedbackIndex(index);
    };

    useEffect(() => {
        setRowsState(allRows);
    }, [ allRows ]);

    return (
        <div>
            <Feedback
                open={feedbackIndex !== null}
                onClose={() => {
                    feedBackClicked(null);
                }} 
                description={feedbackIndex !== null ? rowsStatePaginated[feedbackIndex].description : ''} 
                feedbacks={feedbackIndex !== null ? rowsStatePaginated[feedbackIndex].ratings : []}
            />
        
            <S.Container>
                <S.Header>
                    <S.Titles>
                        <S.Title>{title}</S.Title>
                        <S.Subtitle>{subtitle}</S.Subtitle>
                    </S.Titles>
                    <SearchInputWrapper
                        search={search}
                        handleSearch={handleSearch}
                    />
                </S.Header>
                <Box height={24} />
                <Table stickyHeader>
                    <S.StyledTableHead>
                        <TableRow>
                            {Object.keys(TABLE_HEADER_CELLS).map((th, i) => (
                                <TableCell align="center" key={i}>
                                    <Label onClick={() => handleSort(th)}>
                                        {TABLE_HEADER_CELLS[th]}
                                        {sortBy === th && (
                                            <SortIcon sort={sortType} />
                                        )}
                                    </Label>
                                </TableCell>
                            ))}
                        </TableRow>
                    </S.StyledTableHead>
                    <S.StyledTableBody>
                        {rowsStatePaginated.map((row, i) => (
                            <TableRow key={i}>
                                <S.ProjectCell align="center">
                                    {lodash.startCase(lodash.replace(row.project, 'project:', ''))}
                                </S.ProjectCell>
                                <S.TimeCreatedCell align="center">
                                    {dayjs(row.created).format('MMM DD, YYYY HH:MM')}
                                </S.TimeCreatedCell>
                                <S.TaskNameCell align="center">
                                    {row.name}
                                </S.TaskNameCell>
                                <S.SkillsCell
                                    align="center"
                                    onClick={() => {
                                        feedBackClicked(i);
                                    }}
                                >
                                    {row.ratings.length ? <Rating
                                        readOnly
                                        value={row.ratings.reduce((acc, v, i, a) => (acc+v.score/a.length), 0)}
                                        precision={0.5}
                                        icon={
                                            <StarIcon/>
                                        }
                                        emptyIcon={
                                            <StarBorderIcon/>
                                        }
                                    />
                                        : null}
                                </S.SkillsCell>
                                <S.NetWorkingTimeCell align="center">
                                    {dayjs.duration(row.duration, 'seconds').humanize()}
                                </S.NetWorkingTimeCell>
                                <S.DescriptionAndFeedbackCell align="center">
                                    {`${row.description.slice(
                                        0,
                                        50
                                    )}... `}
                                    <S.ReadMore onClick={() => {
                                        feedBackClicked(i);
                                    }}>
                                    Read more
                                    </S.ReadMore>
                                </S.DescriptionAndFeedbackCell>
                            </TableRow>
                        ))}
                    </S.StyledTableBody>
                    <S.StyledTableFooter>
                        <TableRow>
                            <TablePagination
                                colSpan={6}
                                count={rowsState.length}
                                page={page}
                                rowsPerPageOptions={[ 5, 20, 50, 100 ]}
                                onPageChange={handleChangePage}
                                rowsPerPage={rowsPerPage}
                                onRowsPerPageChange={handleChangeRowsPerPage}
                            />
                        </TableRow>
                    </S.StyledTableFooter>
                </Table>
            </S.Container>
        </div>
    );
};

export default TasksTable;
