import { Box } from '@mui/material';
import { FC, useCallback } from 'react';

import AmountIcon from '../../../../assets/icons/amount.png';
import BranchIcon from '../../../../assets/icons/branch.png';
import CalendarIcon from '../../../../assets/icons/calendar.png';
import CopyIcon from '../../../../assets/icons/copy.png';
import GithubIcon from '../../../../assets/icons/github.png';
import InfoIcon from '../../../../assets/icons/info.png';
import { UserSelectors } from '../../../../reducers/user';
import { WorkSelectors } from '../../../../reducers/work';
import { InformationTooltip } from '../../../../shared';
import { ContributorWorkSteps } from '../../../../types/contributorWork';
import { TaskContext } from '../../../../types/work';
import * as S from './styled';

const tooltipText =
    'This work requires skills that aren\'t\n listed in your profile.\n\
    We show the work anyway in case you want to give it a try. You can easily adjust your profile settings if you prefer to work exclusively within your skill set.';

const parseContextTooltip = (c: TaskContext) => {
    return `File: ${c.file} \nEntity: ${c.entity}\n\n Potential Use: ${c.potentialUse}`;
};

type PrimaryVariantProps = {
    type: string;
    workType: string;
    skillsNeeded?: string[];
    context?: TaskContext[];
    onAccept: () => void;
    onSkip: () => void;
};

const PrimaryVariant: FC<PrimaryVariantProps> = ({
    workType,
    skillsNeeded,
    context,
    onAccept,
    onSkip
}) => {
    const { workLoading } = WorkSelectors();
    const { profile } = UserSelectors();
    const showSkillsTooltip = profile && skillsNeeded && !skillsNeeded.every(s => profile.skills.includes(s));

    return (
        <>
            <S.WorkTypeTitle>Work type</S.WorkTypeTitle>
            <S.WorkTypeContent>{workType}</S.WorkTypeContent>
            {/* <S.WrongWorkTypeLink onClick={onClickWrongWorkType}>
            Wrong work type?
        </S.WrongWorkTypeLink> */}
            <Box height={24} />
            <S.DividerLine />
            <S.SkillsNeededText>Skills needed</S.SkillsNeededText>
            <S.SkillsBox>
                {skillsNeeded?.map((skill, index) => (
                    <S.SkillBox key={index}>
                        <S.SkillNameText>{skill}</S.SkillNameText>
                    </S.SkillBox>
                ))}
                {showSkillsTooltip && 
                    <InformationTooltip text={tooltipText}>
                        <img src={InfoIcon} />
                    </InformationTooltip>
                }
            </S.SkillsBox>
            <Box height={24}/>
            <S.DividerLine />
            {
                (context && context.length) && 
                <>
                    <S.ProjectText>Context</S.ProjectText>
                    <S.WorkContext>Relevant entities for this task (hover for more info)</S.WorkContext>
                        
                    <S.ContextBox maxHeight={160}>
                        {context.map((c, index) => (
                            <InformationTooltip text={parseContextTooltip(c)} key={index}>
                                <S.SkillBox>
                                    <S.SkillNameText>{c.entity}</S.SkillNameText>
                                </S.SkillBox>
                            </InformationTooltip>
                                
                        ))}
                    </S.ContextBox>
                    <Box height={24} />
                    <S.DividerLine />
                    <Box height={24} />
                </>
            }
            
            <div style={{ flexGrow: 10 }}/>
            <S.ActionsBox>
                <S.AcceptButton disabled={workLoading} onClick={() => !workLoading && onAccept()}>Accept</S.AcceptButton>
                <S.SkipButton disabled={workLoading} onClick={() => !workLoading && onSkip()}>Skip</S.SkipButton>
            </S.ActionsBox>
        </>
    );
};

type SecondaryVariantProps = {
    type: string;
    repositoryName: string | null;
    branchName: string | null;
    repositoryUrl: string | null;
    context?: TaskContext[];
};

