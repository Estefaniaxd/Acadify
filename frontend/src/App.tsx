import { lazy, Suspense, useEffect, useState } from "react";
import { Route, Routes, useLocation } from "react-router-dom";
import AuthLayout from "./components/layout/AuthLayout";
import Layout from "./components/layout/Layout";
import { Spinner } from "./components/ui";
import { ToastProvider } from "./context/ToastContext";
import { RachaProvider } from "./context/RachaProvider";

/* ============================================
   CÓDIGO CRÍTICO - Carga inmediata
   ============================================ */
// Solo Home se carga inmediatamente (landing page)
import { Home } from "./pages/home";

/* ============================================
   LAZY LOADING - Code Splitting por Feature
   ============================================ */

// Auth pages - Bundle: ~150KB
const Login = lazy(() => import("./pages/auth/Login"));
const Register = lazy(() => import("./pages/auth/Register"));
const RecoverPassword = lazy(() => import("./pages/auth/RecoverPassword"));
const ResetPassword = lazy(() => import("./pages/auth/ResetPassword"));

// Dashboards - Bundle: ~200KB (separado por rol)
const DashboardPage = lazy(() =>
  import("./pages/dashboard").then((m) => ({ default: m.DashboardPage }))
);
const DashboardAdmin = lazy(() =>
  import("./pages/dashboard").then((m) => ({ default: m.DashboardAdmin }))
);
const DashboardCoordinador = lazy(() =>
  import("./pages/dashboard").then((m) => ({ default: m.DashboardCoordinador }))
);
const DashboardTeacher = lazy(() =>
  import("./pages/dashboard").then((m) => ({ default: m.DashboardTeacher }))
);
const DashboardStudent = lazy(() =>
  import("./pages/dashboard").then((m) => ({ default: m.DashboardStudent }))
);

// Páginas académicas - Bundle: ~180KB
const CursosPage = lazy(() => import("./pages/cursos").then((m) => ({ default: m.CursosPage })));
const ClasePage = lazy(() => import("./pages/cursos").then((m) => ({ default: m.ClasePage })));
const EvaluacionesPage = lazy(() =>
  import("./pages/cursos").then((m) => ({ default: m.EvaluacionesPage }))
);

// Proctoring Test - Bundle: ~50KB (componente de pruebas)
const ProctoringTest = lazy(() =>
  import("./modules/evaluaciones/components/proctoring/ProctoringTest").then((m) => ({
    default: m.ProctoringTest,
  }))
);

// Gamificación - Bundle: ~100KB
const DashboardGamificacion = lazy(() => import("./pages/gamificacion/DashboardGamificacion"));
const LogrosPage = lazy(() =>
  import("./pages/gamificacion").then((m) => ({ default: m.LogrosPage }))
);
const InsigniasPage = lazy(() =>
  import("./pages/gamificacion").then((m) => ({ default: m.InsigniasPage }))
);
const MisionesPage = lazy(() =>
  import("./pages/MisionesPage").then((m) => ({ default: m.default }))
);
const LogrosUsuario = lazy(() => import("./modules/logros"));
const PuntosUsuario = lazy(() => import("./modules/puntos"));
const NivelesUsuario = lazy(() => import("./modules/niveles"));
const TiendaPuntos = lazy(() => import("./modules/tienda"));

// Comunicación - Bundle: ~120KB
const ModuloComunicacion = lazy(() => import("./modules/comunicacion"));
const ComunicacionPage = lazy(() =>
  import("./pages/comunicacion/ComunicacionPage").then((m) => ({ default: m.ComunicacionPage }))
);

// Videollamadas - Bundle: ~150KB
const VideollamadasPage = lazy(() => import("./pages/VideollamadasPage"));

// Configuración - Bundle: ~80KB
const AjustesPage = lazy(() =>
  import("./pages/configuracion").then((m) => ({ default: m.AjustesPage }))
);
const AyudaFaqPage = lazy(() =>
  import("./pages/configuracion").then((m) => ({ default: m.AyudaFaqPage }))
);
const NotificacionesPage = lazy(() =>
  import("./pages/configuracion").then((m) => ({ default: m.NotificacionesPage }))
);
const ConfiguracionNotificacionesPage = lazy(
  () => import("./pages/configuracion/ConfiguracionNotificacionesPage")
);
const PanelNotificacionesPage = lazy(() => import("./pages/PanelNotificacionesPage"));

