import React from 'react'

import success from "../icons/success.svg"

import "../styles/components/success_icon.css"

const SuccessIcon = ({
  size = "small",
}) => {

  const icon_size =
    size === "small"
      ? "success_icon--small"
      : size === "medium"
      ? "success_icon--medium"
      : size === "large"
      ? "success_icon--large"
      : ""

  return (
    <img src={success} className={icon_size} alt="success icon" />
  )
}

export default SuccessIcon