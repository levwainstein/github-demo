import { Box } from '@material-ui/core';
import { Button, Dialog, TextField, Typography } from '@mui/material';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import { FunctionComponent, useCallback, useEffect, useState } from 'react';

import { styles, useStyles } from './styled'; 

export type Props = {
  isVisible: boolean;
  onSave: (value: string, reason?: string) => void;
  onCancel: () => void;
  options: {[key: string]: string};
};

const SelectModal: FunctionComponent<Props> = ({
    isVisible = true,
    onCancel,
    onSave,
    options
}: Props) => {
    const classes = useStyles();
    const [ selectedValue, setSelectedValue ] = useState<string>('');
    const [ otherReason, setOtherReason ] = useState<string>('');

    const handleOnSelectChange = useCallback(
        (event) => {
            setSelectedValue(event.target.value);
        },
        [ setSelectedValue ]
    );
    const handleOnInputChange = useCallback(
        (event) => {
            setOtherReason(event.target.value);
        },
        [ setOtherReason ]
    );
    const handleSave = () => {
        onSave(selectedValue, otherReason);
    };
    useEffect(() => {
        setOtherReason('');
    }, [ selectedValue ]);
    return (
        <Dialog
            onClose={onCancel}
            open={isVisible}
            PaperProps={{
                sx: styles.dialogPaper
            }}
        >
            <Box className={classes.container}>
                <Typography className={classes.title} variant="body1" component="p">
          Suggest a correction to work type
                </Typography>
                <Typography className={classes.subtitle} variant="body2" component="p">
          What do you think the work type should be?
                </Typography>
                <Select
                    className={classes.select}
                    value={selectedValue}
                    onChange={handleOnSelectChange}
                    displayEmpty
                    MenuProps={{
                        PaperProps: {
                            sx: styles.selectMenu
                        }
                    }}
                    inputProps={{
                        classes: {
                            icon: classes.selectIcon
                        }
                    }}
                >
                    {Object.keys(options).map((key) => {
                        return (
                            <MenuItem className={classes.selectItem} value={key} key={key}>
                                {options[key]}
                            </MenuItem>
                        );
                    })}
                </Select>
                {selectedValue === 'OTHER' ? (
                    <TextField
                        multiline
                        className={classes.input}
                        id="outlined-basic"
                        variant="outlined"
                        margin="dense"
                        placeholder="Type your suggestion..."
                        value={otherReason}
                        onChange={handleOnInputChange}
                    />
                ) : null}
                <Box className={classes.buttonsContainer}>
                    <Button onClick={onCancel} className={classes.button}>
                        <Typography className={classes.buttonText}>Cancel</Typography>
                    </Button>
                    <Button
                        disabled={selectedValue === ''}
                        onClick={handleSave}
                        className={classes.button}
                    >
                        <Typography className={classes.buttonText}>Save</Typography>
                    </Button>
                </Box>
            </Box>
        </Dialog>
    );
};

export default SelectModal;
