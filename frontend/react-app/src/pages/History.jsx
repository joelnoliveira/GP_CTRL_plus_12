import React from 'react'

import Menu from '../components/Menu'

const History = (
) => {
  return (
    <div className="w-full h-full flex justify-start items-center">
      <Menu 
        currentPage={"History"}
      />

      
      <p className="text-4xl">Histórico</p>
    </div>
  )
}

export default History