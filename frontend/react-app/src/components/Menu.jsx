import React, {useState} from 'react'

import MenuItem from './MenuItem'
import "../styles/components/menu.css"

const Menu = ({
    currentPage,
}
) => {

    const menuItemsList = [
        { text: 'Home', link_to: '/' },
        { text: 'Run Experiment', link_to: '/run_experiment' },
        { text: 'History', link_to: '/history' },
        { text: 'Compare Results', link_to: '/compare' }
    ]

    const [itemSelected, setItemSelected] = useState(currentPage || menuItemsList[0].text)

    const handleItemSelected = (itemText) => {
        setItemSelected(itemText)
    }

    return (
        <div className="menu">
            <h2 className="menu__h2">Menu</h2>

            <div className="menu__item-list">
                {menuItemsList.map((item, index) => (
                    <MenuItem 
                        key={index}
                        text={item.text}
                        itemSelected={itemSelected}
                        handleItemSelected={handleItemSelected}
                        page={item.link_to}
                    />
                ))}
            </div>
            
        </div>
    )
}

export default Menu
