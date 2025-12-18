import React, { useState, useEffect } from "react";
import Toast from "../components/Toast";
//import TextField from "../components/TextField";
import Label from "../components/Label";
import ProgressBar from "../components/ProgressBar";
import ToggleSwitch from "../components/ToggleSwitch";

import RunCard from "../components/RunCard";

const Demo = () => {
  //const [value, setValue] = useState("");
  const [progress, setProgress] = useState(0);

  const [isPublic, setIsPublic] = useState(false);
    const handleIsPublic = (newValue) => {
        setIsPublic(newValue);
    }

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 1;
      });
    }, 1000); // 1 second = 1%

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative flex flex-col items-center justify-center gap-4 p-40">
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

      <ProgressBar value={progress} label={"Uploading..."}/>

      <ToggleSwitch
        checked={isPublic}
        onChange={handleIsPublic}
      />

      <RunCard 
        run_name_id={"Run 1"}
        username={"Joao123"}
        attack_type={"Attack Type 1"}
        date={"18/12/2025"}
        status={"Ongoing"}
        attack_model={"gemma-2-2b-it"}
        target_model={"gemma-2-2b-it"}
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
