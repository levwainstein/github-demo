import { Box, Card, Checkbox, Chip, Grid, TextField, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import {
    CheckBox as CheckBoxIcon,
    CheckBoxOutlineBlank as CheckBoxOutlineBlankIcon
} from '@material-ui/icons';
import { Autocomplete } from '@material-ui/lab';
import { FunctionComponent, useCallback, useState } from 'react';

const useStyles = makeStyles((theme) => {
    return {
        autoComplete: {
            margin: theme.spacing(1)
        },
        noOptionsBox: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
        },
        option: {
            color: theme.palette.text.secondary
        },
        input: {
            color: theme.palette.text.secondary
        }
    };
});

type Props = {
    skills?: string[];
    availableSkills: string[];
    profileLoading: boolean;
    onSkillsSubmit: (updatedSkills: string[]) => void;
    className?: string;
};

const Skills: FunctionComponent<Props> = ({
    skills,
    availableSkills,
    profileLoading,
    onSkillsSubmit,
    className
}: Props) => {
    const classes = useStyles();

    const [ inputValue, setInputValue ] = useState<string>('');

    const handleInputChange = useCallback(
        (event, newValue) => {
            if (event) {
                setInputValue(newValue);
            }
        },
        [ setInputValue ]
    );

    const handleChange = useCallback(
        (_, newValues) => {
            onSkillsSubmit(newValues);
        },
        [ onSkillsSubmit ]
    );

    return (
        <Card className={className}>
            <Grid container direction="row">
                <Grid item xl={8} lg={8} md={8} sm={8} xs={8}>
                    <Typography variant="h4" color="primary">
                        Skills
                    </Typography>
                    <Autocomplete
                        className={classes.autoComplete}
                        multiple
                        disabled={profileLoading}
                        value={skills ?? []}
                        options={availableSkills}
                        ChipProps={{ color: 'primary' }}
                        inputValue={inputValue}
                        onInputChange={handleInputChange}
                        noOptionsText={(
                            <Box className={classes.noOptionsBox}>
                                Skill &quot;{inputValue}&quot; does not exist
                            </Box>
                        )}
                        renderTags={(tagValue, getTagProps) =>
                            tagValue.map((option, index) => (
                                <Chip
                                    key={`skill-chip-${index}`}
                                    label={option}
                                    color="primary"
                                    {...getTagProps({ index })}
                                    disabled={profileLoading}
                                />
                            ))
                        }
                        renderOption={(option, { selected }) => (
                            <Box className={classes.option}>
                                <Checkbox
                                    icon={<CheckBoxOutlineBlankIcon fontSize="small" />}
                                    checkedIcon={<CheckBoxIcon fontSize="small" />}
                                    style={{ marginRight: 8 }}
                                    checked={selected}
                                />
                                {option}
                            </Box>
                        )}
                        onChange={handleChange}
                        renderInput={(params) => (
                            <TextField
                                {...params}
                                variant="outlined"
                                label="Skills"
                                placeholder="Skills"
                                InputProps={{
                                    ...params.InputProps,
                                    classes: {
                                        root: classes.input
                                    }
                                }}
                            />
                        )}
                    />
                </Grid>
                <Grid item xl={2} lg={2} md={2} sm={2} xs={2}>
                </Grid>
                <Grid item xl={2} lg={2} md={2} sm={2} xs={2}>
                </Grid>
            </Grid>
        </Card>
    );
};

export default Skills;
