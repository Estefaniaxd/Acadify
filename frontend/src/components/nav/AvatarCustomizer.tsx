import { useState } from 'react';

const skinColors = ['#F9D7B5', '#F2B07A', '#D2996B', '#A86B3C', '#6B3F1D'];
const hairStyles = [
  { id: 'short', label: 'Corto', icon: '🧑‍🦲' },
  { id: 'long', label: 'Largo', icon: '🧑‍🦱' },
  { id: 'curly', label: 'Rizado', icon: '🧑‍🦰' },
  { id: 'bun', label: 'Moño', icon: '🧑‍🦳' },
];
const hairColors = ['#222', '#A0522D', '#FFD700', '#F5DEB3', '#FFF', '#C0C0C0'];
const faces = [
  { id: 'smile', label: 'Sonriente', icon: '😊' },
  { id: 'cool', label: 'Cool', icon: '😎' },
  { id: 'wink', label: 'Guiño', icon: '😉' },
  { id: 'serious', label: 'Serio', icon: '😐' },
];
const tops = [
  { id: 'tshirt', label: 'Camiseta', icon: '👕' },
  { id: 'hoodie', label: 'Hoodie', icon: '🧥' },
  { id: 'shirt', label: 'Camisa', icon: '👔' },
  { id: 'dress', label: 'Vestido', icon: '👗' },
];
const accessories = [
  { id: 'none', label: 'Ninguno', icon: '' },
  { id: 'glasses', label: 'Gafas', icon: '🕶️' },
  { id: 'hat', label: 'Sombrero', icon: '🎩' },
  { id: 'headphones', label: 'Auriculares', icon: '🎧' },
];
const backgrounds = ['#F0F4F8', '#FFD700', '#A7F3D0', '#F9A8D4', '#C7D2FE', '#FDE68A'];

const tabs = [
  { id: 'skin', label: 'Color de piel' },
  { id: 'hair', label: 'Cabello' },
  { id: 'face', label: 'Rostro' },
  { id: 'top', label: 'Ropa' },
  { id: 'acc', label: 'Accesorios' },
  { id: 'bg', label: 'Fondo' },
];

type AvatarCustomizerProps = {
  onClose?: () => void;
  previewOnly?: boolean;
  showTabsOnly?: boolean;
};

