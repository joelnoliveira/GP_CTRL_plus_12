import React from "react";
import Label from "./Label"

import "../styles/components/toggle_switch.css"

const ToggleSwitch = (
    { 
        checked,
        onChange, 
    }
) => {

    const label = checked ? "Public" : "Private"
    
    return (
        <label className="toggle__container">
            <div
                className={`toggle__container__div
                ${checked ? "toggle__container__div--public" : "toggle__container__div--private"}
                `}
                onClick={() => onChange(!checked)}
            >
                <div
                className={`toggle__container__div__inner-circle
                    ${checked ? "translate-x-4" : ""}
                `}
                />
            </div>

            <Label 
                size={"medium"}
                text={label}
                styles={"toggle__label"}
            />
        </label>
    );
};

export default ToggleSwitch;

