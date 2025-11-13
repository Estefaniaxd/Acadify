import { AnimatePresence, motion } from "framer-motion";
import {
  Award,
  BarChart,
  Book,
  Building2,
  ChevronRight,
  Edit3,
  Gift,
  LogOut,
  Moon,
  Plus,
  Settings,
  ShoppingBag,
  Star,
  Sun,
  Target,
  TrendingUp,
  User,
  UserCheck,
  Users,
  X,
  Zap,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { avatarAPI } from "../avatar/avatarAPI";
const mockUser = {
  avatar: null, // Será cargado dinámicamente
  name: "Alex Estudiante",
  email: "alex@acadify.com",
  estado: "activo",
  diasActividad: 27,
  diasCharla: 12,
  nivel: 8,
  logros: [
    { id: 1, name: "Primer curso", icon: Book, color: "from-blue-500 to-indigo-600" },
    { id: 2, name: "Participante", icon: Users, color: "from-emerald-500 to-teal-600" },
    { id: 3, name: "Comunidad", icon: Star, color: "from-yellow-500 to-orange-600" },
  ],
};

type SidebarRightProps = { open: boolean; onClose: () => void; role?: string };

export default function SidebarRight({ open, onClose, role = "estudiante" }: SidebarRightProps) {
  // Estado de tema local para el botón
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    try {
      const t = localStorage.getItem("theme");
      return t === "dark" ? "dark" : "light";
    } catch {
      return "light";
    }
  });

  // Estado para el avatar del usuario
  const [userAvatarUrl, setUserAvatarUrl] = useState<string | null>(null);
  const [loadingAvatar, setLoadingAvatar] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    try {
      localStorage.setItem("theme", theme);
    } catch {}
  }, [theme]);

  // Cargar avatar del usuario
  useEffect(() => {
    const loadUserAvatar = async () => {
      if (!user) {
        console.log("🔍 SidebarRight: No user found");
        setLoadingAvatar(false);
        return;
      }

      // Verificar si hay token de autenticación
      const token = localStorage.getItem("access_token");
      if (!token) {
        console.log("🔍 SidebarRight: No auth token found, using fallback avatar");
        setUserAvatarUrl(
          `https://api.dicebear.com/7.x/adventurer/svg?seed=${
            user.username || "user"
          }&backgroundColor=b6e3f4,c0aede,d1d4f9&accessories=glasses&accessoriesProbability=30`
        );
        setLoadingAvatar(false);
        return;
      }

      console.log("🔍 SidebarRight: Loading avatar for user:", user.username);

      try {
        const avatars = await avatarAPI.getMyAvatars();
        console.log("🔍 SidebarRight: Avatars response:", avatars);

        const activeAvatar = avatars.avatars.find((avatar) => avatar.is_active);
        console.log("🔍 SidebarRight: Active avatar:", activeAvatar);

        if (activeAvatar && activeAvatar.image_url) {
          console.log("🔍 SidebarRight: Setting avatar URL:", activeAvatar.image_url);
          setUserAvatarUrl(activeAvatar.image_url);
        } else {
          console.log("🔍 SidebarRight: No active avatar, using fallback");
          // Fallback a un avatar educativo más apropiado para Acadify
          setUserAvatarUrl(
            `https://api.dicebear.com/7.x/adventurer/svg?seed=${
              user.username || "user"
            }&backgroundColor=b6e3f4,c0aede,d1d4f9&accessories=glasses&accessoriesProbability=30`
          );
        }
      } catch (error) {
        console.error("🔍 SidebarRight: Error loading user avatar:", error);
        // Fallback a avatar educativo en caso de error
        setUserAvatarUrl(
          `https://api.dicebear.com/7.x/adventurer/svg?seed=${
            user?.username || "user"
          }&backgroundColor=b6e3f4,c0aede,d1d4f9&accessories=glasses&accessoriesProbability=30`
        );
      } finally {
        setLoadingAvatar(false);
      }
    };

    loadUserAvatar();
  }, [user]);

  // Escuchar actualizaciones de avatar
  useEffect(() => {
    const handleAvatarUpdate = (event: CustomEvent) => {
      const avatarData = event.detail;
      if (avatarData && avatarData.image_url) {
        const urlWithTimestamp = `${avatarData.image_url}?t=${Date.now()}`;
        setUserAvatarUrl(urlWithTimestamp);
      }
    };

    const handleAvatarRefresh = (event: CustomEvent) => {
      console.log("🔄 SidebarRight: Avatar refresh triggered, reloading...");
      // Recargar avatar del usuario
      if (user) {
        loadUserAvatar();
      }
    };

    // Función para recargar avatar (extraída para reutilizar)
    const loadUserAvatar = async () => {
      if (!user) return;

      const token = localStorage.getItem("access_token");
      if (!token) {
        setUserAvatarUrl(
          `https://api.dicebear.com/7.x/adventurer/svg?seed=${
            user.username || "user"
          }&backgroundColor=b6e3f4,c0aede,d1d4f9&accessories=glasses&accessoriesProbability=30`
        );
        return;
      }

      try {
        const avatars = await avatarAPI.getMyAvatars();
        const activeAvatar = avatars.avatars.find((avatar) => avatar.is_active);

        if (activeAvatar && activeAvatar.image_url) {
          const urlWithTimestamp = `${activeAvatar.image_url}?t=${Date.now()}`;
          setUserAvatarUrl(urlWithTimestamp);
        } else {
          setUserAvatarUrl(
            `https://api.dicebear.com/7.x/adventurer/svg?seed=${
              user.username || "user"
            }&backgroundColor=b6e3f4,c0aede,d1d4f9&accessories=glasses&accessoriesProbability=30`
          );
        }
      } catch (error) {
        console.error("🔍 SidebarRight: Error reloading avatar:", error);
        setUserAvatarUrl(
          `https://api.dicebear.com/7.x/adventurer/svg?seed=${
            user.username || "user"
          }&backgroundColor=b6e3f4,c0aede,d1d4f9&accessories=glasses&accessoriesProbability=30`
        );
      }
    };

    window.addEventListener("avatar-updated", handleAvatarUpdate as EventListener);
    window.addEventListener("avatar-refresh", handleAvatarRefresh as EventListener);

    return () => {
      window.removeEventListener("avatar-updated", handleAvatarUpdate as EventListener);
      window.removeEventListener("avatar-refresh", handleAvatarRefresh as EventListener);
    };
  }, []);

  // Menú por rol con iconos React Icons
  const menu = useMemo(() => {
    const userProfilePath = user?.id ? `/perfil/${user.id}` : "/perfil";

    if (role === "admin") {
      return [
        {
          label: "Perfil",
          icon: User,
          path: userProfilePath,
          color: "from-violet-500 to-purple-600",
        },
        { label: "Panel Admin", icon: Settings, path: "/admin", color: "from-red-500 to-pink-600" },
        {
          label: "Instituciones",
          icon: Building2,
          path: "/admin/instituciones",
          color: "from-blue-500 to-indigo-600",
        },
        {
          label: "Usuarios",
          icon: Users,
          path: "/admin/usuarios",
          color: "from-emerald-500 to-teal-600",
        },
        {
          label: "Estadísticas",
          icon: BarChart,
          path: "/admin/estadisticas",
          color: "from-orange-500 to-red-600",
        },
        { label: "Ajustes", icon: Settings, path: "/ajustes", color: "from-gray-500 to-gray-600" },
      ];
    }
    if (role === "coordinador") {
      return [
        {
          label: "Perfil",
          icon: User,
          path: userProfilePath,
          color: "from-violet-500 to-purple-600",
        },
        {
          label: "Panel Coordinador",
          icon: Settings,
          path: "/coordinador",
          color: "from-blue-500 to-indigo-600",
        },
        {
          label: "Mi institución",
          icon: Building2,
          path: "/coordinador/institucion",
          color: "from-emerald-500 to-teal-600",
        },
        {
          label: "Profesores",
          icon: UserCheck,
          path: "/coordinador/profesores",
          color: "from-orange-500 to-red-600",
        },
        {
          label: "Clases",
          icon: Book,
          path: "/coordinador/clases",
          color: "from-purple-500 to-pink-600",
        },
        {
          label: "Estadísticas",
          icon: BarChart,
          path: "/coordinador/estadisticas",
          color: "from-yellow-500 to-orange-600",
        },
        { label: "Ajustes", icon: Settings, path: "/ajustes", color: "from-gray-500 to-gray-600" },
      ];
    }
    if (role === "profesor" || role === "docente") {
      return [
        {
          label: "Perfil",
          icon: User,
          path: userProfilePath,
          color: "from-violet-500 to-purple-600",
        },
        {
          label: "Panel Profesor",
          icon: Settings,
          path: "/profesor",
          color: "from-blue-500 to-indigo-600",
        },
        {
          label: "Mis clases",
          icon: Book,
          path: "/chat-clase",
          color: "from-emerald-500 to-teal-600",
        },
        {
          label: "Tareas",
          icon: UserCheck,
          path: "/profesor/tareas",
          color: "from-orange-500 to-red-600",
        },
        {
          label: "Materiales",
          icon: Book,
          path: "/profesor/materiales",
          color: "from-purple-500 to-pink-600",
        },
        {
          label: "Estadísticas",
          icon: BarChart,
          path: "/profesor/estadisticas",
          color: "from-yellow-500 to-orange-600",
        },
        { label: "Ajustes", icon: Settings, path: "/ajustes", color: "from-gray-500 to-gray-600" },
      ];
    }
    // estudiante o default
    return [
      {
        label: "Perfil",
        icon: User,
        path: userProfilePath,
        color: "from-violet-500 to-purple-600",
      },
      {
        label: "Mis clases",
        icon: Book,
        path: "/chat-clase",
        color: "from-blue-500 to-indigo-600",
      },
      {
        label: "Unirse a clase",
        icon: Plus,
        path: "/unirse-clase",
        color: "from-emerald-500 to-teal-600",
      },
      { label: "Tienda", icon: ShoppingBag, path: "/tienda", color: "from-orange-500 to-red-600" },
      { label: "Logros", icon: Award, path: "/logros", color: "from-yellow-500 to-orange-600" },
      { label: "Avatar", icon: User, path: "/avatar", color: "from-purple-500 to-pink-600" },
      {
        label: "Explorar Avatares",
        icon: Users,
        path: "/explorar-avatares",
        color: "from-indigo-500 to-purple-600",
      },
      { label: "Ajustes", icon: Settings, path: "/ajustes", color: "from-gray-500 to-gray-600" },
    ];
  }, [role, user]);

  // Insignias premium
  const badges = [
    { id: 1, name: "Colaborador", icon: Users, color: "from-blue-500 to-indigo-600" },
    { id: 2, name: "Explorador", icon: Target, color: "from-emerald-500 to-teal-600" },
    { id: 3, name: "Maestro", icon: Star, color: "from-yellow-500 to-orange-600" },
    { id: 4, name: "Innovador", icon: Zap, color: "from-purple-500 to-pink-600" },
  ];

  const progreso = 75; // %
  const navigate = useNavigate();
  const { logout } = useAuth();

  // Fondo igual que SidebarLeft
  const [isDark, setIsDark] = useState(false);
  useEffect(() => {
    if (typeof window !== "undefined" && window.matchMedia) {
      const match = window.matchMedia("(prefers-color-scheme: dark)");
      setIsDark(match.matches);
      const handler = (e: MediaQueryListEvent) => setIsDark(e.matches);
      match.addEventListener("change", handler);
      return () => match.removeEventListener("change", handler);
    }
  }, []);

  const darkBg = "rgba(24, 16, 48, 0.92)";
  const sidebarBg = isDark ? darkBg : "#fff";
  const borderColor = isDark ? "1px solid rgba(139, 92, 246, 0.35)" : "1px solid #e5e7eb";
  const boxShadow = isDark
    ? "8px 0 32px rgba(139, 92, 246, 0.18)"
    : "8px 0 32px rgba(139, 92, 246, 0.04)";

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ x: 420, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 420, opacity: 0 }}
          transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
          className="fixed top-0 right-0 h-full z-40 w-96 max-w-[420px] shadow-2xl overflow-hidden"
          style={{
            background: sidebarBg,
            backdropFilter: "blur(25px)",
            WebkitBackdropFilter: "blur(25px)",
            borderLeft: borderColor,
            boxShadow: boxShadow,
          }}
          tabIndex={-1}
          aria-modal="true"
          role="dialog"
        >
          {/* Header premium con efecto holográfico */}
          <div className="relative overflow-hidden">
            <div
              className="flex items-center justify-between px-6 py-5 relative z-10"
              style={{
                background:
                  "linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(124, 58, 237, 0.15) 100%)",
                borderBottom: "1px solid rgba(139, 92, 246, 0.2)",
              }}
            >
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
                className="flex items-center gap-3"
              >
                <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-violet-600 to-purple-700 flex items-center justify-center shadow-lg">
                  <User className="w-5 h-5 text-white" />
                </div>
                <span
                  className={`text-xl font-bold bg-clip-text ${
                    isDark ? "text-gray-100" : "text-gray-900"
                  }`}
                >
                  Tu perfil
                </span>
              </motion.div>
              <motion.button
                onClick={onClose}
                className="p-2 rounded-xl hover:bg-white/50 text-gray-600 hover:text-violet-600 transition-all duration-300"
                whileHover={{ scale: 1.1, rotate: 90 }}
                whileTap={{ scale: 0.9 }}
              >
                <X className="w-5 h-5" />
              </motion.button>
            </div>
            {/* Efecto de ondas de fondo */}
            <motion.div
              className="absolute inset-0 opacity-30"
              animate={{
                background: [
                  "radial-gradient(circle at 20% 50%, rgba(139, 92, 246, 0.3) 0%, transparent 50%)",
                  "radial-gradient(circle at 80% 50%, rgba(124, 58, 237, 0.3) 0%, transparent 50%)",
                  "radial-gradient(circle at 20% 50%, rgba(139, 92, 246, 0.3) 0%, transparent 50%)",
                ],
              }}
              transition={{ duration: 4, repeat: Infinity }}
            />
          </div>

          <div className="px-6 py-6 overflow-y-auto h-[calc(100vh-80px)] flex flex-col gap-6">
            {/* Perfil de usuario con avatar 3D */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="flex flex-col items-center gap-4 relative"
            >
              <motion.div
                className="relative"
                whileHover={{ scale: 1.05, rotateY: 15 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                {open ? (
                  <div className="w-32 h-32 rounded-3xl overflow-hidden shadow-2xl border-4 border-white/50 relative">
                    {loadingAvatar ? (
                      <div className="w-full h-full bg-gray-200 dark:bg-gray-700 animate-pulse flex items-center justify-center">
                        <div className="w-8 h-8 border-2 border-violet-600 border-t-transparent rounded-full animate-spin"></div>
                      </div>
                    ) : (
                      <>
                        <img
                          src={
                            userAvatarUrl ||
                            `https://api.dicebear.com/7.x/avataaars/svg?seed=${
                              user?.username || "acadify"
                            }&backgroundColor=b6e3f4,c0aede,d1d4f9`
                          }
                          alt="avatar"
                          className="w-full h-full object-cover object-top scale-125 transform origin-center"
                          style={{
                            objectPosition: "center 22%",
                            clipPath: "inset(0 0 20% 0)",
                          }}
                          onError={(e) => {
                            e.currentTarget.src = `https://api.dicebear.com/7.x/adventurer/svg?seed=${
                              user?.username || "acadify"
                            }&backgroundColor=b6e3f4,c0aede,d1d4f9&accessories=glasses&accessoriesProbability=30`;
                          }}
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-violet-600/20 to-transparent" />
                      </>
                    )}
                  </div>
                ) : (
                  <div className="w-12 h-12 flex items-center justify-center">
                    {loadingAvatar ? (
                      <div className="w-full h-full bg-gray-200 dark:bg-gray-700 animate-pulse flex items-center justify-center rounded-full">
                        <div className="w-4 h-4 border-2 border-violet-600 border-t-transparent rounded-full animate-spin"></div>
                      </div>
                    ) : (
                      <img
                        src={
                          userAvatarUrl ||
                          `https://api.dicebear.com/7.x/avataaars/svg?seed=${
                            user?.username || "acadify"
                          }&backgroundColor=b6e3f4,c0aede,d1d4f9`
                        }
                        alt="avatar"
                        className="w-12 h-12 object-cover object-top scale-150 transform origin-center"
                        style={{
                          objectPosition: "center 18%",
                          clipPath: "circle(50% at 50% 38%)",
                          background: "none",
                        }}
                        onError={(e) => {
                          e.currentTarget.src = `https://api.dicebear.com/7.x/adventurer/svg?seed=${
                            user?.username || "acadify"
                          }&backgroundColor=b6e3f4,c0aede,d1d4f9&accessories=glasses&accessoriesProbability=30`;
                        }}
                      />
                    )}
                  </div>
                )}
                {/* Indicador de estado en vivo */}
                <motion.div
                  className="absolute -bottom-1 -right-1 w-8 h-8 bg-green-500 rounded-full border-4 border-white shadow-lg flex items-center justify-center"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <div className="w-3 h-3 bg-white rounded-full" />
                </motion.div>
              </motion.div>

              <div className="text-center">
                <h3 className={`text-xl font-bold ${isDark ? "text-gray-100" : "text-gray-800"}`}>
                  {user?.username || "Usuario"}
                </h3>
                <p className={`text-sm ${isDark ? "text-gray-400" : "text-gray-500"}`}>
                  {user?.email || "usuario@acadify.com"}
                </p>
                <motion.button
                  className="text-xs text-violet-600 hover:text-violet-700 font-medium flex items-center gap-1 mt-2 mx-auto"
                  onClick={() => navigate("/avatar")}
                  whileHover={{ scale: 1.05 }}
                >
                  <Edit3 className="w-3 h-3" />
                  Personalizar avatar
                </motion.button>
              </div>

              {/* Estadísticas de actividad */}
              <div className="flex gap-6 mt-2">
                <motion.div className="flex flex-col items-center" whileHover={{ scale: 1.05 }}>
                  <span className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-violet-600 to-purple-600">
                    {mockUser.diasActividad}
                  </span>
                  <span className="text-xs text-gray-500">Días activo</span>
                </motion.div>
                <motion.div className="flex flex-col items-center" whileHover={{ scale: 1.05 }}>
                  <span className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-teal-600">
                    {mockUser.diasCharla}
                  </span>
                  <span className="text-xs text-gray-500">Días social</span>
                </motion.div>
                <motion.div className="flex flex-col items-center" whileHover={{ scale: 1.05 }}>
                  <span className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-500 to-orange-600">
                    {mockUser.nivel}
                  </span>
                  <span className="text-xs text-gray-500">Nivel</span>
                </motion.div>
              </div>
            </motion.div>

            {/* Progreso de nivel con animaciones */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="relative"
            >
              <div className="flex items-center justify-between mb-3">
                <h4
                  className={`text-lg font-bold flex items-center gap-2 ${
                    isDark ? "text-emerald-300" : "text-emerald-600"
                  }`}
                >
                  <TrendingUp className="w-4 h-4 text-emerald-500" />
                  Progreso de nivel
                </h4>
                <span className="text-sm text-gray-500 font-medium">{progreso}%</span>
              </div>
              <div className="relative w-full h-4 bg-gray-200 rounded-full overflow-hidden shadow-inner">
                <motion.div
                  className="h-4 bg-gradient-to-r from-emerald-400 via-teal-500 to-emerald-600 relative rounded-full shadow-lg"
                  initial={{ width: 0 }}
                  animate={{ width: `${progreso}%` }}
                  transition={{ delay: 0.4, duration: 1.2, ease: "easeOut" }}
                >
                  {/* Efecto de brillo animado */}
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent"
                    animate={{
                      x: ["-100%", "100%"],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      repeatDelay: 3,
                    }}
                  />
                </motion.div>
              </div>
              <p className="text-xs text-gray-400 mt-2 text-center">
                ¡{100 - progreso}% más para alcanzar el nivel {mockUser.nivel + 1}!
              </p>
            </motion.div>

            {/* Insignias premium */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 }}
            >
              <div className="flex items-center justify-between mb-3">
                <h4
                  className={`text-lg font-bold flex items-center gap-2 ${
                    isDark ? "text-yellow-300" : "text-yellow-600"
                  }`}
                >
                  <Award className="w-4 h-4 text-yellow-500" />
                  Insignias
                </h4>
                <motion.button
                  className="text-sm text-violet-600 hover:text-violet-700 font-medium flex items-center gap-1"
                  onClick={() => navigate("/insignias")}
                  whileHover={{ x: 2 }}
                >
                  Ver todas <ChevronRight className="w-3 h-3" />
                </motion.button>
              </div>
              <div className="grid grid-cols-4 gap-3">
                {badges.map((badge, idx) => {
                  const Icon = badge.icon;
                  return (
                    <motion.div
                      key={badge.id}
                      className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${badge.color} flex items-center justify-center shadow-lg border border-white/20 relative overflow-hidden`}
                      title={badge.name}
                      initial={{ opacity: 0, scale: 0.5 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.1 * idx, type: "spring", stiffness: 300 }}
                      whileHover={{ scale: 1.1, rotate: 5 }}
                    >
                      <Icon className="w-5 h-5 text-white" />
                      {/* Efecto de brillo */}
                      <motion.div
                        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent opacity-0 hover:opacity-100"
                        animate={{
                          x: ["-100%", "100%"],
                        }}
                        transition={{
                          duration: 1.5,
                          repeat: Infinity,
                          repeatDelay: 3,
                        }}
                      />
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>

            {/* Logros recientes */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <div className="flex items-center justify-between mb-3">
                <h4
                  className={`text-lg font-bold flex items-center gap-2 ${
                    isDark ? "text-gray-100" : "text-gray-700"
                  }`}
                >
                  <Gift className="w-4 h-4 text-purple-500" />
                  Logros recientes
                </h4>
                <motion.button
                  className="text-sm text-violet-600 hover:text-violet-700 font-medium flex items-center gap-1"
                  onClick={() => navigate("/logros")}
                  whileHover={{ x: 2 }}
                >
                  Ver todos <ChevronRight className="w-3 h-3" />
                </motion.button>
              </div>
              <div className="grid gap-2">
                {mockUser.logros.map((logro, idx) => {
                  const Icon = logro.icon;
                  return (
                    <motion.div
                      key={logro.id}
                      className={`flex items-center gap-3 p-3 rounded-2xl shadow-sm border border-purple-100 hover:border-purple-200 transition-all duration-300 ${
                        isDark ? "" : "bg-gray-50"
                      }`}
                      style={
                        isDark
                          ? {
                              background:
                                "linear-gradient(135deg, rgba(40, 20, 80, 0.10) 0%, rgba(139, 92, 246, 0.10) 100%)",
                            }
                          : {}
                      }
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.1 * idx }}
                      whileHover={{ scale: 1.02 }}
                    >
                      <motion.div
                        className={`w-10 h-10 rounded-xl bg-gradient-to-br ${logro.color} flex items-center justify-center shadow-md`}
                        whileHover={{ rotate: 10, scale: 1.1 }}
                      >
                        <Icon className="w-4 h-4 text-white" />
                      </motion.div>
                      <div>
                        <h5
                          className={`font-semibold text-sm ${
                            isDark ? "text-gray-100" : "text-gray-800"
                          }`}
                        >
                          {logro.name}
                        </h5>
                        <p className={`text-xs ${isDark ? "text-gray-400" : "text-gray-500"}`}>
                          Desbloqueado recientemente
                        </p>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>

            {/* Menú de acciones */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35 }}
              className="border-t border-gray-200 pt-4"
            >
              {/* Botón de tema */}
              <motion.button
                className="w-full flex items-center gap-3 px-4 py-3 rounded-2xl mb-2 transition-all duration-300 group"
                style={{
                  background: isDark
                    ? "linear-gradient(135deg, rgba(40, 20, 80, 0.10) 0%, rgba(139, 92, 246, 0.10) 100%)"
                    : "linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,250,252,0.95) 100%)",
                  border: isDark ? "1px solid #312e81" : "1px solid #ede9fe",
                }}
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <motion.div
                  className="w-10 h-10 rounded-xl flex items-center justify-center"
                  style={{
                    background: isDark
                      ? "linear-gradient(135deg, rgba(40, 20, 80, 0.10) 0%, rgba(139, 92, 246, 0.10) 100%)"
                      : "linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,250,252,0.95) 100%)",
                    border: isDark ? "1px solid #312e81" : "1px solid #ede9fe",
                  }}
                  animate={{ rotate: theme === "dark" ? 180 : 0 }}
                  transition={{ duration: 0.3 }}
                >
                  {theme === "dark" ? (
                    <Sun className="w-5 h-5 text-yellow-500" />
                  ) : (
                    <Moon className="w-5 h-5 text-purple-600" />
                  )}
                </motion.div>
                <span
                  className={`font-medium ${
                    isDark ? "text-gray-200" : "text-gray-700"
                  } group-hover:text-violet-700`}
                >
                  Modo {theme === "dark" ? "claro" : "oscuro"}
                </span>
              </motion.button>

              {/* Menú principal */}
              {menu.slice(0, -1).map((item, idx) => {
                const Icon = item.icon;
                return (
                  <motion.button
                    key={item.label}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-2xl mb-2 transition-all duration-300 group ${
                      isDark ? "hover:bg-violet-900/30" : "hover:bg-violet-50"
                    }`}
                    onClick={() => item.path && navigate(item.path)}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.05 * idx }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <motion.div
                      className={`w-10 h-10 rounded-xl bg-gradient-to-br ${item.color} flex items-center justify-center shadow-md`}
                      whileHover={{ rotate: 5, scale: 1.1 }}
                    >
                      <Icon className="w-5 h-5 text-white" />
                    </motion.div>
                    <span
                      className={`font-medium transition-colors duration-300 ${
                        isDark
                          ? "text-gray-200 group-hover:text-violet-300"
                          : "text-gray-800 group-hover:text-violet-700"
                      }`}
                    >
                      {item.label}
                    </span>
                  </motion.button>
                );
              })}

              {/* Botón de cerrar sesión premium */}
              <motion.button
                onClick={() => {
                  logout();
                  onClose();
                  navigate("/");
                }}
                className="w-full flex items-center gap-3 px-4 py-4 rounded-2xl bg-gradient-to-r from-red-500 to-pink-600 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300 mt-4 relative overflow-hidden"
                whileHover={{ scale: 1.02, y: -1 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
                  <LogOut className="w-5 h-5" />
                </div>
                <span>Cerrar sesión</span>
                {/* Efecto de brillo */}
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 hover:opacity-100"
                  animate={{
                    x: ["-100%", "100%"],
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    repeatDelay: 2,
                  }}
                />
              </motion.button>
            </motion.div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
