/**
 * Configuración centralizada de navegación por roles
 * Aplica principio de responsabilidad única (SRP) y abierto/cerrado (OCP)
 */

;
;
import type { IconType } from 'react-icons';
import { Award, BarChart, Book, Building2, Calendar, CheckCircle, Database, Edit, FileText, Home, Info, MessageSquare, Plus, Settings, ShoppingBag, Target, TrendingUp, User, Users } from 'lucide-react';

export type UserRole = 'admin' | 'administrador' | 'coordinador' | 'profesor' | 'docente' | 'estudiante' | 'guest';

export interface NavigationItem {
  label: string;
  href: string;
  icon: IconType;
  description?: string;
  badge?: string;
  roles: UserRole[]; // Roles que pueden ver este ítem
  section?: 'main' | 'academic' | 'management' | 'social' | 'tools'; // Agrupación lógica
}

/**
 * Definición completa de navegación
 * Cada item especifica explícitamente qué roles pueden acceder
 */
export const NAVIGATION_ITEMS: NavigationItem[] = [
  // ========== NAVEGACIÓN PRINCIPAL (HOME SECTIONS para guest) ==========
  {
    label: 'Inicio',
    href: '/',
    icon: Home,
    description: 'Página principal',
    roles: ['guest'],
    section: 'main'
  },
  {
    label: 'Características',
    href: '/#features',
    icon: Target,
    description: 'Características de la plataforma',
    roles: ['guest'],
    section: 'main'
  },
  {
    label: 'Cómo funciona',
    href: '/#how',
    icon: Info,
    description: 'Cómo funciona Acadify',
    roles: ['guest'],
    section: 'main'
  },
  {
    label: 'Open Source',
    href: '/#opensource',
    icon: Database,
    description: 'Proyecto de código abierto',
    roles: ['guest'],
    section: 'main'
  },
  {
    label: 'Testimonios',
    href: '/#testimonials',
    icon: MessageSquare,
    description: 'Lo que dicen nuestros usuarios',
    roles: ['guest'],
    section: 'main'
  },

  // ========== NAVEGACIÓN AUTENTICADA ==========
  {
    label: 'Dashboard',
    href: '/dashboard',
    icon: Home,
    description: 'Panel principal',
    roles: ['admin', 'coordinador', 'profesor', 'docente', 'estudiante'],
    section: 'main'
  },

  // ========== GESTIÓN ADMINISTRATIVA ==========
  {
    label: 'Instituciones',
    href: '/admin/instituciones',
    icon: Building2,
    description: 'Administrar instituciones educativas',
    roles: ['admin'],
    section: 'main'
  },
  {
    label: 'Usuarios Pendientes',
    href: '/admin/usuarios-pendientes',
    icon: CheckCircle,
    description: 'Gestionar solicitudes de acceso',
    roles: ['admin'],
    section: 'main'
  },
  {
    label: 'Tienda',
    href: '/admin/tienda',
    icon: ShoppingBag,
    description: 'Gestionar productos y categorías de la tienda',
    roles: ['admin'],
    section: 'main'
  },
  {
    label: 'Configuración',
    href: '/admin/configuracion',
    icon: Settings,
    description: 'Configuración general del sistema',
    roles: ['admin'],
    section: 'main'
  },

  // ========== COORDINACIÓN ==========
  {
    label: 'Mi Institución',
    href: '/coordinador/institucion',
    icon: Building2,
    description: 'Gestionar mi institución',
    roles: ['coordinador'],
    section: 'main'
  },

  // ========== GESTIÓN DE CURSOS (roles académicos - NO ADMIN) ==========
  {
    label: 'Cursos',
    href: '/cursos',
    icon: Book,
    description: 'Explorar cursos disponibles',
    roles: ['profesor', 'docente', 'estudiante'], // Admin NO necesita esto en navbar
    section: 'main'
  },
  {
    label: 'Mis Clases',
    href: '/mis-clases',
    icon: Calendar,
    description: 'Clases inscritas/impartidas',
    roles: ['profesor', 'docente', 'estudiante'],
    section: 'academic'
  },

  // ========== PROFESOR ==========
  {
    label: 'Panel Profesor',
    href: '/profesor',
    icon: Settings,
    description: 'Panel de gestión docente',
    roles: ['profesor', 'docente'],
    section: 'management'
  },
  {
    label: 'Crear Clase',
    href: '/profesor/crear-clase',
    icon: Plus,
    description: 'Crear una nueva clase',
    roles: ['profesor', 'docente'],
    section: 'academic'
  },
  {
    label: 'Gestión de Tareas',
    href: '/profesor/tareas',
    icon: Edit,
    description: 'Administrar tareas y asignaciones',
    roles: ['profesor', 'docente'],
    section: 'academic'
  },
  {
    label: 'Calificaciones',
    href: '/profesor/calificaciones',
    icon: BarChart,
    description: 'Gestionar calificaciones',
    roles: ['profesor', 'docente', 'coordinador'],
    section: 'academic'
  },
  {
    label: 'Asistencia',
    href: '/profesor/asistencia',
    icon: CheckCircle,
    description: 'Registro de asistencia',
    roles: ['profesor', 'docente'],
    section: 'academic'
  },

  // ========== ESTUDIANTE ==========
  {
    label: 'Unirse a Clase',
    href: '/estudiante/unirse-clase',
    icon: Plus,
    description: 'Inscribirse en nuevas clases',
    roles: ['estudiante'],
    section: 'academic'
  },
  {
    label: 'Mis Tareas',
    href: '/estudiante/tareas',
    icon: FileText,
    description: 'Tareas pendientes y completadas',
    roles: ['estudiante'],
    section: 'academic'
  },
  {
    label: 'Mis Calificaciones',
    href: '/estudiante/calificaciones',
    icon: BarChart,
    description: 'Ver mis notas',
    roles: ['estudiante'],
    section: 'academic'
  },

  // ========== EVALUACIONES (roles académicos - NO ADMIN) ==========
  {
    label: 'Evaluaciones',
    href: '/evaluaciones',
    icon: FileText,
    description: 'Sistema de evaluaciones y exámenes',
    roles: ['coordinador', 'profesor', 'docente', 'estudiante'], // Admin NO necesita esto
    section: 'main'
  },

  // ========== COMUNICACIÓN (roles académicos - NO ADMIN) ==========
  {
    label: 'Comunicación',
    href: '/comunicacion',
    icon: MessageSquare,
    description: 'Chat y mensajería',
    roles: ['coordinador', 'profesor', 'docente', 'estudiante'], // Admin NO necesita esto
    section: 'main'
  },
  {
    label: 'Foros',
    href: '/foros',
    icon: Users,
    description: 'Foros de discusión',
    roles: ['coordinador', 'profesor', 'docente', 'estudiante'],
    section: 'social'
  },
  {
    label: 'Anuncios',
    href: '/anuncios',
    icon: Info,
    description: 'Anuncios y notificaciones',
    roles: ['admin', 'coordinador', 'profesor', 'docente', 'estudiante'],
    section: 'social'
  },

  // ========== GAMIFICACIÓN (estudiantes principalmente) ==========
  {
    label: 'Misiones',
    href: '/misiones',
    icon: Target,
    description: 'Misiones diarias y semanales',
    roles: ['estudiante'],
    section: 'tools'
  },
  {
    label: 'Logros',
    href: '/logros',
    icon: Award,
    description: 'Logros y medallas',
    roles: ['estudiante'],
    section: 'tools'
  },
  {
    label: 'Tienda',
    href: '/tienda',
    icon: ShoppingBag,
    description: 'Canjear puntos por premios',
    roles: ['estudiante'],
    section: 'tools'
  },
  {
    label: 'Ranking',
    href: '/ranking',
    icon: TrendingUp,
    description: 'Tabla de posiciones',
    roles: ['estudiante'],
    section: 'tools'
  },

  // ========== HERRAMIENTAS PERSONALES (todos) ==========
  {
    label: 'Mi Avatar',
    href: '/avatar',
    icon: User,
    description: 'Personalizar avatar',
    roles: ['admin', 'coordinador', 'profesor', 'docente', 'estudiante'],
    section: 'tools'
  },
  {
    label: 'Mi Perfil',
    href: '/perfil',
    icon: Settings,
    description: 'Configuración de perfil',
    roles: ['admin', 'coordinador', 'profesor', 'docente', 'estudiante'],
    section: 'tools'
  }
];

