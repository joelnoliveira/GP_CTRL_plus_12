import React from 'react'

import warning from "../icons/warning.svg"

import "../styles/components/warning_icon.css"

const WarningIcon = ({
  size = "small",
}) => {

  const icon_size =
    size === "small"
      ? "warning_icon--small"
      : size === "medium"
      ? "warning_icon--medium"
      : size === "large"
      ? "warning_icon--large"
      : ""

  return (
    <img src={warning} className={icon_size} alt="warning icon" />
  )
}

export default WarningIcon