// Avatar - Bundle: ~150KB (pesado por SVG editor)
const AvatarCustomizerPage = lazy(() => import("./pages/avatar/AvatarCustomizerPage"));
const EditorAvatar = lazy(() => import("./modules/avatar/EditorAvatar"));

// Clase específica - Bundle: ~90KB
const TablonPage = lazy(() => import("./pages/clase/TablonPage"));
const MaterialesPage = lazy(() => import("./pages/clase/MaterialesPage"));
const TareasPage = lazy(() => import("./pages/clase/TareasPage"));
const CalificacionesPage = lazy(() => import("./pages/clase/CalificacionesPage"));
const PersonasPage = lazy(() => import("./pages/clase/PersonasPage"));
const ChatClasePage = lazy(() => import("./pages/clase/ChatClasePage"));

// Tareas - Bundle: ~120KB
const TareaDetallePage = lazy(() => import("./pages/tareas/TareaDetallePage"));

// Legal - Bundle: ~30KB (poco acceso)
const TratamientoDatos = lazy(() => import("./pages/legal/TratamientoDatos"));
const Consentimiento = lazy(() => import("./pages/legal/Consentimiento"));

// Perfil - Bundle: ~100KB
const ProfilePage = lazy(() => import("./modules/perfil/ProfilePage"));

// Admin - Instituciones - Bundle: ~120KB
// const ListaInstituciones = lazy(() => import('./modules/instituciones').then(m => ({ default: m.ListaInstituciones }))); // Old module version
const FormularioInstitucion = lazy(() =>
  import("./modules/instituciones").then((m) => ({ default: m.FormularioInstitucion }))
);
const AdminInstitucionesPage = lazy(() => import("./pages/admin/AdminInstitucionesPage"));
const AdminUsuariosPendientesPage = lazy(() => import("./pages/admin/AdminUsuariosPendientesPage"));
const AdminReportesPage = lazy(() => import("./pages/admin/AdminReportesPage"));
const AdminTiendaPage = lazy(() => import("./pages/admin/AdminTiendaPage"));
const AdminLogrosPage = lazy(() => import("./pages/admin/AdminLogrosPage"));

// Admin - Programas - Bundle: ~140KB
const ListaProgramas = lazy(() =>
  import("./modules/programas").then((m) => ({ default: m.ListaProgramas }))
);
const FormularioPrograma = lazy(() =>
  import("./modules/programas").then((m) => ({ default: m.FormularioPrograma }))
);
const DetallePrograma = lazy(() =>
  import("./modules/programas").then((m) => ({ default: m.DetallePrograma }))
);

// Admin - Invitaciones - Bundle: ~130KB
const ListaInvitaciones = lazy(() =>
  import("./modules/invitaciones").then((m) => ({ default: m.ListaInvitaciones }))
);

// Invitaciones - Página pública - Bundle: ~90KB
const AceptarInvitacion = lazy(() =>
  import("./modules/invitaciones").then((m) => ({ default: m.AceptarInvitacion }))
);
const RegistroCoordinadorPage = lazy(() =>
  import("./modules/invitaciones").then((m) => ({ default: m.RegistroCoordinadorPage }))
);
const AceptarInvitacionPage = lazy(() =>
  import("./pages/invitaciones/AceptarInvitacionPage").then((m) => ({ default: m.default }))
);
const UsarCodigoInvitacionPage = lazy(() =>
  import("./pages/invitaciones/UsarCodigoInvitacionPage").then((m) => ({ default: m.default }))
);
const CoordinadorInstitucionPage = lazy(() =>
  import("./pages/coordinador/CoordinadorInstitucionPageV2").then((m) => ({ default: m.default }))
);

