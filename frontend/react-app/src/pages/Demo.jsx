import React, { useState } from "react";
import Toast from "../components/Toast";
//import TextField from "../components/TextField";
import Label from "../components/Label";

const Demo = () => {
  //const [value, setValue] = useState("");

  return (
    <div className="relative flex flex-col items-center justify-center gap-4 p-40">
      <Toast
        icon_size="large"
        type="error"
        message="This is an error message."
      />

      <Toast
        icon_size="large"
        type="caution"
        message="This is a caution message."
      />

      <Label
        size="small"
        text="This is a small label."
      />

      <Label
        size="medium"
        text="This is a medium label."
      />

      {/* Default 
      <TextField
        label="Placeholder"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />

      {/* Active (auto focus) 
      <TextField
        label="Placeholder"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />

      {/* Required
      <TextField
        label="Required"
        required
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />

      {/* Error
      <TextField
        label="Error"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        error="Error"
      />

      {/* Disabled 
      <TextField
        label="Placeholder"
        disabled
      />*/}
    </div>
  );
};

export default Demo;
