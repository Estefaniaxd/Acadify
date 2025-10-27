import React from 'react'
import Nav from './Nav'
import Footer from './Footer'

type Props = {
  children: React.ReactNode
}

export default function AuthLayout({ children }: Props) {
  return (
    <div className="min-h-screen bg-[var(--color-bg)] text-[var(--color-text)]">
      <Nav />
      <div className="pt-32 pb-8" style={{ minHeight: 'calc(100vh - 8rem)', zIndex: 1 }}>
        {children}
      </div>
      <Footer />
    </div>
  )
}