import React from 'react'

import userIcon from "../icons/user.svg"

import "../styles/components/user_icon.css"

const UserIcon = ({
  size = "small",
}) => {
  const icon_size =
    size === "small"
      ? "user_icon--small"
      : size === "medium"
      ? "user_icon--medium"
      : size === "large"
      ? "user_icon--large"
      : ""

  return (
    <div className="user_icon__wrapper">
      <img src={userIcon} className={icon_size} alt="user icon" />
    </div>
  )
}

export default UserIcon