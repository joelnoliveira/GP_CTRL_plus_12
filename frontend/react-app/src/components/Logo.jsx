import React from 'react'
import '../styles/components/logo.css';

const Logo = (
  {
    size = 'medium',
  }
) => {

  const logo_size =
    size === "small"
      ? "logo--small"
      : size === "medium"
      ? "logo--medium"
      : size === "large"
      ? "logo--large"
      : ""

  return (
    <img src="/logo_GP.png" className={logo_size} alt="Logo" />
  )
}

export default Logo
