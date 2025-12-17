import React from 'react'

import arrowUp from "../icons/arrow_up.svg"
import arrowDown from "../icons/arrow_down.svg"

import "../styles/components/arrow_icon.css"

const ArrowIcon = ({
  size = "small",
  variant = "arrow_up",
}) => {
  const icon_source =
    variant === "arrow_up"
      ? arrowUp
      : arrowDown

  const icon_size =
    size === "small"
      ? "icon--small"
      : size === "medium"
      ? "icon--medium"
      : size === "large"
      ? "icon--large"
      : ""

  return (
    <img src={icon_source} className={icon_size} alt="arrow icon" />
  )
}

export default ArrowIcon