export default function HamburgerButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      className="fixed top-4 left-4 z-50 p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none"
      aria-label="Abrir menú"
      onClick={onClick}
    >
      <svg className="w-7 h-7 text-primary" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>
  );
}