/**
 * Filtra items de navegación por rol
 * Principio de separación de responsabilidades
 */
export function getNavigationByRole(role: UserRole = 'guest'): NavigationItem[] {
  return NAVIGATION_ITEMS.filter(item => item.roles.includes(role));
}

/**
 * Agrupa items por sección
 * Útil para crear menús categorizados
 */
export function getNavigationBySection(role: UserRole = 'guest'): Record<string, NavigationItem[]> {
  const items = getNavigationByRole(role);
  const sections: Record<string, NavigationItem[]> = {};
  
  items.forEach(item => {
    const section = item.section || 'main';
    if (!sections[section]) {
      sections[section] = [];
    }
    sections[section].push(item);
  });
  
  return sections;
}

/**
 * Obtiene items principales para navbar (límite de items)
 * Prioriza items de la sección 'main'
 */
export function getMainNavItems(role: UserRole = 'guest', limit: number = 6): NavigationItem[] {
  // Normalizar rol: si es 'administrador', buscar como 'admin' también
  const normalizedRole = role === 'administrador' ? 'admin' : role;
  
  const allItems = getNavigationByRole(normalizedRole);
  const mainItems = allItems.filter(item => item.section === 'main');
  
  // Si hay menos items 'main' que el límite, completar con otros
  if (mainItems.length < limit) {
    const otherItems = allItems.filter(item => item.section !== 'main');
    return [...mainItems, ...otherItems].slice(0, limit);
  }
  
  return mainItems.slice(0, limit);
}

