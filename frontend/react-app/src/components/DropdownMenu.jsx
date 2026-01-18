import React, { useState, useRef, useEffect } from "react";
import ArrowIcon from "./ArrowIcon";
import "../styles/components/dropdown_menu.css";

const DropdownMenu = ({ placeholder = "Placeholder", items = ["Item1", "Item2", "Item3"], onSelect, value }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [internalSelected, setInternalSelected] = useState("");
  const dropdownRef = useRef(null);

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
    if (onSelect) {
      onSelect(item);
    }
    setInternalSelected(item);
    setIsOpen(false);
  };

  return (
    <div className="dropdown" ref={dropdownRef}>
      {/*<button
            onClick={() => setIsOpen(!isOpen)}
            className={`dropdown__button
                        ${isOpen ? "border-red-400" : "border-gray-300"}`}
        >*/}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="dropdown__button"
      >
        {selectedValue || placeholder}
        <span className="dropdown__arrow">
          {isOpen
            ? <ArrowIcon variant="arrow_up" />
            : <ArrowIcon variant="arrow_down" />
          }
        </span>
      </button>

      {isOpen && (
        <ul className="dropdown__menu">
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
