import React from 'react'
import { Link } from "react-router-dom";

import "../styles/components/menu_item.css"

const MenuItem = (
    {
        text,
        itemSelected,
        handleItemSelected,
        page
    }
) => {
  return (
    <Link to={page}>
        <div 
            className={`menu-item ${itemSelected === text ? 'menu-item--active' : ''}`} 
            onClick={() => handleItemSelected(text)}
        >
            {text}
        </div>
    </Link>
  )
}

export default MenuItem
