import AvatarCustomizer from '../../components/nav/AvatarCustomizer';
import { useNavigate } from 'react-router-dom';

export default function AvatarCustomizerPage() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#18181b] flex flex-col">
      <header className="flex items-center justify-between px-8 py-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-[#18181b]">
        <div className="flex items-center gap-2">
          <button onClick={() => navigate(-1)} className="text-2xl text-gray-500 hover:text-primary">←</button>
          <span className="text-xl font-bold text-primary">Personaliza tu avatar</span>
        </div>
      </header>
      <main className="flex-1 flex justify-center items-center">
        <div className="w-full max-w-5xl flex flex-row gap-12 p-8">
          <div className="flex-1 flex flex-col items-center justify-center">
            {/* Avatar grande */}
            <div className="w-64 h-64 flex items-center justify-center bg-white dark:bg-zinc-900 rounded-2xl shadow border border-gray-200 dark:border-gray-700 mb-6">
              <AvatarCustomizer previewOnly />
            </div>
            <button className="mt-4 px-8 py-3 bg-primary text-white rounded-full text-lg font-bold shadow hover:bg-primary-dark transition">Salvar</button>
          </div>
          <div className="flex-[2]">
            {/* Editor de opciones */}
            <AvatarCustomizer showTabsOnly />
          </div>
        </div>
      </main>
    </div>
  );
}
