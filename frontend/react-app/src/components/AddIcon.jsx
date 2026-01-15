import React from 'react'

import addIcon from "../icons/add.svg"

import "../styles/components/add_icon.css"

const AddIcon = ({
  size = "small",
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
    <div className="add_icon__wrapper">
      <img src={addIcon} className={icon_size} alt="add icon" />
    </div>
  )
}

export default AddIcon