import React from 'react'

import addIcon from "../icons/add.svg"

import "../styles/components/add_icon.css"

const AddIcon = ({
  size = "small",
  disabled = false,
  onClick
}) => {
  const icon_size =
    size === "small"
      ? "add_icon--small"
      : size === "medium"
      ? "add_icon--medium"
      : size === "large"
      ? "add_icon--large"
      : ""

  return (
    <button 
      className="add_icon__wrapper"
      disabled={disabled} 
      onClick={onClick}
      type="button"
    >
      <img src={addIcon} className={icon_size} alt="add icon" />
    </button>
  )
}

export default AddIcon