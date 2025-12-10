// Constants
const RECENT_KEY = 'emoji_recent';
import React, { useEffect, useState, useRef, useCallback } from "react";
import Picker from '@emoji-mart/react';
import data from '@emoji-mart/data';

import axios from "axios";
import courseService from "../modules/academico/services/courseService";
import { motion, AnimatePresence } from 'framer-motion';

import { getWebSocketService, WebSocketEventType } from "../services/websocketService";

interface EmojiReactionsProps {
  comentarioId: string;
  currentUserId: string;
  apiBaseUrl?: string;
  onChange?: (reacciones: Reaction[]) => void;
  initialReactions?: Reaction[];
  postType?: 'anuncio' | 'pregunta' | 'comentario' | string;
}

type ReactionUser = { usuario_id: string; usuario_nombre?: string; fecha?: string; reaccion_id?: string };

type Reaction = {
  emoji: string;
  cantidad: number;
  usuarios: ReactionUser[];
};

export const EmojiReactions: React.FC<EmojiReactionsProps> = ({ comentarioId, currentUserId, apiBaseUrl, onChange, initialReactions, postType = 'comentario' }) => {
  // State
  const [serverReactions, setServerReactions] = useState<Reaction[]>([]);
  const [reactions, setReactions] = useState<Reaction[]>([]);
  const reactionsRef = useRef<Reaction[]>([]);
  useEffect(() => { reactionsRef.current = reactions; }, [reactions]);
  const arraysEqual = (a: Reaction[], b: Reaction[]) => {
    if (a === b) return true;
    if (!a || !b) return false;
    if (a.length !== b.length) return false;
    for (let i = 0; i < a.length; i++) {
      if (a[i].emoji !== b[i].emoji) return false;
      if (a[i].cantidad !== b[i].cantidad) return false;
      const aUsers = (a[i].usuarios || []).map(u => String(u.usuario_id)).sort().join(',');
      const bUsers = (b[i].usuarios || []).map(u => String(u.usuario_id)).sort().join(',');
      if (aUsers !== bUsers) return false;
    }
    return true;
  };

  const updateDisplayedIfDifferent = (displayed: Reaction[]) => {
    try {
      if (!arraysEqual(reactionsRef.current ?? [], displayed)) {
        reactionsRef.current = displayed;
        setReactions(displayed); // <-- update UI state
        onChange?.(displayed);
      }
    } catch (err) {
      // Log error but do not recurse
      console.error('updateDisplayedIfDifferent error', err);
    }
  };
  const [loading, setLoading] = useState(false);
  const [openPicker, setOpenPicker] = useState(false);
  const [pickerPosition, setPickerPosition] = useState<{ left?: number; right?: number } | null>(null);
  const [activeUsersEmoji, setActiveUsersEmoji] = useState<string | null>(null);
  const [recentlyAdded, setRecentlyAdded] = useState<string[]>([]);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Pending state
  type PendingEntry = { ts: number; action: 'add' | 'remove' };
  const [pendingReactions, setPendingReactions] = useState<Record<string, PendingEntry>>({});
  const pendingRef = useRef<Record<string, PendingEntry>>({});
  useEffect(() => { pendingRef.current = pendingReactions; }, [pendingReactions]);
  const lastToggleRef = useRef<Record<string, number>>({});
  const pendingTimersRef = useRef<Record<string, ReturnType<typeof setTimeout> | null>>({});
  const PENDING_AUTOCLEAR_MS = 12000;

  // Debug logger
  const dbg = (...args: any[]) => { try { console.debug('[EmojiReactions]', ...args); } catch {} };
  // Throttled debug logger for high-frequency events
  const dbgThrottleRef = useRef<Record<string, number>>({});
  const dbgThrottle = (key: string, interval = 1500, ...args: any[]) => {
    try {
      const now = Date.now();
      const last = dbgThrottleRef.current[key] ?? 0;
      if (now - last < interval) return;
      dbg(...args);
      dbgThrottleRef.current[key] = now;
    } catch {}
  };

  // Derive displayed reactions from server and pending
  // Always merge pending optimistic reactions with server state, never let server wipe out optimistic if not confirmed
  const deriveDisplayed = useCallback((srv: Reaction[], pending: Record<string, PendingEntry>): Reaction[] => {
    const serverMap = new Map<string, Reaction>();
    (srv || []).forEach((r: Reaction) => serverMap.set(r.emoji, { ...r, usuarios: Array.isArray(r.usuarios) ? r.usuarios : [] }));
    Object.keys(pending || {}).forEach(emoji => {
      const entry = pending[emoji];
      if (!entry) return;
      if (entry.action === 'add') {
        // If server does not have this emoji, always show it as optimistic
        if (!serverMap.has(emoji)) {
          serverMap.set(emoji, { emoji, cantidad: 1, usuarios: [{ usuario_id: String(currentUserId), usuario_nombre: undefined, fecha: new Date().toISOString() }] });
        } else {
          const srv = serverMap.get(emoji)!;
          // If server does not show current user, add optimistically
          if (!srv.usuarios.some(u => String(u.usuario_id) === String(currentUserId))) {
            srv.usuarios = [{ usuario_id: String(currentUserId), usuario_nombre: undefined, fecha: new Date().toISOString() }, ...srv.usuarios];
            srv.cantidad = srv.usuarios.length;
          }
        }
      } else if (entry.action === 'remove') {
        // Apply optimistic removal immediately so the UI reflects user's intent
        if (serverMap.has(emoji)) {
          const srv = serverMap.get(emoji)!;
          srv.usuarios = srv.usuarios.filter(u => String(u.usuario_id) !== String(currentUserId));
          srv.cantidad = srv.usuarios.length;
          if (srv.cantidad === 0) serverMap.delete(emoji);
        }
      }
    });
    return Array.from(serverMap.values());
  }, [currentUserId]);

  // Load reactions from server (dummy, should be replaced with real API call if needed)
  const load = useCallback(async () => {
    // Fetch reactions from backend and set server state
    try {
      // Prevent re-entrant loads which can cause UI thrashing
      if (loadingRef.current) {
        dbg('load: already loading, skipping');
        return;
      }
      loadingRef.current = true;
      setLoading(true);
      const resp = await courseService.getPostReactions(comentarioId);
      if (resp && resp.success && Array.isArray(resp.data)) {
  setServerReactions(resp.data as Reaction[]);
  updateDisplayedIfDifferent(deriveDisplayed(resp.data as Reaction[], pendingReactions));
      }
    } catch (err) {
      dbg('load: error fetching reactions', err);
    }
    finally {
      loadingRef.current = false;
      setLoading(false);
    }
  }, [comentarioId, deriveDisplayed]);

  // Prevent overlapping loads
  const loadingRef = useRef(false);

  // Schedule reload after mutation
  const loadTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const scheduleReload = (delay = 1500) => {
    if (loadTimeoutRef.current) clearTimeout(loadTimeoutRef.current);
    // Prevent scheduling loads too often to avoid heavy reflows
    const now = Date.now();
    const last = lastLoadTsRef.current ?? 0;
    if (now - last < 400) {
      dbgThrottle('scheduleReload_skip', 1000, 'scheduleReload: skipped because last load too recent', { delay });
      return;
    }
    loadTimeoutRef.current = setTimeout(() => {
  dbgThrottle('scheduleReload_triggered', 2000, 'scheduleReload triggered', { delay });
      const now = Date.now();
      const pendingKeys = Object.keys(pendingRef.current || {});
      const stillPending = pendingKeys.some(k => now - ((pendingRef.current[k]?.ts) ?? 0) < 5000);
  dbgThrottle('scheduleReload_check', 2000, 'scheduleReload check', { pendingKeys, stillPending });
      if (stillPending) {
        loadTimeoutRef.current = setTimeout(() => {
          dbgThrottle('scheduleReload_deferred', 2000, 'scheduleReload executing deferred load after pending still present');
          load();
          lastLoadTsRef.current = Date.now();
          loadTimeoutRef.current = null;
        }, 1200);
      } else {
  dbgThrottle('scheduleReload_now', 2000, 'scheduleReload executing load now (no recent pending)');
        // We call load immediately now to improve persistence UX
        load();
        lastLoadTsRef.current = Date.now();
        loadTimeoutRef.current = null;
      }
    }, delay);
  };

  const lastLoadTsRef = useRef<number | null>(null);

  // Recent emojis from localStorage
  const getRecent = (): string[] => {
    return [];
  };
  const pushRecent = (emoji: string) => {
    try {
      const prev = getRecent();
      const next = [emoji, ...prev.filter(e => e !== emoji)].slice(0, 16);
      localStorage.setItem(RECENT_KEY, JSON.stringify(next));
    } catch {}
  };

  // Mark emoji as pending
  const markPending = (emoji: string, action: 'add' | 'remove') => {
    setPendingReactions(prev => {
      const copy = { ...prev };
      copy[emoji] = { ts: Date.now(), action };
      return copy;
    });
    // No timeout: pending is only cleared when server confirms
    if (pendingTimersRef.current[emoji]) {
      clearTimeout(pendingTimersRef.current[emoji] as ReturnType<typeof setTimeout>);
      pendingTimersRef.current[emoji] = null;
    }
    // Setup fallback auto-clear if server never confirms
    pendingTimersRef.current[emoji] = setTimeout(() => {
      setPendingReactions(prev => {
        if (!prev || !Object.prototype.hasOwnProperty.call(prev, emoji)) return prev;
        const copy = { ...prev };
        delete copy[emoji];
        return copy;
      });
      pendingTimersRef.current[emoji] = null;
    }, PENDING_AUTOCLEAR_MS);
  };

  // Main toggle reaction logic
  const toggleReaction = useCallback(async (emoji: string) => {
    dbg('toggleReaction: start', { emoji }); // Log start of function
    if (!currentUserId) {
      dbg('toggleReaction: no currentUserId, exiting');
      return;
    }
    if (loadingRef.current) {
      dbg('toggleReaction: ignored, load in progress');
      return;
    }
    const now = Date.now();
    const last = lastToggleRef.current[emoji] ?? 0;
    if (now - last < 400) {
      dbg('toggleReaction debounced', { emoji, sinceLast: now - last });
      return;
    }
    lastToggleRef.current[emoji] = now;

    dbg('toggleReaction: determining intentAction');
    const existing = reactions.find((r: Reaction) => r.emoji === emoji);
    const userReacted = existing?.usuarios.some((u: ReactionUser) => String(u.usuario_id) === String(currentUserId));
    const serverExisting = serverReactions.find((r: Reaction) => r.emoji === emoji);
    const serverHasUser = serverExisting?.usuarios.some((u: ReactionUser) => String(u.usuario_id) === String(currentUserId));
    const intentAction: 'add' | 'remove' = serverHasUser ? 'remove' : (userReacted ? 'remove' : 'add');

    dbg('toggleReaction: intentAction determined', { intentAction });
    markPending(emoji, intentAction);
    if (!userReacted) {
      pushRecent(emoji);
      setRecentlyAdded(prev => [...prev.filter(e => e !== emoji), emoji]);
    }

    try {
      dbg('toggleReaction: sending request to server', { intentAction });
      let resp;
      if (serverHasUser || userReacted) {
        // IMPORTANT: backend DELETE endpoint treats the path param as comentario_id
        // and will remove ALL reactions for the user on that comment. To remove a
        // single emoji reaction we must call the POST endpoint with action='remove'
        // and include the emoji. Always use addReaction with action 'remove' here.
        dbg('toggleReaction: performing remove via addReaction(action=remove) to avoid deleting all user reactions');
        resp = await courseService.addReaction(comentarioId, emoji, 'like', 'remove');
        dbg('remove by action response', resp);
      } else {
        resp = await courseService.addReaction(comentarioId, emoji, 'like', 'add');
        dbg('addReaction response', resp);
      }

      dbg('toggleReaction: processing server response');
      let canonical: Reaction[] | undefined;
      try {
        const r: any = resp as any;
        const returned = r.reacciones ?? r.data ?? r;
        if (Array.isArray(returned)) {
          canonical = returned as Reaction[];
        } else if (returned && returned.reacciones && Array.isArray(returned.reacciones)) {
          canonical = returned.reacciones as Reaction[];
        }
      } catch {}
      if (canonical) {
        setServerReactions(canonical);
        updateDisplayedIfDifferent(deriveDisplayed(canonical, pendingReactions));
      } else {
        await load();
      }
      scheduleReload(400);
    } catch (err) {
      dbg('Error toggling reaction', err);
      await load();
    }
    dbg('toggleReaction: end'); // Log end of function
  }, [currentUserId, reactions, pendingReactions, comentarioId, deriveDisplayed, load, updateDisplayedIfDifferent]);

  // Recompute displayed reactions whenever server or pending changes
  // Throttle logging to avoid spamming the console in fast update loops
  const lastDeriveLogRef = useRef<{ key?: string; ts?: number }>({});

  useEffect(() => {
    try {
      const displayed = deriveDisplayed(serverReactions, pendingReactions);
        // Avoid updating state if nothing changed to prevent infinite render loops
        const oldKey = JSON.stringify(reactionsRef.current.map(r => ({ emoji: r.emoji, cantidad: r.cantidad })));
        const newKey = JSON.stringify(displayed.map(d => ({ emoji: d.emoji, cantidad: d.cantidad })));
        if (oldKey === newKey) {
          // No change in displayed state -> do nothing (avoid calling onChange)
          return;
        }
      // Only log if the derived content changed or if more than 2s have passed
      try {
        const key = JSON.stringify(displayed.map(d => ({ emoji: d.emoji, cantidad: d.cantidad }))); 
        const now = Date.now();
        if (lastDeriveLogRef.current.key !== key || (lastDeriveLogRef.current.ts && now - lastDeriveLogRef.current.ts > 2000)) {
          dbg('deriveDisplayed ->', displayed.map(d => ({ emoji: d.emoji, cantidad: d.cantidad })));
          lastDeriveLogRef.current.key = key;
          lastDeriveLogRef.current.ts = now;
        }
      } catch (ex) {
        dbgThrottle('deriveDisplayed_error', 2000, 'deriveDisplayed ->', displayed.map(d => ({ emoji: d.emoji, cantidad: d.cantidad })));
      }
      // Only update state if content actually changed to avoid re-render loops
      const old = reactionsRef.current ?? [];
      const equal = (() => {
        if (old.length !== displayed.length) return false;
        for (let i = 0; i < old.length; i++) {
          if (old[i].emoji !== displayed[i].emoji) return false;
          if (old[i].cantidad !== displayed[i].cantidad) return false;
          // Quick users length + presence check
          const oldUsers = old[i].usuarios?.map(u => String(u.usuario_id)).sort().join(',') ?? '';
          const newUsers = displayed[i].usuarios?.map(u => String(u.usuario_id)).sort().join(',') ?? '';
          if (oldUsers !== newUsers) return false;
        }
        return true;
      })();

      if (!equal) {
        updateDisplayedIfDifferent(displayed);
      }
      // Clear pending for emojis where server now matches intent
      setPendingReactions(prev => {
        const copy = { ...prev };
        let changed = false;
        Object.keys(prev).forEach(emoji => {
          const entry = prev[emoji];
          if (!entry) return;
          const server = serverReactions.find(r => r.emoji === emoji);
          // Solo limpiar pending si el backend refleja el cambio
          if (entry.action === 'add') {
            // Solo limpiar si el usuario YA aparece en la reacción
            if (server && server.usuarios.some(u => String(u.usuario_id) === String(currentUserId))) {
              delete copy[emoji];
              changed = true;
            }
          } else if (entry.action === 'remove') {
            // Solo limpiar si el usuario YA NO aparece en la reacción
            if (server && !server.usuarios.some(u => String(u.usuario_id) === String(currentUserId))) {
              delete copy[emoji];
              changed = true;
            }
            // Si la reacción ya no existe, también limpiar
            if (!server) {
              delete copy[emoji];
              changed = true;
            }
          }
        });
        return changed ? copy : prev;
      });
  // onChange has been invoked by updateDisplayedIfDifferent when needed
    } catch {}
  }, [serverReactions, pendingReactions, deriveDisplayed, onChange, currentUserId]);

  // Initial load: use provided `initialReactions` when available, otherwise fetch
  useEffect(() => {
    if (initialReactions && Array.isArray(initialReactions)) {
  setServerReactions(initialReactions);
  const displayed = deriveDisplayed(initialReactions, pendingReactions);
  updateDisplayedIfDifferent(displayed);
    } else {
      load();
    }
  }, [comentarioId, load, initialReactions, deriveDisplayed, pendingReactions, onChange]);

  // (initialReactions handled in initial load effect above)

  // Clear recentlyAdded after short delay
  useEffect(() => {
    if (recentlyAdded.length === 0) return;
    const t = setTimeout(() => setRecentlyAdded([]), 900);
    return () => clearTimeout(t);
  }, [recentlyAdded]);

  // Click outside to close picker
  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (!containerRef.current) return;
      if (!(e.target instanceof Node)) return;
      if (!containerRef.current.contains(e.target)) {
        setOpenPicker(false);
        setActiveUsersEmoji(null);
      }
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  // WebSocket reaction events
  useEffect(() => {
    let ws: any = null;
    const handler = (event: any) => {
      const id = event?.mensaje_id ?? event?.comentario_id ?? event?.data?.mensaje_id ?? event?.data?.comentario_id;
      if (!id) return;
      if (String(id) !== String(comentarioId)) return;
      const reacciones = event.reacciones ?? event.data?.reacciones ?? event.data;
      if (reacciones) {
        try {
          const arr = Array.isArray(reacciones) ? reacciones as Reaction[] : (reacciones.reacciones ?? reacciones.data ?? []);
          if (Array.isArray(arr)) {
            setServerReactions(arr as Reaction[]);
          }
        } catch {}
        const serverMap = new Map<string, Reaction>();
        (reacciones as Reaction[]).forEach((r: Reaction) => serverMap.set(r.emoji, { ...r }));
        const pending = pendingRef.current || {};
        Object.keys(pending).forEach(emoji => {
          const entry = pending[emoji];
          if (!entry) return;
          if (entry.action === 'add') {
            // Si el backend NO refleja la reacción, forzarla localmente
            if (!serverMap.has(emoji)) {
              serverMap.set(emoji, {
                emoji,
                cantidad: 1,
                usuarios: [{ usuario_id: String(currentUserId), usuario_nombre: undefined, fecha: new Date().toISOString() }]
              });
            } else {
              const srv = serverMap.get(emoji)!;
              if (!srv.usuarios.some(u => String(u.usuario_id) === String(currentUserId))) {
                srv.usuarios = [{ usuario_id: String(currentUserId), usuario_nombre: undefined, fecha: new Date().toISOString() }, ...srv.usuarios];
                srv.cantidad = srv.usuarios.length;
              }
            }
          } else if (entry.action === 'remove') {
            // Si el backend aún no borra la reacción, quitarla localmente
            if (serverMap.has(emoji)) {
              const srv = serverMap.get(emoji)!;
              srv.usuarios = srv.usuarios.filter(u => String(u.usuario_id) !== String(currentUserId));
              srv.cantidad = srv.usuarios.length;
              if (srv.cantidad === 0) serverMap.delete(emoji);
            }
          }
        });
  const merged = Array.from(serverMap.values());
  updateDisplayedIfDifferent(merged as Reaction[]);
        // Clear pending entries that were confirmed by server
        const pendingKeys = Object.keys(pendingRef.current || {});
        const toClear: string[] = [];
        pendingKeys.forEach(k => {
          const entry = pendingRef.current[k];
          const srv = merged.find(m => m.emoji === k);
          if (!entry) return;
          if (entry.action === 'add') {
            if (srv && srv.usuarios.some(u => String(u.usuario_id) === String(currentUserId))) toClear.push(k);
          } else if (entry.action === 'remove') {
            if (!srv || !srv.usuarios.some(u => String(u.usuario_id) === String(currentUserId))) toClear.push(k);
          }
        });
        if (toClear.length > 0) {
    dbgThrottle('ws_clearing_pending', 2000, 'ws clearing pending keys', toClear.map(k => ({ key:k, entry: pendingRef.current[k], serverHas: !!merged.find(m=>m.emoji===k) })));
          setPendingReactions(prev => {
            if (!prev) return prev;
            const copy = { ...prev };
            let changed = false;
            toClear.forEach(k => {
              if (Object.prototype.hasOwnProperty.call(copy, k)) { delete copy[k]; changed = true; }
            });
            return changed ? copy : prev;
          });
        }
      }
    };
    try {
      ws = getWebSocketService();
      ws.on(WebSocketEventType.MESSAGE_REACTION, handler);
    } catch {}
    return () => {
      try { if (ws) ws.off(WebSocketEventType.MESSAGE_REACTION, handler); } catch {}
    };
  }, [comentarioId, currentUserId, reactions, onChange]);

  // Render
  return (
    <div ref={containerRef} className="flex items-center gap-2 relative">
      {/* Inline reaction buttons */}
      <div className="flex items-center gap-1 flex-wrap">
        {/* Solo muestra las reacciones activas, sin lista fija */}
        {reactions.map((r) => {
          const reacted = r.usuarios.some(u => String(u.usuario_id) === String(currentUserId));
          const isPending = !!pendingReactions[r.emoji];
          return (
            <motion.button
              key={r.emoji}
              onClick={() => toggleReaction(r.emoji)}
              onMouseEnter={() => setActiveUsersEmoji(r.emoji)}
              onMouseLeave={() => setActiveUsersEmoji(prev => (prev === r.emoji ? null : prev))}
              initial={false}
              animate={{ scale: 1 }}
              transition={{ duration: 0.35, ease: 'easeOut' }}
              className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-sm font-medium transition-all duration-150 border ${reacted ? `bg-white/10 ${postType === 'anuncio' ? 'border-blue-400' : postType === 'pregunta' ? 'border-amber-400' : 'border-emerald-400'} text-white shadow-md` : "bg-transparent/0 border-transparent text-gray-300 hover:bg-white/5"} ${isPending ? 'opacity-80' : ''}`}
              title={`${r.cantidad} reacciones`}
              aria-pressed={reacted}
            >
              <span className="text-base">{r.emoji}</span>
              <span className="text-xs leading-none">{r.cantidad}</span>
            </motion.button>
          );
        })}
      </div>
      {/* Button to open picker */}
      <button
        onClick={e => {
          const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
          const rightSpace = window.innerWidth - rect.right;
          setPickerPosition(rightSpace < 260 ? { right: 0 } : { left: 0 });
          setOpenPicker(v => !v);
        }}
        className="w-6 h-6 flex items-center justify-center rounded-full bg-transparent backdrop-blur-sm border border-white/10 text-emerald-300 hover:bg-white/5 hover:scale-105 transition-transform shadow-sm"
        aria-label="Agregar reacción"
  title={'Agregar reacción'}
      >
        <span className="text-xl">+</span>
      </button>
      {/* Emoji picker popover */}
      {openPicker && (
          <div className="absolute z-50 top-10" style={pickerPosition ?? { left: 0 }}>
            <Picker
              data={data}
              onEmojiSelect={async (emojiObj: any) => {
                setOpenPicker(false);
                if (!emojiObj || !emojiObj.native) return;
                await toggleReaction(emojiObj.native);
              }}
              theme={window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'}
              previewPosition="none"
              skinTonePosition="search"
              style={{ borderRadius: 12, boxShadow: '0 8px 32px rgba(0,0,0,0.18)' }}
            />
          </div>
        )}
    </div>
  );
}
