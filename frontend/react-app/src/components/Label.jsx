import React from 'react'

import "../styles/components/label.css";

const Label = (
    {
        size = "small",
        text,
    }
) => {
  return (
    <p className={`label--${size}`}>
      {text}
    </p>
  )
}

export default Label
