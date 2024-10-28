import { Typography } from '@mui/material';
import { ForwardedRef, FunctionComponent } from 'react';

import { colors } from '../../theme';

type VariantType = 'body1' | 'body2' | 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';

type ComponentType =
    | 'span'
    | 'div'
    | 'p'
    | 'h1'
    | 'h2'
    | 'h3'
    | 'h4'
    | 'h5'
    | 'h6'
    | 'label';

export interface Props {
    component?: ComponentType;
    variant?: VariantType;
    sxOverrides?: Record<string, unknown>;
    children?: React.ReactNode;
    gutterBottom?: boolean;
    noWrap?: boolean;
    paragraph?: boolean;
    color?: string;
    fontFamily?: string;
    fontSize?: string;
    fontWeight?: number;
    lineHeight?: string;
    opacity?: string;
    onClick?: () => void;
    ref?: ForwardedRef<HTMLElement | null>;
}

const Label: FunctionComponent<Props> = ({
    children,
    sxOverrides,
    component,
    variant,
    gutterBottom,
    noWrap,
    paragraph,
    color,
    fontFamily,
    fontSize,
    fontWeight,
    lineHeight,
    opacity,
    onClick,
    ref
}: Props) => (
    <Typography
        sx={{
            fontSize: fontSize ? fontSize : '14px',
            color: color ? color : colors.black,
            fontWeight: fontWeight ? fontWeight : '400',
            lineHeight: lineHeight ? lineHeight : '21px',
            margin: 0,
            fontFamily: fontFamily ? fontFamily : 'Poppins !important',
            fontStyle: 'normal',
            opacity,
            ...sxOverrides
        }}
        component={component || 'label'}
        variant={variant || 'body1'}
        gutterBottom={gutterBottom || false}
        noWrap={noWrap || false}
        paragraph={paragraph || false}
        onClick={onClick}
        ref={ref}
    >
        {children}
    </Typography>
);

export default Label;
