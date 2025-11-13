import React, { useEffect, useState, useRef } from "react";
import axios from "axios";

interface Reaction {
  emoji: string;
  cantidad: number;
  usuarios: Array<{ usuario_id: string; usuario_nombre: string; fecha: string; reaccion_id?: string }>;
}

interface EmojiReactionsProps {
  comentarioId: string;
  currentUserId: string;
  apiBaseUrl: string;
}

const EMOJI_CATEGORIES = [
  {
    name: "Aprobación",
    emojis: ["👍", "�", "💯", "👌", "🙌", "🔥", "🎉"]
  },
  {
    name: "Alegría",
    emojis: ["�", "�", "😊", "😃", "😁", "😆", "😎"]
  },
  {
    name: "Sorpresa",
    emojis: ["�😮", "�", "�", "�", "�"]
  },
  {
    name: "Tristeza",
    emojis: ["�", "😭", "😔", "😞"]
  },
  {
    name: "Pensando",
    emojis: ["🤔", "😐", "😶"]
  }
];

export const EmojiReactions: React.FC<EmojiReactionsProps> = ({ comentarioId, currentUserId, apiBaseUrl }) => {
  const [reactions, setReactions] = useState<Reaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const [activeCategory, setActiveCategory] = useState(EMOJI_CATEGORIES[0].name);
  const [feedback, setFeedback] = useState<string|null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowMenu(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const fetchReactions = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${apiBaseUrl}/cursos/comentarios/${comentarioId}/reacciones`);
      setReactions(res.data.data || []);
    } catch (err) {
      setReactions([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReactions();
    // eslint-disable-next-line
  }, [comentarioId]);

  const handleReact = async (emoji: string) => {
    try {
      await axios.post(`${apiBaseUrl}/cursos/comentarios/${comentarioId}/reacciones`, { emoji, tipo: 'like' });
      setShowMenu(false);
      setFeedback("¡Reacción agregada!");
      setTimeout(() => setFeedback(null), 1200);
      fetchReactions();
    } catch (err) {
      setFeedback("Error al agregar reacción");
      setTimeout(() => setFeedback(null), 1500);
    }
  };

  const handleRemove = async (emoji: string) => {
    const reaccion = reactions
      .find(r => r.emoji === emoji)?.usuarios
      .find(u => u.usuario_id === currentUserId);
    if (reaccion && reaccion.reaccion_id) {
      try {
        await axios.delete(`${apiBaseUrl}/cursos/reacciones/${reaccion.reaccion_id}`);
        setFeedback("Reacción eliminada");
        setTimeout(() => setFeedback(null), 1200);
        fetchReactions();
      } catch (err) {
        setFeedback("Error al eliminar reacción");
        setTimeout(() => setFeedback(null), 1500);
      }
    }
  };

  return (
    <div className="flex items-center gap-2 relative">
      {/* Botón + moderno */}
      <button
        className="w-8 h-8 flex items-center justify-center rounded-full bg-gradient-to-tr from-blue-200 to-blue-400 text-blue-800 shadow-lg hover:scale-110 transition-all border-2 border-blue-300"
        title="Agregar reacción"
        onClick={() => setShowMenu(v => !v)}
        aria-label="Agregar reacción"
      >
        <span className="text-xl font-bold">+</span>
      </button>
      {/* Popover de emojis por categoría */}
      {showMenu && (
        <div
          ref={menuRef}
          className={`absolute top-10 z-50 bg-white border border-gray-200 shadow-2xl rounded-xl p-3 min-w-[220px] max-h-[260px] flex flex-col animate-fade-in`}
          style={(() => {
            if (window.innerWidth < 600) {
              // Móvil: centrar y scroll horizontal
              return { left: '50%', transform: 'translateX(-50%)', minWidth: 220, maxWidth: '90vw', overflowX: 'auto' };
            }
            // Desktop: calcular borde derecho
            const btn = menuRef.current?.parentElement?.getBoundingClientRect();
            if (btn && window.innerWidth - btn.left < 340) {
              return { right: 0, minWidth: 220, maxWidth: 320 };
            }
            return { left: 0, minWidth: 220, maxWidth: 320 };
          })()}
        >
          <div className="flex gap-1 mb-2 overflow-x-auto">
            {EMOJI_CATEGORIES.map(cat => (
              <button
                key={cat.name}
                className={`px-2 py-1 rounded-full text-xs font-semibold border transition-all ${activeCategory === cat.name ? "bg-blue-100 border-blue-400 text-blue-700" : "bg-gray-50 border-gray-200 text-gray-500 hover:bg-blue-50"}`}
                onClick={() => setActiveCategory(cat.name)}
              >
                {cat.name}
              </button>
            ))}
          </div>
          <div className="grid grid-cols-7 gap-2 overflow-y-auto">
            {EMOJI_CATEGORIES.find(cat => cat.name === activeCategory)?.emojis.map(emoji => {
              const reaction = reactions.find(r => r.emoji === emoji);
              const reacted = reaction?.usuarios.some(u => u.usuario_id === currentUserId);
              return (
                <button
                  key={emoji}
                  className={`w-8 h-8 flex items-center justify-center text-xl rounded-full transition-all duration-150 border-2 ${reacted ? "border-blue-400 bg-blue-50" : "border-transparent bg-gray-50 hover:bg-blue-100"}`}
                  onClick={() => (reacted ? handleRemove(emoji) : handleReact(emoji))}
                  aria-label={`Reaccionar con ${emoji}`}
                >
                  {emoji}
                </button>
              );
            })}
          </div>
        </div>
      )}
      {/* Feedback visual */}
      {feedback && (
        <span className="absolute left-12 top-0 bg-blue-50 text-blue-700 px-2 py-1 rounded shadow text-xs animate-fade-in">{feedback}</span>
      )}
      {/* Mostrar reacciones seleccionadas */}
      <div className="flex gap-1 flex-wrap ml-2">
        {reactions.map(reaction => (
          <div
            key={reaction.emoji}
            className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold bg-gray-100 border border-gray-200 ${reaction.usuarios.some(u => u.usuario_id === currentUserId) ? "ring-2 ring-blue-400" : ""}`}
          >
            <span className="text-lg">{reaction.emoji}</span>
            <span>{reaction.cantidad}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
