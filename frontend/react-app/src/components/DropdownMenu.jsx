import React, { useState, useRef, useEffect } from "react";

import ArrowIcon from "./ArrowIcon";

import "../styles/components/dropdown_menu.css";

const DropdownMenu = ({ 
  placeholder = "Placeholder",
  items = ["Item1", "Item2", "Item3"],
  value,
  onSelect,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  //const [selected, setSelected] = useState("");
  const dropdownRef = useRef(null);

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
    setIsOpen(false);
    onSelect?.(item);
  };

  return (
    <div className="dropdown" ref={dropdownRef}>
        <button
            onClick={() => setIsOpen(!isOpen)}
            className="dropdown__button"
        >
            <div className="truncate">
              {value || placeholder}
            </div>
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
                  className={`dropdown__menu-item ${item === value ? "dropdown__menu-item--selected" : ""}`}
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
