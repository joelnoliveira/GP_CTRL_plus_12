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
      : variant == "arrow_down"
      ? arrowDown
      : arrowUp

  const icon_size =
    size === "small"
      ? "arrow_icon--small"
      : size === "medium"
      ? "arrow_icon--medium"
      : size === "large"
      ? "arrow_icon--large"
      : ""

  return (
    <img src={icon_source} className={icon_size} alt="arrow icon" />
  )
}

export default ArrowIcon