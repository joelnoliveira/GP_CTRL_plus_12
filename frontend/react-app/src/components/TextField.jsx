import React from "react";

import "../styles/components/text_field.css";

const TextField = ({
  label = "Placeholder",
  value,
  onChange,
  onBlur,
  required = false,
  error = "",
  disabled = false,
  type = "text",
}) => {
  const hasValue = value && value.length > 0;

  return (
    <div className="textfield__wrapper">
      <input
        type={type}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        disabled={disabled}
        placeholder=" "
        className={`
          textfield__input peer
          
          ${disabled
            ? "textfield__input--disabled"
            : error
            ? "textfield__input--error"
            : "border-red-400 focus:border-red-500"
          }

          focus:shadow-md
        `}
      />

      <label
        className={`
          textfield__label 
          peer-focus:-top-2 peer-focus:text-sm peer-focus:bg-white peer-focus:px-1
          ${hasValue ? "textfield__label--hasValue" : ""}

          ${error ? "textfield__label--error" : ""}
          ${disabled ? "textfield__label--disabled" : ""}
        `}
      >
        {label} {required && <span className="textfield__label--required">*</span>}
      </label>

      {error && (
        <p className="textfield__error-message">
          {error}
        </p>
      )}
    </div>
  );
};

export default TextField;
