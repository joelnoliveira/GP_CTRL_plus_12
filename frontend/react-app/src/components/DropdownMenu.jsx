import React, { useState, useRef, useEffect } from "react";
import ArrowIcon from "./ArrowIcon";
import "../styles/components/dropdown_menu.css";

const DropdownMenu = ({
  placeholder = "Select...",   // Shown when closed
  items = ["Item1", "Item2", "Item3"],
  onSelect,
  value,
  hasDefault = false,        // <-- new prop, default false
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [internalSelected, setInternalSelected] = useState(null);
  const dropdownRef = useRef(null);

  // Controlled value takes priority
  const selectedValue = value !== undefined ? value : internalSelected;

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (item) => {
    setInternalSelected(item);
    onSelect?.(item);
    setIsOpen(false);
  };

  return (
    <div className="dropdown" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="dropdown__button"
      >
        {/* Button shows placeholder when nothing selected */}
        {selectedValue ?? placeholder}
        <span className="dropdown__arrow">
          {isOpen ? <ArrowIcon variant="arrow_up" /> : <ArrowIcon variant="arrow_down" />}
        </span>
      </button>

      {isOpen && (
        <ul className="dropdown__menu">
          {/* Render default "--" option only if hasDefault is true */}
          {hasDefault && (
            <li
              onClick={() => handleSelect(null)}
              className="dropdown__menu-item"
            >
              --
            </li>
          )}

          {items.map((item, index) => (
            <li
              key={index}
              onClick={() => handleSelect(item)}
              className="dropdown__menu-item"
            >
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default DropdownMenu;
