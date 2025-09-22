import React from 'react'

type Props = {
  children: React.ReactNode
  onClick?: () => void
  className?: string
}

export default function Button({ children, onClick, className = '' }: Props) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors shadow-sm ${className}`}
    >
      {children}
    </button>
  )
}
