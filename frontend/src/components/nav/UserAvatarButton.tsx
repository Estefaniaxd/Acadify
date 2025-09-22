export default function UserAvatarButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      className="fixed top-4 right-4 z-50 p-1 rounded-full border-2 border-primary bg-white dark:bg-[#18181b] shadow hover:scale-105 transition-transform"
      aria-label="Abrir perfil"
      onClick={onClick}
    >
      <img
        src="https://api.dicebear.com/7.x/bottts/svg?seed=acadify"
        alt="avatar"
        className="w-10 h-10 rounded-full"
      />
    </button>
  );
}
