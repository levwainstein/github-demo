import Box from '@mui/material/Box';
import InputAdornment from '@mui/material/InputAdornment';
import OutlinedInput from '@mui/material/OutlinedInput';
import Typography from '@mui/material/Typography';
import { Formik } from 'formik';
import { FunctionComponent, useState } from 'react';

import Github from '../../../../assets/icons/github';
import { Colors } from '../../../../utils/Colors';
import S from './styled';

type Props = {
    onSubmit: (url: string) => void;
};

const AddPullRequest: FunctionComponent<Props> = ({ onSubmit }: Props) => {
    const [ submitted, setSubmitted ] = useState<boolean>(false);

    const validateURL = (values) => {
        const errors = { url: '' };
        if (
            !/^https?:\/\/github\.com\/\S+\/\S+\/pull\/\d+$/i.test(values.url) &&
            !/^github\.com\/\S+\/\S+\/pull\/\d+$/i.test(values.url)
        ) {
            errors.url = 'Invalid url';
            return errors;
        }
        return;
    };

    return (
        <Formik
            initialValues={{ url: '' }}
            validate={(values) => validateURL(values)}
            onSubmit={(values, { setSubmitting }) => {
                setTimeout(() => {
                    setSubmitting(false);
                    setSubmitted(true);
                    onSubmit(values.url);
                }, 500);
            }}
            validateOnChange={false}
            validateOnBlur={false}
        >
            {({
                values,
                errors,
                handleChange,
                handleBlur,
                handleSubmit,
                isSubmitting,
                setFieldError
                /* and other goodies */
            }) => {
                const handleChangeWrapper = (e: React.ChangeEvent) => {
                    setFieldError('url', undefined); // <- reset error on the field
                    setSubmitted(false);
                    handleChange(e); // <- call original Formik's change handler
                };

                return (
                    <form onSubmit={handleSubmit}>
                        <S.Root>
                            <Typography sx={S.labelTitle} component="label">
                                Pull request URL
                            </Typography>
                            <Box>
                                <Typography
                                    sx={S.labelInstructions}
                                    component="label"
                                >
                                    Complete your work, create a Pull Request
                                    (PR), and paste it in the box below to
                                    analyze and submit your solution.
                                </Typography>
                                <S.Container>
                                    <OutlinedInput
                                        sx={S.Input(errors.url)}
                                        placeholder={'https://'}
                                        autoComplete={'off'}
                                        endAdornment={
                                            <InputAdornment position="end">
                                                <Github
                                                    color_start={
                                                        values.url &&
                                                        !errors.url
                                                            ? Colors.lightningYellow
                                                            : Colors.white30
                                                    }
                                                    color_stop={
                                                        values.url &&
                                                        !errors.url
                                                            ? Colors.pirateGold
                                                            : Colors.white30
                                                    }
                                                />
                                            </InputAdornment>
                                        }
                                        onChange={handleChangeWrapper}
                                        onBlur={handleBlur}
                                        name="url"
                                        value={values.url}
                                        error={!!errors.url}
                                    />
                                    {submitted ? (
                                        <S.SuccessSvg />
                                    ) : (
                                        <S.Button
                                            errorsUrl={errors.url}
                                            valuesUrl={values.url}
                                            disabled={
                                                isSubmitting || !values.url
                                            }
                                            type="submit"
                                        >
                                            <Typography
                                                sx={S.ButtonLabel(
                                                    values.url,
                                                    errors.url
                                                )}
                                                component={'label'}
                                            >
                                                Add
                                            </Typography>
                                        </S.Button>
                                    )}
                                </S.Container>
                            </Box>
                            <S.ErrorContainer>
                                {errors.url && (
                                    <S.ErrorChip
                                        label="Please check the Url"
                                        icon={<S.ReviewSvg />}
                                    />
                                )}
                            </S.ErrorContainer>
                        </S.Root>
                    </form>
                );
            }}
        </Formik>
    );
};

export default AddPullRequest;
