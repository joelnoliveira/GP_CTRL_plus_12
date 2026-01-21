import React from 'react'

import caution from "../icons/caution.svg"

import "../styles/components/caution_icon.css"

const CautionIcon = ({
  size = "small",
}) => {

  const icon_size =
    size === "small"
      ? "caution_icon--small"
      : size === "medium"
      ? "caution_icon--medium"
      : size === "large"
      ? "caution_icon--large"
      : ""

  return (
    <img src={caution} className={icon_size} alt="caution icon" />
  )
}

export default CautionIcon