/**
 * Obtiene items de sidebar completos
 */
export function getSidebarItems(role: UserRole = 'guest'): NavigationItem[] {
  // Normalizar rol: si es 'administrador', buscar como 'admin' también
  const normalizedRole = role === 'administrador' ? 'admin' : role;
  return getNavigationByRole(normalizedRole);
}

/**
 * Verifica si un usuario con cierto rol puede acceder a una ruta
 */
export function canAccessRoute(role: UserRole, href: string): boolean {
  const item = NAVIGATION_ITEMS.find(i => i.href === href);
  return item ? item.roles.includes(role) : false;
}

/**
 * Nombres de secciones para UI
 */
export const SECTION_NAMES: Record<string, string> = {
  main: 'Principal',
  academic: 'Académico',
  management: 'Gestión',
  social: 'Comunicación',
  tools: 'Herramientas'
};

/**
 * Configuración de visualización por rol
 */
export const ROLE_CONFIG = {
  admin: {
    displayName: 'Administrador',
    primaryColor: 'from-red-500 to-red-600',
    description: 'Gestión completa del sistema'
  },
  administrador: {
    displayName: 'Administrador',
    primaryColor: 'from-red-500 to-red-600',
    description: 'Gestión completa del sistema'
  },
  coordinador: {
    displayName: 'Coordinador',
    primaryColor: 'from-blue-500 to-blue-600',
    description: 'Coordinación académica'
  },
  profesor: {
    displayName: 'Profesor',
    primaryColor: 'from-green-500 to-green-600',
    description: 'Gestión de clases'
  },
  docente: {
    displayName: 'Docente',
    primaryColor: 'from-green-500 to-green-600',
    description: 'Gestión de clases'
  },
  estudiante: {
    displayName: 'Estudiante',
    primaryColor: 'from-purple-500 to-purple-600',
    description: 'Aprendizaje y evaluaciones'
  },
  guest: {
    displayName: 'Visitante',
    primaryColor: 'from-gray-500 to-gray-600',
    description: 'Explorar la plataforma'
  }
} as const;