/* ============================================
   COMPONENTE DE LOADING PARA SUSPENSE
   Definido fuera de App() para evitar recreación
   ============================================ */
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-neutral-950 dark:via-violet-950/20 dark:to-neutral-900">
    <div className="text-center space-y-4">
      <Spinner size="lg" variant="primary" />
      <p className="text-sm text-neutral-600 dark:text-neutral-400 animate-pulse">Cargando...</p>
    </div>
  </div>
);

export default function App() {
  const location = useLocation();
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    try {
      const t = localStorage.getItem("theme");
      return t === "dark" ? "dark" : "light";
    } catch {
      // Si falla localStorage, usar tema claro por defecto
      return "light";
    }
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    try {
      localStorage.setItem("theme", theme);
    } catch {
      // Ignorar errores de localStorage (ej: modo incógnito)
    }
  }, [theme]);

  const authPages = ["/login", "/register", "/recover", "/reset-password"];
  const isAuthPage = authPages.includes(location.pathname);

  const routes = (
    <Routes>
      {/* Página principal - Sin Suspense (ya cargada) */}
      <Route path="/" element={<Home />} />
      {/* Autenticación - Lazy loaded */}
      <Route
        path="/login"
        element={
          <Suspense fallback={<PageLoader />}>
            <Login />
          </Suspense>
        }
      />
      <Route
        path="/register"
        element={
          <Suspense fallback={<PageLoader />}>
            <Register />
          </Suspense>
        }
      />
      <Route
        path="/recover"
        element={
          <Suspense fallback={<PageLoader />}>
            <RecoverPassword />
          </Suspense>
        }
      />
      <Route
        path="/reset-password"
        element={
          <Suspense fallback={<PageLoader />}>
            <ResetPassword />
          </Suspense>
        }
      />
      {/* Dashboard principal - Lazy loaded */}
      <Route
        path="/dashboard"
        element={
          <Suspense fallback={<PageLoader />}>
            <DashboardPage />
          </Suspense>
        }
      />
      {/* Dashboards por rol - Lazy loaded */}
      <Route
        path="/dashboard-admin"
        element={
          <Suspense fallback={<PageLoader />}>
            <DashboardAdmin />
          </Suspense>
        }
      />
      <Route
        path="/dashboard-coordinador"
        element={
          <Suspense fallback={<PageLoader />}>
            <DashboardCoordinador />
          </Suspense>
        }
      />
      <Route
        path="/dashboard-teacher"
        element={
          <Suspense fallback={<PageLoader />}>
            <DashboardTeacher />
          </Suspense>
        }
      />
      <Route
        path="/dashboard-student"
        element={
          <Suspense fallback={<PageLoader />}>
            <DashboardStudent />
          </Suspense>
        }
      />
      {/* Páginas principales - Lazy loaded */}
      <Route
        path="/panel-notificaciones"
        element={
          <Suspense fallback={<PageLoader />}>
            <PanelNotificacionesPage />
          </Suspense>
        }
      />
      <Route
        path="/notificaciones"
        element={
          <Suspense fallback={<PageLoader />}>
            <NotificacionesPage />
          </Suspense>
        }
      />
      <Route
        path="/configuracion/notificaciones"
        element={
          <Suspense fallback={<PageLoader />}>
            <ConfiguracionNotificacionesPage />
          </Suspense>
        }
      />
      <Route
        path="/mensajes"
        element={
          <Suspense fallback={<PageLoader />}>
            <ModuloComunicacion />
          </Suspense>
        }
      />
      <Route
        path="/comunicacion"
        element={
          <Suspense fallback={<PageLoader />}>
            <ComunicacionPage />
          </Suspense>
        }
      />
      <Route
        path="/videollamadas"
        element={
          <Suspense fallback={<PageLoader />}>
            <VideollamadasPage />
          </Suspense>
        }
      />
      {/* Admin - Nuevas páginas administrativas */}
      <Route
        path="/admin/instituciones"
        element={
          <Suspense fallback={<PageLoader />}>
            <AdminInstitucionesPage />
          </Suspense>
        }
      />
      <Route
        path="/admin/instituciones/crear"
        element={
          <Suspense fallback={<PageLoader />}>
            <FormularioInstitucion modo="crear" />
          </Suspense>
        }
      />
      <Route
        path="/admin/instituciones/:id/editar"
        element={
          <Suspense fallback={<PageLoader />}>
            <FormularioInstitucion modo="editar" />
          </Suspense>
        }
      />
      <Route
        path="/admin/usuarios-pendientes"
        element={
          <Suspense fallback={<PageLoader />}>
            <AdminUsuariosPendientesPage />
          </Suspense>
        }
      />
      <Route
        path="/admin/reportes"
        element={
          <Suspense fallback={<PageLoader />}>
            <AdminReportesPage />
          </Suspense>
        }
      />
      <Route
        path="/admin/tienda"
        element={
          <Suspense fallback={<PageLoader />}>
            <AdminTiendaPage />
          </Suspense>
        }
      />
      <Route
        path="/admin/logros"
        element={
          <Suspense fallback={<PageLoader />}>
            <AdminLogrosPage />
          </Suspense>
        }
      />
      {/* Programas */}
      <Route
        path="/admin/programas"
        element={
          <Suspense fallback={<PageLoader />}>
            <ListaProgramas />
          </Suspense>
        }
      />
      <Route
        path="/admin/programas/crear"
        element={
          <Suspense fallback={<PageLoader />}>
            <FormularioPrograma modo="crear" />
          </Suspense>
        }
      />
      <Route
        path="/admin/programas/:id"
        element={
          <Suspense fallback={<PageLoader />}>
            <DetallePrograma />
          </Suspense>
        }
      />
      <Route
        path="/admin/programas/:id/editar"
        element={
          <Suspense fallback={<PageLoader />}>
            <FormularioPrograma modo="editar" />
          </Suspense>
        }
      />
      {/* Admin - Invitaciones - Lazy loaded */}
      <Route
        path="/admin/invitaciones"
        element={
          <Suspense fallback={<PageLoader />}>
            <ListaInvitaciones />
          </Suspense>
        }
      />
      {/* Invitaciones públicas (sin autenticación) - Lazy loaded */}
      <Route
        path="/invitacion/aceptar/:token"
        element={
          <Suspense fallback={<PageLoader />}>
            <AceptarInvitacion />
          </Suspense>
        }
      />
      <Route
        path="/invitaciones/aceptar"
        element={
          <Suspense fallback={<PageLoader />}>
            <AceptarInvitacionPage />
          </Suspense>
        }
      />
      <Route
        path="/invitaciones/usar-codigo"
        element={
          <Suspense fallback={<PageLoader />}>
            <UsarCodigoInvitacionPage />
          </Suspense>
        }
      />
      <Route
        path="/registro-coordinador"
        element={
          <Suspense fallback={<PageLoader />}>
            <RegistroCoordinadorPage />
          </Suspense>
        }
      />
      <Route
        path="/coordinador/institucion"
        element={
          <Suspense fallback={<PageLoader />}>
            <CoordinadorInstitucionPage />
          </Suspense>
        }
      />
      {/* Académico - Lazy loaded */}
      <Route
        path="/cursos"
        element={
          <Suspense fallback={<PageLoader />}>
            <CursosPage />
          </Suspense>
        }
      />
      <Route
        path="/clase/:id"
        element={
          <Suspense fallback={<PageLoader />}>
            <ClasePage />
          </Suspense>
        }
      />
      <Route
        path="/evaluaciones"
        element={
          <Suspense fallback={<PageLoader />}>
            <EvaluacionesPage />
          </Suspense>
        }
      />
      <Route
        path="/evaluaciones/proctoring-test"
        element={
          <Suspense fallback={<PageLoader />}>
            <ProctoringTest />
          </Suspense>
        }
      />
      {/* Clase específica - Lazy loaded */}
      <Route
        path="/clase/:id/tablon"
        element={
          <Suspense fallback={<PageLoader />}>
            <TablonPage />
          </Suspense>
        }
      />
      <Route
        path="/clase/:id/materiales"
        element={
          <Suspense fallback={<PageLoader />}>
            <MaterialesPage />
          </Suspense>
        }
      />
      <Route
        path="/clase/:id/tareas"
        element={
          <Suspense fallback={<PageLoader />}>
            <TareasPage />
          </Suspense>
        }
      />
      <Route
        path="/clase/:id/calificaciones"
        element={
          <Suspense fallback={<PageLoader />}>
            <CalificacionesPage />
          </Suspense>
        }
      />
      <Route
        path="/clase/:id/personas"
        element={
          <Suspense fallback={<PageLoader />}>
            <PersonasPage />
          </Suspense>
        }
      />
      <Route
        path="/clase/:id/chat"
        element={
          <Suspense fallback={<PageLoader />}>
            <ChatClasePage />
          </Suspense>
        }
      />
      {/* Tareas - Lazy loaded */}
      <Route
        path="/cursos/:cursoId/tareas/:tareaId"
        element={
          <Suspense fallback={<PageLoader />}>
            <TareaDetallePage />
          </Suspense>
        }
      />
      {/* Gamificación - Lazy loaded */}
      <Route
        path="/gamificacion"
        element={
          <Suspense fallback={<PageLoader />}>
            <DashboardGamificacion />
          </Suspense>
        }
      />
      <Route
        path="/logros"
        element={
          <Suspense fallback={<PageLoader />}>
            <LogrosPage />
          </Suspense>
        }
      />
      <Route
        path="/insignias"
        element={
          <Suspense fallback={<PageLoader />}>
            <InsigniasPage />
          </Suspense>
        }
      />
      <Route
        path="/misiones"
        element={
          <Suspense fallback={<PageLoader />}>
            <MisionesPage />
          </Suspense>
        }
      />
      <Route
        path="/logros-usuario"
        element={
          <Suspense fallback={<PageLoader />}>
            <LogrosUsuario />
          </Suspense>
        }
      />
      <Route
        path="/puntos"
        element={
          <Suspense fallback={<PageLoader />}>
            <PuntosUsuario />
          </Suspense>
        }
      />
      <Route
        path="/niveles"
        element={
          <Suspense fallback={<PageLoader />}>
            <NivelesUsuario />
          </Suspense>
        }
      />
      <Route
        path="/tienda"
        element={
          <Suspense fallback={<PageLoader />}>
            <TiendaPuntos />
          </Suspense>
        }
      />{" "}
      {/* Usuario y configuración - Lazy loaded */}
      <Route
        path="/perfil"
        element={
          <Suspense fallback={<PageLoader />}>
            <ProfilePage />
          </Suspense>
        }
      />
      <Route
        path="/perfil/:userId"
        element={
          <Suspense fallback={<PageLoader />}>
            <ProfilePage />
          </Suspense>
        }
      />
      <Route
        path="/ajustes"
        element={
          <Suspense fallback={<PageLoader />}>
            <AjustesPage theme={theme} setTheme={setTheme} />
          </Suspense>
        }
      />
      <Route
        path="/ayuda"
        element={
          <Suspense fallback={<PageLoader />}>
            <AyudaFaqPage />
          </Suspense>
        }
      />
      {/* Avatar - Lazy loaded (pesado) */}
      <Route
        path="/avatar"
        element={
          <Suspense fallback={<PageLoader />}>
            <AvatarCustomizerPage />
          </Suspense>
        }
      />
      <Route
        path="/editor-avatar"
        element={
          <Suspense fallback={<PageLoader />}>
            <EditorAvatar />
          </Suspense>
        }
      />
      {/* Páginas legales - Lazy loaded */}
      <Route
        path="/tratamiento-datos"
        element={
          <Suspense fallback={<PageLoader />}>
            <TratamientoDatos />
          </Suspense>
        }
      />
      <Route
        path="/consentimiento"
        element={
          <Suspense fallback={<PageLoader />}>
            <Consentimiento />
          </Suspense>
        }
      />
    </Routes>
  );

  return (
    <ToastProvider>
      <RachaProvider>
        {isAuthPage ? (
          <AuthLayout>{routes}</AuthLayout>
        ) : (
          <Layout>
            <main>{routes}</main>
          </Layout>
        )}
      </RachaProvider>
    </ToastProvider>
  );
}
