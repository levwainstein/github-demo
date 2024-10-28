import { Card, Grid, Typography } from '@material-ui/core';
import { FunctionComponent } from 'react';

type Props = {
    className?: string
};

const Billing: FunctionComponent<Props> = ({ className }: Props) => {
    return (
        <Card className={className}>
            <Grid container direction="row">
                <Grid item xl={8} lg={8} md={8} sm={8} xs={8}>
                    <Typography variant="h4" color="primary">
                        Billing
                    </Typography>
                </Grid>
                <Grid item xl={2} lg={2} md={2} sm={2} xs={2}>
                </Grid>
                <Grid item xl={2} lg={2} md={2} sm={2} xs={2}>
                </Grid>
            </Grid>
        </Card>
    );
};

export default Billing;
