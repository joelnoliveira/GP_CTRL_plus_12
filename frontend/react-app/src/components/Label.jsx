import React from 'react'

import "../styles/components/label.css";

const Label = (
    {
        size = "small",
        text,
        styles,
    }
) => {
  return (
    <p className={`label--${size} ${styles}`}>
      {text}
    </p>
  )
}

export default Label
