import React from 'react'

import close from "../icons/x.svg"

import "../styles/components/close_icon.css"

const CloseIcon = ({
  size = "small",
}) => {
  const icon_size =
    size === "small"
      ? "close_icon--small"
      : size === "medium"
      ? "close_icon--medium"
      : size === "large"
      ? "close_icon--large"
      : ""

  return (
    <img src={close} className={icon_size} alt="close icon" />
  )
}

export default CloseIcon