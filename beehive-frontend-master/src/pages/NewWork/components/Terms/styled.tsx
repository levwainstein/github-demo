import { Box, Typography } from '@mui/material';
import { styled } from '@mui/system';

import { colors } from '../../../../theme';

export const Container = styled(Box)`
    background-color: ${colors.darkBlue};
    width: 302px;
    padding: 24px 24px;
    border-radius: 4px;
    height: inherit;
    display: flex;
    flex-direction: column;
`;

export const TermsPriorityBox = styled(Box)`
    display: flex;
    justify-content: space-between;
    align-items: center;
`;

export const TermsText = styled(Typography)`
    color: ${colors.white90};
    font: 600 14px 'Inter';
`;

const getPriorityTextColor = (priority: string): string => {
    switch (priority) {
        case 'Urgent':
            return colors.sunsetOrange;
        case 'High':
            return colors.sunsetOrange;
        case 'Medium':
            return colors.orangeyYellow;
        case 'Low':
            return colors.freshGreen90;
        default:
            return '';
    }
};

const getPriorityBackgroundColor = (priority: string): string => {
    switch (priority) {
        case 'Urgent':
            return colors.lightSalmon10;
        case 'Medium':
        case 'High':
            return colors.lightSalmon10;
        case 'Medium':
            return colors.novajoWhite10;
        case 'Low':
            return colors.easterGreen10;
        default:
            return '';
    }
};

export const PriorityText = styled(Typography)<{ priority: string }>`
    color: ${({ priority }) => getPriorityTextColor(priority)};
    font: 12px 'Inter';
    padding: 8px 12px;
    background-color: ${({ priority }) => getPriorityBackgroundColor(priority)};
    border-radius: 16px;
`;

export const CalendarBox = styled(Box)`
    display: flex;
    margin-top: 13px;
    align-items: center;
    gap: 10px;
`;

export const CalenderText = styled(Typography)`
    color: ${colors.white70};
    font: 13px/23px 'Inter';
`;

export const AmountBox = CalendarBox;

export const AmountText = CalenderText;

export const DividerLine = styled(Box)`
    width: 308px;
    background-color: ${colors.ebonyClay};
    height: 2px;
`;

export const WorkTypeTitle = styled(TermsText)`
    margin-top: 24px;
`;

export const WorkTypeContent = styled(CalenderText)`
    margin-top: 13px;
`;

export const WorkContext = styled(Typography)`
    margin-top: 13px;
    color: ${colors.white70};
    font: 11px/23px 'Inter';
`;

export const WrongWorkTypeLink = styled(Typography)`
    text-decoration: underline;
    color: ${colors.orangeyYellow80};
    font: 13px/23px 'Inter';
    margin-top: 6px;
    cursor: pointer;
`;

export const SkillsNeededText = WorkTypeTitle;

export const SkillsBox = styled(Box)`
    margin-top: 18px;
    display: flex;
    gap: 6px;
    align-items: center;
    flex-wrap: wrap;
`;

export const ContextBox = styled(Box)<{ maxHeight: number }>`
    margin-top: 18px;
    display: flex;
    flex-direction: row;
    gap: 6px;
    align-items: left;
    flex-wrap: wrap;
    max-height: ${({ maxHeight }) => maxHeight}px;
    overflow: scroll;
`;

export const SkillBox = styled(Box)`
    background-color: ${colors.ebonyClay};
    border-radius: 16px;
    padding: 7px 10px;
    display: flex;
    gap: 6px;
`;

export const SkillNameText = styled(Typography)`
    font: 12px/18px 'Inter';
    color: ${colors.white70};
`;

export const ProjectText = WorkTypeTitle;

export const ProjectContent = WorkTypeContent;

export const ActionsBox = styled(Box)`
    display: flex;
    gap: 20px;
    justify-content: center;
`;

export const AcceptButton = styled(Typography)<{ disabled: boolean }>`
    width: 130px;
    height: 40px;
    background-color: ${colors.novajoWhite10};
    color: ${({ disabled }) => disabled ? colors.dimGray : colors.orangeyYellow};
    font: 500 14px 'Inter';
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 100px;
    cursor: ${({ disabled }) => disabled ? 'auto' : 'pointer'};
`;

export const SkipButton = AcceptButton;

export const CodeTitle = TermsText;

export const TertiaryVariantText = styled(CalenderText)`
    text-align: center;
    padding: 0px 10px;
    font-style: normal;
`;

export const RepoNameContainer = styled(Box)`
    display: flex;
    flex-direction: row;
    gap: 10px;
    align-items: center;
`;

export const RepoName = styled(Typography)`
    color: #c79719;
    font: 13px/23px 'Inter';
    cursor: pointer;
`;

export const BranchNameContainer = styled(RepoNameContainer)`
    align-items: flex-start;
`;

export const BranchIcon = styled(Box)`
    height: 18px;
    width: 18px;
`;

export const BranchName = styled(RepoName)`
    margin-top: -4px;
`;

export const CopyIconWrapper = styled(Box)`
    cursor: pointer;
`;

export const ImproveCodebaseText = styled(Typography)`
    font: 13px/23px 'Inter';
    color: ${colors.white50};
`;

export const ImproveCodebaseHighlight = styled(Typography)`
    font: 13px/23px 'Inter';
    color: #bc901a;
    display: inline;
    cursor: pointer;
`;

export const SpecialInstructionsTitle = CodeTitle;

export const SpecialInstructionsText = styled(ImproveCodebaseText)`
    padding-right: 15px;
`;

export const CodingGithubGuidelinesLink = styled(ImproveCodebaseHighlight)`
    text-decoration: underline;
    cursor: pointer;
`;
