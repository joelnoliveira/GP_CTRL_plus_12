import React from "react";

import Label from "./Label"

import "../styles/components/progress_bar.css"

const ProgressBar = (
    { 
        value = 0,
        label = "",
    }
) => {
  return (
    <div className="progress-bar__container">
        {
            label !== "" && (
                <div className="progress-bar__label-div">
                    <Label
                        size={"small"}
                        text={label}
                    />
                </div>
            )
        }
        

        <div className="progress-bar__outter-div">
        <div
          className="
            progress-bar__inner-div
          "
          style={{ width: `${value}%` }}
        />

        <span className="progress-bar__value text-md">
            {value}%
        </span>
        </div>
    </div>
  );
};

export default ProgressBar;
