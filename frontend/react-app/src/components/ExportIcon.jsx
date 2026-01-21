import React from 'react'

import exportIcon from "../icons/export.svg"

import "../styles/components/export_icon.css"

const ExportIcon = ({
  size = "small",
  hasWrapper = true,
}) => {
  const icon_size =
    size === "small"
      ? "export_icon--small"
      : size === "medium"
      ? "export_icon--medium"
      : size === "large"
      ? "export_icon--large"
      : ""

  return (
    hasWrapper ? (
      <div className="export_icon__wrapper">
        <img src={exportIcon} className={icon_size} alt="export icon" />
      </div>
    ) : (
      <img src={exportIcon} className={icon_size} alt="export icon" />
    )
  );
};

export default ExportIcon;