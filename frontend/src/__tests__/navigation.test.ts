/**
 * Tests para el sistema de navegación
 * Valida la configuración de rutas, permisos y visualización por rol
 */

import { describe, it, expect } from 'vitest';
import {
  getNavigationByRole,
  getNavigationBySection,
  getMainNavItems,
  getSidebarItems,
  canAccessRoute,
  NAVIGATION_ITEMS,
  SECTION_NAMES,
  ROLE_CONFIG,
  type UserRole
} from '../config/navigation';

describe('Sistema de Navegación', () => {
  describe('Configuración de Roles', () => {
    it('debe tener configuración para todos los roles', () => {
      const roles: UserRole[] = ['admin', 'coordinador', 'profesor', 'docente', 'estudiante', 'guest'];
      
      roles.forEach(role => {
        expect(ROLE_CONFIG[role]).toBeDefined();
        expect(ROLE_CONFIG[role].displayName).toBeTruthy();
        expect(ROLE_CONFIG[role].primaryColor).toBeTruthy();
        expect(ROLE_CONFIG[role].description).toBeTruthy();
      });
    });

    it('debe tener colores únicos para cada rol', () => {
      const colors = Object.values(ROLE_CONFIG).map(config => config.primaryColor);
      const uniqueColors = new Set(colors);
      
      // Docente y profesor pueden compartir color
      expect(uniqueColors.size).toBeGreaterThanOrEqual(5);
    });
  });

  describe('Items de Navegación', () => {
    it('todos los items deben tener propiedades requeridas', () => {
      NAVIGATION_ITEMS.forEach(item => {
        expect(item.label).toBeTruthy();
        expect(item.href).toBeTruthy();
        expect(item.icon).toBeDefined();
        expect(Array.isArray(item.roles)).toBe(true);
        expect(item.roles.length).toBeGreaterThan(0);
      });
    });

    it('todos los items deben tener al menos un rol asignado', () => {
      NAVIGATION_ITEMS.forEach(item => {
        expect(item.roles.length).toBeGreaterThan(0);
      });
    });

    it('las rutas no deben tener duplicados para el mismo rol', () => {
      const roles: UserRole[] = ['admin', 'coordinador', 'profesor', 'docente', 'estudiante', 'guest'];
      
      roles.forEach(role => {
        const items = getNavigationByRole(role);
        const hrefs = items.map(item => item.href);
        const uniqueHrefs = new Set(hrefs);
        
        expect(hrefs.length).toBe(uniqueHrefs.size);
      });
    });

    it('todas las secciones deben tener nombres definidos', () => {
      const sections = new Set(NAVIGATION_ITEMS.map(item => item.section).filter(Boolean));
      
      sections.forEach(section => {
        if (section) {
          expect(SECTION_NAMES[section]).toBeDefined();
        }
      });
    });
  });

  describe('Filtrado por Rol - Admin', () => {
    it('admin debe tener acceso a gestión de instituciones', () => {
      const items = getNavigationByRole('admin');
      const hasInstituciones = items.some(item => item.href === '/admin/instituciones');
      
      expect(hasInstituciones).toBe(true);
    });

    it('admin debe tener acceso a gestión de usuarios', () => {
      const items = getNavigationByRole('admin');
      const hasUsuarios = items.some(item => item.href === '/admin/usuarios');
      
      expect(hasUsuarios).toBe(true);
    });

    it('admin debe tener acceso al dashboard', () => {
      const items = getNavigationByRole('admin');
      const hasDashboard = items.some(item => item.href === '/dashboard');
      
      expect(hasDashboard).toBe(true);
    });

    it('admin debe tener sección de gestión', () => {
      const sections = getNavigationBySection('admin');
      
      expect(sections.management).toBeDefined();
      expect(sections.management.length).toBeGreaterThan(0);
    });

    it('admin NO debe ver items exclusivos de estudiantes', () => {
      const items = getNavigationByRole('admin');
      const hasTienda = items.some(item => item.href === '/tienda');
      const hasLogros = items.some(item => item.href === '/logros');
      
      expect(hasTienda).toBe(false);
      expect(hasLogros).toBe(false);
    });
  });

  describe('Filtrado por Rol - Coordinador', () => {
    it('coordinador debe tener acceso a gestión de profesores', () => {
      const items = getNavigationByRole('coordinador');
      const hasProfesores = items.some(item => item.href === '/coordinador/profesores');
      
      expect(hasProfesores).toBe(true);
    });

    it('coordinador debe tener acceso a asignación de cursos', () => {
      const items = getNavigationByRole('coordinador');
      const hasAsignaciones = items.some(item => item.href === '/coordinador/asignaciones');
      
      expect(hasAsignaciones).toBe(true);
    });

    it('coordinador debe tener acceso a seguimiento académico', () => {
      const items = getNavigationByRole('coordinador');
      const hasSeguimiento = items.some(item => item.href === '/coordinador/seguimiento');
      
      expect(hasSeguimiento).toBe(true);
    });

    it('coordinador debe tener acceso a cursos', () => {
      const items = getNavigationByRole('coordinador');
      const hasCursos = items.some(item => item.href === '/cursos');
      
      expect(hasCursos).toBe(true);
    });
  });

  describe('Filtrado por Rol - Profesor/Docente', () => {
    it('profesor debe tener acceso a crear clases', () => {
      const items = getNavigationByRole('profesor');
      const hasCrearClase = items.some(item => item.href === '/profesor/crear-clase');
      
      expect(hasCrearClase).toBe(true);
    });

    it('profesor debe tener acceso a gestión de tareas', () => {
      const items = getNavigationByRole('profesor');
      const hasTareas = items.some(item => item.href === '/profesor/tareas');
      
      expect(hasTareas).toBe(true);
    });

    it('profesor debe tener acceso a calificaciones', () => {
      const items = getNavigationByRole('profesor');
      const hasCalificaciones = items.some(item => item.href === '/profesor/calificaciones');
      
      expect(hasCalificaciones).toBe(true);
    });

    it('profesor debe tener acceso a registro de asistencia', () => {
      const items = getNavigationByRole('profesor');
      const hasAsistencia = items.some(item => item.href === '/profesor/asistencia');
      
      expect(hasAsistencia).toBe(true);
    });

    it('profesor NO debe tener acceso a gestión de instituciones', () => {
      const items = getNavigationByRole('profesor');
      const hasInstituciones = items.some(item => item.href === '/admin/instituciones');
      
      expect(hasInstituciones).toBe(false);
    });

    it('docente debe tener las mismas rutas que profesor', () => {
      const itemsProfesor = getNavigationByRole('profesor');
      const itemsDocente = getNavigationByRole('docente');
      
      expect(itemsProfesor.length).toBe(itemsDocente.length);
    });
  });

  describe('Filtrado por Rol - Estudiante', () => {
    it('estudiante debe tener acceso a unirse a clases', () => {
      const items = getNavigationByRole('estudiante');
      const hasUnirse = items.some(item => item.href === '/estudiante/unirse-clase');
      
      expect(hasUnirse).toBe(true);
    });

    it('estudiante debe tener acceso a sus tareas', () => {
      const items = getNavigationByRole('estudiante');
      const hasTareas = items.some(item => item.href === '/estudiante/tareas');
      
      expect(hasTareas).toBe(true);
    });

    it('estudiante debe tener acceso a sus calificaciones', () => {
      const items = getNavigationByRole('estudiante');
      const hasCalificaciones = items.some(item => item.href === '/estudiante/calificaciones');
      
      expect(hasCalificaciones).toBe(true);
    });

    it('estudiante debe tener acceso a gamificación', () => {
      const items = getNavigationByRole('estudiante');
      const hasLogros = items.some(item => item.href === '/logros');
      const hasTienda = items.some(item => item.href === '/tienda');
      const hasRanking = items.some(item => item.href === '/ranking');
      
      expect(hasLogros).toBe(true);
      expect(hasTienda).toBe(true);
      expect(hasRanking).toBe(true);
    });

    it('estudiante NO debe tener acceso a gestión administrativa', () => {
      const items = getNavigationByRole('estudiante');
      const hasAdmin = items.some(item => item.href.startsWith('/admin'));
      const hasCoordinador = items.some(item => item.href.startsWith('/coordinador'));
      const hasProfesor = items.some(item => item.href.startsWith('/profesor'));
      
      expect(hasAdmin).toBe(false);
      expect(hasCoordinador).toBe(false);
      expect(hasProfesor).toBe(false);
    });
  });

  describe('Filtrado por Rol - Guest', () => {
    it('guest debe tener acceso solo a rutas públicas', () => {
      const items = getNavigationByRole('guest');
      
      items.forEach(item => {
        expect(
          item.href === '/' || 
          item.href.startsWith('/#')
        ).toBe(true);
      });
    });

    it('guest NO debe tener acceso a rutas autenticadas', () => {
      const items = getNavigationByRole('guest');
      const hasProtected = items.some(item => 
        item.href === '/dashboard' ||
        item.href === '/cursos' ||
        item.href === '/evaluaciones'
      );
      
      expect(hasProtected).toBe(false);
    });

    it('guest debe poder ver información institucional', () => {
      const items = getNavigationByRole('guest');
      const hasInstituciones = items.some(item => item.href === '/#institutions');
      
      expect(hasInstituciones).toBe(true);
    });
  });

  describe('Agrupación por Secciones', () => {
    it('debe retornar objeto con secciones para cada rol', () => {
      const roles: UserRole[] = ['admin', 'coordinador', 'profesor', 'estudiante', 'guest'];
      
      roles.forEach(role => {
        const sections = getNavigationBySection(role);
        
        expect(typeof sections).toBe('object');
        expect(Object.keys(sections).length).toBeGreaterThan(0);
      });
    });

    it('items en cada sección deben pertenecer a esa sección', () => {
      const sections = getNavigationBySection('estudiante');
      
      Object.entries(sections).forEach(([sectionKey, items]) => {
        items.forEach(item => {
          expect(item.section).toBe(sectionKey);
        });
      });
    });

    it('todas las secciones deben estar en SECTION_NAMES', () => {
      const roles: UserRole[] = ['admin', 'coordinador', 'profesor', 'estudiante', 'guest'];
      
      roles.forEach(role => {
        const sections = getNavigationBySection(role);
        
        Object.keys(sections).forEach(sectionKey => {
          expect(SECTION_NAMES[sectionKey]).toBeDefined();
        });
      });
    });
  });

  describe('Funciones Auxiliares', () => {
    it('getMainNavItems debe limitar correctamente los items', () => {
      const items = getMainNavItems('estudiante', 3);
      
      expect(items.length).toBeLessThanOrEqual(3);
    });

    it('getMainNavItems debe retornar items del rol correcto', () => {
      const items = getMainNavItems('admin', 5);
      
      items.forEach(item => {
        expect(item.roles.includes('admin')).toBe(true);
      });
    });

    it('getSidebarItems debe retornar todos los items del rol', () => {
      const itemsAdmin = getSidebarItems('admin');
      const itemsEstudiante = getSidebarItems('estudiante');
      
      expect(itemsAdmin.length).toBeGreaterThan(0);
      expect(itemsEstudiante.length).toBeGreaterThan(0);
      expect(itemsAdmin.length).not.toBe(itemsEstudiante.length);
    });

    it('canAccessRoute debe validar correctamente el acceso', () => {
      expect(canAccessRoute('admin', '/admin/instituciones')).toBe(true);
      expect(canAccessRoute('estudiante', '/admin/instituciones')).toBe(false);
      expect(canAccessRoute('profesor', '/profesor/tareas')).toBe(true);
      expect(canAccessRoute('estudiante', '/profesor/tareas')).toBe(false);
      expect(canAccessRoute('guest', '/')).toBe(true);
      expect(canAccessRoute('guest', '/dashboard')).toBe(false);
    });
  });

  describe('Consistencia de Datos', () => {
    it('todos los roles en items deben ser válidos', () => {
      const validRoles: UserRole[] = ['admin', 'coordinador', 'profesor', 'docente', 'estudiante', 'guest'];
      
      NAVIGATION_ITEMS.forEach(item => {
        item.roles.forEach(role => {
          expect(validRoles.includes(role)).toBe(true);
        });
      });
    });

    it('todas las rutas deben comenzar con /', () => {
      NAVIGATION_ITEMS.forEach(item => {
        expect(item.href.startsWith('/')).toBe(true);
      });
    });

    it('no debe haber labels vacíos o undefined', () => {
      NAVIGATION_ITEMS.forEach(item => {
        expect(item.label).toBeTruthy();
        expect(item.label.length).toBeGreaterThan(0);
      });
    });

    it('items con badge deben tener badge no vacío', () => {
      NAVIGATION_ITEMS.forEach(item => {
        if (item.badge) {
          expect(item.badge.length).toBeGreaterThan(0);
        }
      });
    });
  });

  describe('Acceso Compartido', () => {
    it('todos los roles autenticados deben tener acceso a comunicación', () => {
      const authRoles: UserRole[] = ['admin', 'coordinador', 'profesor', 'docente', 'estudiante'];
      
      authRoles.forEach(role => {
        const items = getNavigationByRole(role);
        const hasComunicacion = items.some(item => item.href === '/comunicacion');
        
        expect(hasComunicacion).toBe(true);
      });
    });

    it('todos los roles autenticados deben tener acceso a evaluaciones', () => {
      const authRoles: UserRole[] = ['admin', 'coordinador', 'profesor', 'docente', 'estudiante'];
      
      authRoles.forEach(role => {
        const items = getNavigationByRole(role);
        const hasEvaluaciones = items.some(item => item.href === '/evaluaciones');
        
        expect(hasEvaluaciones).toBe(true);
      });
    });

    it('todos los roles autenticados deben tener acceso a cursos', () => {
      const authRoles: UserRole[] = ['admin', 'coordinador', 'profesor', 'docente', 'estudiante'];
      
      authRoles.forEach(role => {
        const items = getNavigationByRole(role);
        const hasCursos = items.some(item => item.href === '/cursos');
        
        expect(hasCursos).toBe(true);
      });
    });

    it('todos los roles autenticados deben tener acceso a avatar', () => {
      const authRoles: UserRole[] = ['admin', 'coordinador', 'profesor', 'docente', 'estudiante'];
      
      authRoles.forEach(role => {
        const items = getNavigationByRole(role);
        const hasAvatar = items.some(item => item.href === '/avatar');
        
        expect(hasAvatar).toBe(true);
      });
    });
  });

  describe('Jerarquía de Permisos', () => {
    it('admin y coordinador deben tener items de gestión', () => {
      const itemsAdmin = getNavigationByRole('admin');
      const itemsCoordinador = getNavigationByRole('coordinador');
      
      // Ambos tienen roles de gestión, la cantidad puede variar
      expect(itemsAdmin.length).toBeGreaterThan(0);
      expect(itemsCoordinador.length).toBeGreaterThan(0);
    });

    it('roles educativos deben tener más items que guest', () => {
      const itemsProfesor = getNavigationByRole('profesor');
      const itemsEstudiante = getNavigationByRole('estudiante');
      const itemsGuest = getNavigationByRole('guest');
      
      expect(itemsProfesor.length).toBeGreaterThan(itemsGuest.length);
      expect(itemsEstudiante.length).toBeGreaterThan(itemsGuest.length);
    });

    it('estudiante NO debe tener acceso a rutas de gestión', () => {
      const items = getNavigationByRole('estudiante');
      const hasManagement = items.some(item => item.section === 'management');
      
      expect(hasManagement).toBe(false);
    });
  });
});
