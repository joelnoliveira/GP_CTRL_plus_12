import React from 'react'

import "../styles/components/button.css" 

{/*

  The ...props prop can be used to pass other props
  to the component such as disabled, etc.

  Example:

  <Button 
    variant={"default"}
    text={"Register"}
    disabled
  />
  
*/}

const Button = (
  {
    children,
    size,
    variant,
    text,
    styles = "",
    ...props
  }
) => {

  const btn_size = size === "small" ? 
  "btn--small" : size === "large" ?
  "btn--large" : ""

  const btn_variant = variant === "default" ? 
  "btn--default" : variant === "alternative" ?
  "btn--alternative" : ""


  return (
    <button 
      className={`${btn_size} ${btn_variant} ${styles}`}
      {...props}>
      {text}
      {children}
    </button>
  )
}

export default Button
