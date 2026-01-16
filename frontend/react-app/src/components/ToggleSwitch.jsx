import React from "react";
import Label from "./Label"

import "../styles/components/toggle_switch.css"

const ToggleSwitch = (
    { 
        checked,
        onChange, 
        options = ["Private", "Public"],
        styles_text = "toggle__label",
    }
) => {

    const label = checked ? options[1] : options[0];
    
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
                styles={styles_text}
            />
        </label>
    );
};

export default ToggleSwitch;