const SecondaryVariant: FC<SecondaryVariantProps> = ({
    repositoryName,
    branchName,
    repositoryUrl,
    context
}) => {
    const onClickCopyIcon = useCallback(() => {
        navigator.clipboard.writeText(branchName || '');
    }, [ branchName ]);

    const onClickCodingGitubGuidelines = useCallback(() => {
        window.open('https://docs.caas.ai/community/general', '_blank');
    }, []);

    const onClickImproveOurCodebase = useCallback(() => {
        window.open(`${repositoryUrl}/issues`, '_blank');
    }, []);

    const onClickRepoName = useCallback(() => {
        if (repositoryUrl) {
            window.open(repositoryUrl, '_blank');
        }
    }, [ repositoryUrl ]);
    return (
        <>
            <Box height={20} />
            <S.CodeTitle>Code</S.CodeTitle>
            <Box height={15} />
            {repositoryName && 
                <S.RepoNameContainer onClick={onClickRepoName}>
                    <Box component={'img'} src={GithubIcon} />
                    <S.RepoName>{repositoryName}</S.RepoName>
                </S.RepoNameContainer>
            }
            <Box height={15} />
            {branchName && 
                <S.BranchNameContainer>
                    <img src={BranchIcon} />
                    <S.BranchName>{branchName}</S.BranchName>
                    <S.CopyIconWrapper onClick={onClickCopyIcon}>
                        <img src={CopyIcon} />
                    </S.CopyIconWrapper>
                </S.BranchNameContainer>
            }
            <Box height={20} />
            <S.ImproveCodebaseText>
                Have any ideas to{' '}
                <S.ImproveCodebaseHighlight
                    onClick={onClickImproveOurCodebase}
                >
                    improve our codebase
                </S.ImproveCodebaseHighlight>
                ?
            </S.ImproveCodebaseText>
            <S.ImproveCodebaseText>
                Make $1 for each improvement we accept.
            </S.ImproveCodebaseText>
            <Box height={25} />
            <S.DividerLine />
            {
                (context && context.length) && 
                <>
                    <S.ProjectText>Context</S.ProjectText>
                    <S.WorkContext>Relevant entities for this task (hover for more info)</S.WorkContext>
                        
                    <S.ContextBox maxHeight={85}>
                        {context.map((c, index) => (
                            <InformationTooltip text={parseContextTooltip(c)} key={index}>
                                <S.SkillBox>
                                    <S.SkillNameText>{c.entity}</S.SkillNameText>
                                </S.SkillBox>
                            </InformationTooltip>
                                
                        ))}
                    </S.ContextBox>
                    <Box height={24} />
                    <S.DividerLine />
                    <Box height={24} />
                </>
            }
            <S.SpecialInstructionsTitle>
                Special instructions
            </S.SpecialInstructionsTitle>
            <Box height={15} />
            <S.SpecialInstructionsText>
                Make sure you follow our{' '}
                <S.CodingGithubGuidelinesLink
                    onClick={onClickCodingGitubGuidelines}
                >
                    coding and GitHub guidelines
                </S.CodingGithubGuidelinesLink>
                , otherwise your work will be rejected.
            </S.SpecialInstructionsText>
            <Box height={15} />
            <S.SpecialInstructionsText>
                In particular, only use your designated branch, do not merge
                code yourself, and always do PR changes requests on the same
                branch.
            </S.SpecialInstructionsText>
        </>
    );
};

type TertiaryVariantProps = {
    type: string;
    text: string;
};

const TertiaryVariant: FC<TertiaryVariantProps> = ({ text }) => (
    <>
        <Box height={20} />
        <S.TertiaryVariantText>{text}</S.TertiaryVariantText>
    </>
);

export type TermsProps = {
    priority: 'High' | 'Medium' | 'Low' | 'Urgent';
    datetime: string;
    amount: string | null;
    variant: PrimaryVariantProps | SecondaryVariantProps | TertiaryVariantProps;
    currentStep: ContributorWorkSteps;
};

const Terms: FC<TermsProps> = ({ priority, datetime, amount, variant, currentStep }) => {

    const Variant = useCallback(() => {
        switch (variant.type) {
            case 'Primary':
                return <PrimaryVariant {...(variant as PrimaryVariantProps)} />;
            case 'Secondary':
                return (
                    <SecondaryVariant {...(variant as SecondaryVariantProps)} />
                );
            case 'Tertiary':
                return (
                    <TertiaryVariant {...(variant as TertiaryVariantProps)} />
                );
            default:
                return <></>;
        }
    }, [ variant ]);
    return (
        <S.Container height={currentStep === ContributorWorkSteps.SubmitPullRequest ? '243px' : '100%'}>
            <S.TermsPriorityBox>
                <S.TermsText>Terms</S.TermsText>
                {priority !== 'Medium' && 
                <S.PriorityText priority={priority}>
                    {priority} Priority
                </S.PriorityText>
                }
            </S.TermsPriorityBox>
            <S.CalendarBox>
                <img src={CalendarIcon} />
                <S.CalenderText>{datetime}</S.CalenderText>
            </S.CalendarBox>
            {amount &&
                <S.AmountBox>
                    <img src={AmountIcon} />
                    <S.AmountText>{amount}</S.AmountText>
                </S.AmountBox>
            }
            <Box height={24} />
            <S.DividerLine />
            <Variant />
        </S.Container>
    );
};

export default Terms;
