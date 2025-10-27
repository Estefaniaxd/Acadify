import React from 'react'

type Props = {
  theme: 'light' | 'dark'
  setTheme: (t: 'light' | 'dark') => void
}

export default function ThemeToggle({ theme, setTheme }: Props) {
  return (
    <div className="flex items-center gap-2">
      <button
        aria-label="toggle-theme"
        className="px-3 py-1 rounded-md bg-primary text-white"
        onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      >
        {theme === 'dark' ? 'Claro' : 'Oscuro'}
      </button>
    </div>
  )
}
