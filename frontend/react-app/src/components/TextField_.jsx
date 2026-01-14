import React from "react";

const TextField = ({
  label = "Placeholder",
  value,
  onChange,
  required = false,
  error = "",
  disabled = false,
  type = "text",
}) => {
  const hasValue = value && value.length > 0;

  return (
    <div className="w-full relative">
      {/* Input */}
      <input
        type={type}
        value={value}
        onChange={onChange}
        disabled={disabled}
        placeholder=" "
        className={`
          peer w-full rounded-xl px-4 pt-5 pb-2 text-base
          border transition-all duration-200 outline-none
          
          ${disabled
            ? "bg-gray-100 text-gray-400 cursor-not-allowed border-gray-300"
            : error
            ? "border-red-500 border-2 focus:border-red-600"
            : "border-red-400 focus:border-red-500"
          }

          focus:shadow-md
        `}
      />

      {/* Floating label */}
      <label
        className={`
          absolute left-4 top-4 text-gray-400 pointer-events-none
          transition-all duration-200

          peer-focus:-top-2 peer-focus:text-xs peer-focus:bg-white peer-focus:px-1
          ${hasValue ? "-top-2 text-xs bg-white px-1" : ""}

          ${error ? "text-red-500 font-bold" : ""}
          ${disabled ? "text-gray-400" : ""}
        `}
      >
        {label} {required && <span className="text-red-500">*</span>}
      </label>

      {/* Error message */}
      {error && (
        <p className="mt-1 text-sm text-red-500 font-bold pl-4 pt-1">
          {error}
        </p>
      )}
    </div>
  );
};

export default TextField;