export default function AvatarCustomizer({ onClose, previewOnly, showTabsOnly }: AvatarCustomizerProps) {
  const [tab, setTab] = useState('skin');
  const [skin, setSkin] = useState(skinColors[0]);
  const [hair, setHair] = useState(hairStyles[0].id);
  const [hairColor, setHairColor] = useState(hairColors[0]);
  const [face, setFace] = useState(faces[0].id);
  const [top, setTop] = useState(tops[0].id);
  const [acc, setAcc] = useState(accessories[0].id);
  const [bg, setBg] = useState(backgrounds[0]);

  // Preview SVG (simple, cartoon style)
  function AvatarSVG() {
    return (
      <svg width="120" height="120" viewBox="0 0 120 120" className="mx-auto mb-2" style={{ background: bg, borderRadius: 16 }}>
        {/* Cabeza */}
        <circle cx="60" cy="48" r="32" fill={skin} stroke="#222" strokeWidth="2" />
        {/* Cabello */}
        {hair === 'short' && <ellipse cx="60" cy="32" rx="28" ry="14" fill={hairColor} />}
        {hair === 'long' && <ellipse cx="60" cy="60" rx="30" ry="28" fill={hairColor} />}
        {hair === 'curly' && <ellipse cx="60" cy="38" rx="28" ry="18" fill={hairColor} />}
        {hair === 'bun' && <ellipse cx="60" cy="18" rx="10" ry="8" fill={hairColor} />}
        {/* Cara */}
        {face === 'smile' && <ellipse cx="60" cy="60" rx="12" ry="6" fill="#fff" />}
        {face === 'cool' && <rect x="45" y="50" width="30" height="10" rx="5" fill="#222" />}
        {face === 'wink' && <ellipse cx="60" cy="60" rx="10" ry="5" fill="#fff" />}
        {face === 'serious' && <rect x="50" y="60" width="20" height="4" rx="2" fill="#222" />}
        {/* Accesorios */}
        {acc === 'glasses' && <rect x="40" y="45" width="40" height="10" rx="5" fill="#333" opacity=".7" />}
        {acc === 'hat' && <rect x="40" y="10" width="40" height="18" rx="8" fill="#444" />}
        {acc === 'headphones' && <ellipse cx="30" cy="48" rx="6" ry="12" fill="#888" />}
        {acc === 'headphones' && <ellipse cx="90" cy="48" rx="6" ry="12" fill="#888" />}
        {/* Ropa */}
        {top === 'tshirt' && <rect x="35" y="80" width="50" height="30" rx="16" fill="#4F46E5" />}
        {top === 'hoodie' && <rect x="30" y="80" width="60" height="32" rx="18" fill="#10B981" />}
        {top === 'shirt' && <rect x="38" y="80" width="44" height="28" rx="12" fill="#F59E42" />}
        {top === 'dress' && <ellipse cx="60" cy="100" rx="24" ry="18" fill="#F472B6" />}
      </svg>
    );
  }

  // Solo preview del avatar (sin tabs ni botones)
  if (previewOnly) {
    return (
      <div className="flex items-center justify-center">
        <AvatarSVG />
      </div>
    );
  }

  // Solo tabs y opciones (sin preview ni header)
  if (showTabsOnly) {
    return (
      <div className="w-full max-w-lg mx-auto bg-white dark:bg-[#18181b] rounded-xl shadow-lg p-6 mt-2">
        <div className="flex gap-2 mb-4 overflow-x-auto pb-1">
          {tabs.map(t => (
            <button
              key={t.id}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${tab === t.id ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200'}`}
              onClick={() => setTab(t.id)}
            >
              {t.label}
            </button>
          ))}
        </div>
        {/* Opciones de cada tab */}
        {tab === 'skin' && (
          <div className="flex gap-2 flex-wrap justify-center">
            {skinColors.map(c => (
              <button key={c} className={`w-8 h-8 rounded-full border-2 ${skin === c ? 'border-primary' : 'border-gray-300'}`} style={{ background: c }} onClick={() => setSkin(c)} />
            ))}
          </div>
        )}
        {tab === 'hair' && (
          <>
            <div className="flex gap-2 mb-2 justify-center">
              {hairStyles.map(h => (
                <button key={h.id} className={`px-2 py-1 rounded text-lg ${hair === h.id ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-800'}`} onClick={() => setHair(h.id)}>{h.icon} {h.label}</button>
              ))}
            </div>
            <div className="flex gap-2 flex-wrap justify-center">
              {hairColors.map(c => (
                <button key={c} className={`w-8 h-8 rounded-full border-2 ${hairColor === c ? 'border-primary' : 'border-gray-300'}`} style={{ background: c }} onClick={() => setHairColor(c)} />
              ))}
            </div>
          </>
        )}
        {tab === 'face' && (
          <div className="flex gap-2 mb-2 justify-center">
            {faces.map(f => (
              <button key={f.id} className={`px-2 py-1 rounded text-lg ${face === f.id ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-800'}`} onClick={() => setFace(f.id)}>{f.icon} {f.label}</button>
            ))}
          </div>
        )}
        {tab === 'top' && (
          <div className="flex gap-2 mb-2 justify-center">
            {tops.map(t => (
              <button key={t.id} className={`px-2 py-1 rounded text-lg ${top === t.id ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-800'}`} onClick={() => setTop(t.id)}>{t.icon} {t.label}</button>
            ))}
          </div>
        )}
        {tab === 'acc' && (
          <div className="flex gap-2 mb-2 justify-center">
            {accessories.map(a => (
              <button key={a.id} className={`px-2 py-1 rounded text-lg ${acc === a.id ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-800'}`} onClick={() => setAcc(a.id)}>{a.icon} {a.label}</button>
            ))}
          </div>
        )}
        {tab === 'bg' && (
          <div className="flex gap-2 flex-wrap justify-center">
            {backgrounds.map(c => (
              <button key={c} className={`w-8 h-8 rounded-full border-2 ${bg === c ? 'border-primary' : 'border-gray-300'}`} style={{ background: c }} onClick={() => setBg(c)} />
            ))}
          </div>
        )}
      </div>
    );
  }

  // Modo sidebar (completo)
  return (
    <div className="w-full max-w-md mx-auto bg-white dark:bg-[#18181b] rounded-xl shadow-lg p-6 mt-2">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-bold text-primary">Personalizar avatar</h3>
        {onClose && <button onClick={onClose} className="text-xl text-gray-500 hover:text-primary">×</button>}
      </div>
      <AvatarSVG />
      <div className="flex gap-2 mb-4 overflow-x-auto pb-1">
        {tabs.map(t => (
          <button
            key={t.id}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${tab === t.id ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200'}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>
      {/* Opciones de cada tab */}
      {tab === 'skin' && (
        <div className="flex gap-2 flex-wrap justify-center">
          {skinColors.map(c => (
            <button key={c} className={`w-8 h-8 rounded-full border-2 ${skin === c ? 'border-primary' : 'border-gray-300'}`} style={{ background: c }} onClick={() => setSkin(c)} />
          ))}
        </div>
      )}
      {tab === 'hair' && (
        <>
          <div className="flex gap-2 mb-2 justify-center">
            {hairStyles.map(h => (
              <button key={h.id} className={`px-2 py-1 rounded text-lg ${hair === h.id ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-800'}`} onClick={() => setHair(h.id)}>{h.icon} {h.label}</button>
            ))}
          </div>
          <div className="flex gap-2 flex-wrap justify-center">
            {hairColors.map(c => (
              <button key={c} className={`w-8 h-8 rounded-full border-2 ${hairColor === c ? 'border-primary' : 'border-gray-300'}`} style={{ background: c }} onClick={() => setHairColor(c)} />
            ))}
          </div>
        </>
      )}
      {tab === 'face' && (
        <div className="flex gap-2 mb-2 justify-center">
          {faces.map(f => (
            <button key={f.id} className={`px-2 py-1 rounded text-lg ${face === f.id ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-800'}`} onClick={() => setFace(f.id)}>{f.icon} {f.label}</button>
          ))}
        </div>
      )}
      {tab === 'top' && (
        <div className="flex gap-2 mb-2 justify-center">
          {tops.map(t => (
            <button key={t.id} className={`px-2 py-1 rounded text-lg ${top === t.id ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-800'}`} onClick={() => setTop(t.id)}>{t.icon} {t.label}</button>
          ))}
        </div>
      )}
      {tab === 'acc' && (
        <div className="flex gap-2 mb-2 justify-center">
          {accessories.map(a => (
            <button key={a.id} className={`px-2 py-1 rounded text-lg ${acc === a.id ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-800'}`} onClick={() => setAcc(a.id)}>{a.icon} {a.label}</button>
          ))}
        </div>
      )}
      {tab === 'bg' && (
        <div className="flex gap-2 flex-wrap justify-center">
          {backgrounds.map(c => (
            <button key={c} className={`w-8 h-8 rounded-full border-2 ${bg === c ? 'border-primary' : 'border-gray-300'}`} style={{ background: c }} onClick={() => setBg(c)} />
          ))}
        </div>
      )}
      <div className="mt-6 flex justify-end">
        <button className="px-4 py-2 rounded bg-primary text-white font-semibold hover:bg-primary/90 transition-colors">Guardar avatar</button>
      </div>
    </div>
  );
}
