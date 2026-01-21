import React from "react";

const Checkbox = ({ label, checked, onChange }) => {
  return (
    <label className="flex items-center gap-4 cursor-pointer select-none">
      {/* Hidden native checkbox */}
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="hidden peer"
      />

      {/* Custom checkbox */}
      <span
        className="
          flex items-center justify-center
          w-[18px] h-[18px]
          rounded-md
          border-2 border-gray-300
          transition-all duration-200
          peer-checked:bg-emerald-500
          peer-checked:border-emerald-500
          shrink-0
          mt-0.5
        "
      >
        <span
          className="
            text-white text-xs
            opacity-0
            peer-checked:opacity-100
          "
        >
          ✓
        </span>
      </span>

      {/* Label text */}
      <span className="text-sm leading-snug">
        {label}
      </span>
    </label>
  );
};

export default Checkbox;
