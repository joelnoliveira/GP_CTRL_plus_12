import React, { useState, useRef, useEffect } from 'react';
import userIcon from "../icons/user.svg"
import { useAuth } from '../context/AuthContext';

import "../styles/components/user_icon.css"

const UserIcon = ({
  size = "small",
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);
  const icon_size =
    size === "small"
      ? "user_icon--small"
      : size === "medium"
      ? "user_icon--medium"
      : size === "large"
      ? "user_icon--large"
      : ""

  const { logout } = useAuth();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="user_icon__container" ref={dropdownRef}>
      {/* The clickable trigger */}
      <div className="user_icon__wrapper " onClick={() => setIsOpen(!isOpen)}>
        <img src={userIcon} className={icon_size} alt="user icon" />
      </div>
      {/* The Dropdown Menu */}
      {isOpen && (
        <div className="user_icon__dropdown">
          <button className="dropdown__logout-btn" onClick={() => logout()}>
            Logout
          </button>
        </div>
      )}
    </div>
  )
}

export default UserIcon