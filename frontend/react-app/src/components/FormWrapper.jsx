import React from 'react'

const FormWrapper = (
    { 
        onSubmit,
        children
    }
) => {
  return (
    <form onSubmit={onSubmit} noValidate className="flex flex-col gap-4 w-full">
      {children}
    </form>
  )
}

export default FormWrapper
