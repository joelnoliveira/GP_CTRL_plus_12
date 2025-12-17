import React, { useState } from "react";
import TextField from "../components/TextField";

const Demo = () => {
  const [value, setValue] = useState("");

  return (
    <div className="flex flex-col items-center justify-center gap-4 p-40">
      {/* Default */}
      <TextField
        label="Placeholder"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />

      {/* Active (auto focus) */}
      <TextField
        label="Placeholder"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />

      {/* Required */}
      <TextField
        label="Required"
        required
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />

      {/* Error */}
      <TextField
        label="Error"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        error="Error"
      />

      {/* Disabled */}
      <TextField
        label="Placeholder"
        disabled
      />
    </div>
  );
};

export default Demo;
