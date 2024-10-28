import StarIcon from '@material-ui/icons/Star';
import StarBorderIcon from '@material-ui/icons/StarBorder';
import { Rating } from '@mui/material';
import lodash from 'lodash';
import { FunctionComponent } from 'react';

import { Label } from '../../../../shared';
import Modal from '../../../../shared/modal';
import { BHRating } from '../../../../types/history';
import {
    CreatedAt,
    DescriptionBox,
    HorizontalLine,
    RatingBox,
    S,
    WrapperBox } from './styled';

type Props = {
    open?: boolean;
    onClose?: () => void;
    description: string;
    feedbacks: BHRating[];
};

const FeedbackModal: FunctionComponent<Props> = ({
    open = false,
    onClose,
    description,
    feedbacks
}: Props) => {
    return (
        <Modal
            hasCrossIcon={false}
            open={open}
            onClose={onClose}
            dialogStyle={S.modal}
        >
            <WrapperBox>
                <DescriptionBox>
                    <Label sxOverrides={S.title}>
                        Description
                    </Label>
                    <Label sxOverrides={S.text}>
                        {description}
                    </Label>
                    <HorizontalLine />
                </DescriptionBox>
                {feedbacks.map((item: any, index: number) => {
                    return (
                        <div key={index}>
                            <Label sxOverrides={S.title}>
                                {lodash.startCase(item.subject)}
                            </Label>
                            {item.created && (
                                <CreatedAt>
                                    <Label sxOverrides={S.createdTitle}>
                                        Created on
                                    </Label>
                                    <Label sxOverrides={S.created}>
                                        {item.created}
                                    </Label>
                                </CreatedAt>
                            )}
                            {item.score && (
                                <RatingBox>
                                    <Rating
                                        readOnly
                                        value={Number(item.score)}
                                        precision={0.5}
                                        icon={
                                            <StarIcon/>
                                        }
                                        emptyIcon={
                                            <StarBorderIcon/>
                                        }
                                    />
                                    <Label
                                        sxOverrides={S.rating}
                                    >
                                        {item.score}
                                    </Label>
                                </RatingBox>
                            )}
                            <Label sxOverrides={S.text}>
                                {item.text}
                            </Label>
                            {feedbacks.length - 1 !== index && (
                                <HorizontalLine />
                            )}
                        </div>
                    );
                })}
            </WrapperBox>
        </Modal>
    );
};

export default FeedbackModal;
