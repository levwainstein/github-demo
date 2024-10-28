import {
    Box,
    styled,
    TableBody,
    TableCell,
    TableFooter,
    TableHead,
    Typography } from '@mui/material';

import { colors } from '../../../../theme';

export const Container = styled(Box)``;

export const StyledTableHead = styled(TableHead)`
    th {
        background-color: ${colors.darkBlue};
        border-bottom: 0.5px solid ${colors.white30};
        padding: 24px;
        svg {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            left: 100%;
            color: ${colors.white90};
        }
        label {
            font: 500 12px/15px 'Inter', sans-serif !important;
            color: ${colors.white90};
            cursor: pointer;
            position: relative;
        }
    }
`;

export const StyledTableBody = styled(TableBody)`
    td {
        background-color: ${colors.darkBlue};
        font: 12px/18px 'Inter', sans-serif;
        color: ${colors.white70};
        border-bottom: 0.5px solid ${colors.tuna};
        padding: 24px;
    }
`;

export const StyledTableFooter = styled(TableFooter)`
    background-color: ${colors.darkBlue};
    .MuiSelect-select {
        position: relative;
        top: 3px;
    }
    & svg.MuiSelect-icon {
        fill: ${colors.white50};
    }
    & .MuiTablePagination-root {
        padding: 8px 0px !important;
        border-bottom: none;
        & div,
        p {
            font: 12px/12px 'Inter', sans-serif !important;
            color: ${colors.white50};
        }
    }
`;

export const ProjectCell = styled(TableCell)`
    width: 12%;
`;

export const TimeCreatedCell = styled(ProjectCell)``;

export const SkillsCell = styled(ProjectCell)`
    cursor: pointer;
`;

export const TaskNameCell = styled(TableCell)`
    width: 30%;
`;

export const NetWorkingTimeCell = styled(ProjectCell)``;

export const DescriptionAndFeedbackCell = styled(TableCell)`
    width: 22%;
    text-align: left;
`;

export const Header = styled(Box)`
    display: flex;
    margin-top: 50px;
    justify-content: space-between;
`;

export const Titles = styled(Box)`
    margin-left: 20px;
`;

export const Title = styled(Typography)`
    font: 600 16px/19px 'Inter', sans-serif;
    color: ${colors.white90};
`;

export const Subtitle = styled(Typography)`
    font: 12px/12px 'Inter', sans-serif;
    color: ${colors.white50};
    margin-top: 10px;
`;

export const ReadMore = styled('label')`
    color: ${colors.lightningYellowRgba};
    text-decoration: underline;
    cursor: pointer;
`;
