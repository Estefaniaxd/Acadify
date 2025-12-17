/**
 * Configuración centralizada de navegación por roles - VERSIÓN SIMPLIFICADA
 * Solo rutas esenciales que existen en el proyecto
 */

import type { IconType } from 'react-icons';
import { Award, BarChart, Book, Building2, Home, MessageSquare, Settings, ShoppingBag, User } from 'lucide-react';

export type UserRole = 'admin' | 'administrador' | 'coordinador' | 'profesor' | 'docente' | 'estudiante' | 'guest';

export interface NavigationItem {
  label: string;
  href: string;
  icon: IconType;
  description?: string;
  roles: UserRole[];
  section?: 'main' | 'academic' | 'tools';
}

/**
 * Navegación simplificada - Solo rutas verificadas
 */
export const NAVIGATION_ITEMS: NavigationItem[] = [
  // ========== GUEST ==========
  {
    label: 'Inicio',
    href: '/',
    icon: Home,
    description: 'Página principal',
    roles: ['guest'],
    section: 'main'
  },

  // ========== DASHBOARD (Todos los autenticados) ==========
  {
    label: 'Dashboard',
    href: '/dashboard',
    icon: Home,
    description: 'Panel principal',
    roles: ['admin', 'administrador', 'coordinador', 'profesor', 'docente', 'estudiante'],
    section: 'main'
  },

  // ========== ADMIN ==========
  {
    label: 'Instituciones',
    href: '/admin/instituciones',
    icon: Building2,
    description: 'Administrar instituciones',
    roles: ['admin', 'administrador'],
    section: 'main'
  },
  {
    label: 'Usuarios Pendientes',
    href: '/admin/usuarios-pendientes',
    icon: User,
    description: 'Aprobar usuarios',
    roles: ['admin', 'administrador'],
    section: 'main'
  },
  {
    label: 'Tienda',
    href: '/admin/tienda',
    icon: ShoppingBag,
    description: 'Gestionar tienda',
    roles: ['admin', 'administrador'],
    section: 'main'
  },

  // ========== COORDINADOR ==========
  {
    label: 'Mi Institución',
    href: '/coordinador/institucion',
    icon: Building2,
    description: 'Gestionar institución',
    roles: ['coordinador'],
    section: 'main'
  },

  // ========== ACADÉMICO (Profesores y Estudiantes) ==========
  {
    label: 'Mis Cursos',
    href: '/cursos',
    icon: Book,
    description: 'Ver cursos',
    roles: ['profesor', 'docente', 'estudiante'],
    section: 'main'
  },

  // ========== GAMIFICACIÓN (Solo Estudiantes) ==========
  {
    label: 'Logros',
    href: '/logros',
    icon: Award,
    description: 'Mis logros',
    roles: ['estudiante'],
    section: 'tools'
  },
  {
    label: 'Tienda',
    href: '/tienda',
    icon: ShoppingBag,
    description: 'Canjear puntos',
    roles: ['estudiante'],
    section: 'tools'
  },

  // ========== COMUNICACIÓN (Todos excepto admin) ==========
  {
    label: 'Mensajes',
    href: '/comunicacion',
    icon: MessageSquare,
    description: 'Chat y mensajes',
    roles: ['coordinador', 'profesor', 'docente', 'estudiante'],
    section: 'main'
  },

  // ========== PERFIL (Todos autenticados) ==========
  {
    label: 'Mi Perfil',
    href: '/perfil',
    icon: Settings,
    description: 'Configuración',
    roles: ['admin', 'administrador', 'coordinador', 'profesor', 'docente', 'estudiante'],
    section: 'tools'
  },
  {
    label: 'Avatar',
    href: '/avatar',
    icon: User,
    description: 'Personalizar avatar',
    roles: ['admin', 'administrador', 'coordinador', 'profesor', 'docente', 'estudiante'],
    section: 'tools'
  }
];

/**
 * Filtra items de navegación por rol
 */
export function getNavigationByRole(role: UserRole = 'guest'): NavigationItem[] {
  const normalizedRole = role === 'administrador' ? 'admin' : role;
  return NAVIGATION_ITEMS.filter(item => item.roles.includes(normalizedRole));
}

/**
 * Obtiene items principales para navbar (máximo 6)
 */
export function getMainNavItems(role: UserRole = 'guest', limit: number = 6): NavigationItem[] {
  const normalizedRole = role === 'administrador' ? 'admin' : role;
  const allItems = getNavigationByRole(normalizedRole);
  const mainItems = allItems.filter(item => item.section === 'main');
  return mainItems.slice(0, limit);
}

/**
 * Obtiene items de sidebar
 */
export function getSidebarItems(role: UserRole = 'guest'): NavigationItem[] {
  const normalizedRole = role === 'administrador' ? 'admin' : role;
  return getNavigationByRole(normalizedRole);
}

/**
 * Nombres de secciones para el UI
 */
export const SECTION_NAMES: Record<string, string> = {
  main: 'Principal',
  academic: 'Académico',
  tools: 'Herramientas'
};

/**
 * Agrupa items de navegación por sección
 */
export function getNavigationBySection(role: UserRole = 'guest'): Record<string, NavigationItem[]> {
  const normalizedRole = role === 'administrador' ? 'admin' : role;
  const items = getNavigationByRole(normalizedRole);

  const grouped: Record<string, NavigationItem[]> = {
    main: [],
    academic: [],
    tools: []
  };

  items.forEach(item => {
    const section = item.section || 'main';
    if (grouped[section]) {
      grouped[section].push(item);
    }
  });

  // Filtrar secciones vacías
  Object.keys(grouped).forEach(key => {
    if (grouped[key].length === 0) {
      delete grouped[key];
    }
  });

  return grouped;
}

/**
 * Verifica si un usuario puede acceder a una ruta
 */
export function canAccessRoute(role: UserRole, href: string): boolean {
  const normalizedRole = role === 'administrador' ? 'admin' : role;
  const item = NAVIGATION_ITEMS.find(i => i.href === href);
  return item ? item.roles.includes(normalizedRole) : false;
}

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

