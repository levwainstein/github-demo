import { Meta, Story } from "@storybook/react";
import React, { useState } from "react";

import { SelectModal } from "../../src/shared";
import { Props } from "../../src/shared/selectModal";
import { Box, Button } from "@mui/material";

import { options } from '../../src/types/workTypes';

export default {
  title: "ContributorWork/SelectModal",
  component: SelectModal,
  argTypes: {},
  args: {},
} as Meta;

const Template: Story<Props> = (args) => {
  const [isVisible, setIsVisible] = useState(false);
  const handleClose = () => {
    setIsVisible(false);
  };
  const showModal = () => {
    setIsVisible(true);
  };
  return (
    <Box
      {...args}
      sx={{
        height: "200px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Button onClick={showModal}>Wrong work type?</Button>
      <SelectModal
        isVisible={isVisible}
        onSave={handleClose}
        onCancel={handleClose}
        option={options}
      />
    </Box>
  );
};

export const Primary = Template.bind({});
Primary.args = {
  title: "Select Modal",
};
