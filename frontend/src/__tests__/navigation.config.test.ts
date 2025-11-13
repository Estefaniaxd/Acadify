/**
 * Tests de navegación - Verificación de rutas y roles
 * Asegura que la navegación funcione correctamente para cada rol
 */

import { describe, it, expect } from 'vitest';
import { 
  NAVIGATION_ITEMS, 
  getNavigationByRole, 
  getNavigationBySection,
  canAccessRoute,
  getMainNavItems,
  getSidebarItems,
  ROLE_CONFIG
} from '../config/navigation';

describe('Navigation Configuration Tests', () => {
  describe('NAVIGATION_ITEMS', () => {
    it('debe tener items válidos', () => {
      expect(NAVIGATION_ITEMS).toBeDefined();
      expect(NAVIGATION_ITEMS.length).toBeGreaterThan(0);
      
      console.log(`📊 Total navigation items: ${NAVIGATION_ITEMS.length}`);
    });

    it('todos los items deben tener propiedades requeridas', () => {
      for (const item of NAVIGATION_ITEMS) {
        expect(item).toHaveProperty('label');
        expect(item).toHaveProperty('href');
        expect(item).toHaveProperty('icon');
        expect(item).toHaveProperty('roles');
        expect(item.roles).toBeInstanceOf(Array);
        expect(item.roles.length).toBeGreaterThan(0);
      }
    });

    it('no debe haber rutas duplicadas', () => {
      const hrefs = NAVIGATION_ITEMS.map(item => item.href);
      const uniqueHrefs = new Set(hrefs);
      
      if (hrefs.length !== uniqueHrefs.size) {
        const duplicates = hrefs.filter((item, index) => hrefs.indexOf(item) !== index);
        console.error('🔴 Rutas duplicadas:', duplicates);
      }
      
      expect(hrefs.length).toBe(uniqueHrefs.size);
    });

    it('todas las rutas deben tener formato válido', () => {
      for (const item of NAVIGATION_ITEMS) {
        // Debe empezar con / o #
        expect(item.href).toMatch(/^[/#]/);
      }
    });
  });

  describe('getNavigationByRole', () => {
    const roles = ['admin', 'coordinador', 'profesor', 'estudiante', 'guest'];

    for (const role of roles) {
      it(`debe retornar items para rol: ${role}`, () => {
        const items = getNavigationByRole(role as any);
        
        expect(items).toBeDefined();
        expect(items.length).toBeGreaterThan(0);
        
        console.log(`👤 ${role}: ${items.length} items`);
        
        // Todos los items deben incluir el rol especificado
        for (const item of items) {
          expect(item.roles).toContain(role);
        }
      });
    }

    it('admin debe tener más items que estudiante', () => {
      const adminItems = getNavigationByRole('admin');
      const estudianteItems = getNavigationByRole('estudiante');
      
      expect(adminItems.length).toBeGreaterThan(estudianteItems.length);
      
      console.log(`👑 Admin: ${adminItems.length} vs 🎓 Estudiante: ${estudianteItems.length}`);
    });

    it('guest solo debe ver items públicos', () => {
      const guestItems = getNavigationByRole('guest');
      
      // Guest no debería tener acceso a dashboards o configuraciones
      const restrictedPaths = guestItems.filter(item => 
        item.href.includes('dashboard') || 
        item.href.includes('ajustes') ||
        item.href.includes('perfil')
      );
      
      expect(restrictedPaths.length).toBe(0);
    });
  });

  describe('getNavigationBySection', () => {
    const roles = ['admin', 'coordinador', 'profesor', 'estudiante'];

    for (const role of roles) {
      it(`debe agrupar items por sección para ${role}`, () => {
        const sections = getNavigationBySection(role as any);
        
        expect(sections).toBeDefined();
        expect(Object.keys(sections).length).toBeGreaterThan(0);
        
        console.log(`📂 ${role} sections:`, Object.keys(sections));
        
        // Verificar que cada sección tiene items
        for (const [, items] of Object.entries(sections)) {
          expect(items.length).toBeGreaterThan(0);
        }
      });
    }

    it('debe tener secciones estándar', () => {
      const expectedSections = ['main', 'academic', 'management', 'social', 'tools'];
      const adminSections = getNavigationBySection('admin');
      const adminSectionKeys = Object.keys(adminSections);
      
      for (const section of expectedSections) {
        if (adminSectionKeys.includes(section)) {
          expect(adminSections[section].length).toBeGreaterThan(0);
        }
      }
    });
  });

  describe('getMainNavItems', () => {
    it('debe limitar items correctamente', () => {
      const limit = 5;
      const items = getMainNavItems('estudiante', limit);
      
      expect(items.length).toBeLessThanOrEqual(limit);
      console.log(`📌 Main nav items (limit ${limit}): ${items.length}`);
    });

    it('debe retornar items prioritarios primero', () => {
      const items = getMainNavItems('estudiante', 3);
      
      // El primer item típicamente debería ser Dashboard o Home
      expect(items[0].href).toMatch(/dashboard|^\//);
    });
  });

  describe('getSidebarItems', () => {
    it('debe retornar todos los items para el rol', () => {
      const mainItems = getMainNavItems('estudiante', 5);
      const sidebarItems = getSidebarItems('estudiante');
      
      expect(sidebarItems.length).toBeGreaterThanOrEqual(mainItems.length);
      
      console.log(`📋 Sidebar vs Main: ${sidebarItems.length} vs ${mainItems.length}`);
    });
  });

  describe('canAccessRoute', () => {
    it('admin debe acceder a rutas de admin', () => {
      const canAccess = canAccessRoute('admin', '/admin');
      expect(canAccess).toBe(true);
    });

    it('estudiante NO debe acceder a rutas de admin', () => {
      const canAccess = canAccessRoute('estudiante', '/admin');
      expect(canAccess).toBe(false);
    });

    it('profesor debe acceder a /cursos', () => {
      const canAccess = canAccessRoute('profesor', '/cursos');
      expect(canAccess).toBe(true);
    });

    it('guest NO debe acceder a /dashboard', () => {
      const canAccess = canAccessRoute('guest', '/dashboard');
      expect(canAccess).toBe(false);
    });

    it('debe retornar false para rutas inexistentes', () => {
      const canAccess = canAccessRoute('admin', '/ruta-inexistente');
      expect(canAccess).toBe(false);
    });
  });

  describe('ROLE_CONFIG', () => {
    it('debe tener configuración para todos los roles', () => {
      const roles = ['admin', 'coordinador', 'profesor', 'docente', 'estudiante', 'guest'];
      
      for (const role of roles) {
        expect(ROLE_CONFIG).toHaveProperty(role);
        expect(ROLE_CONFIG[role as keyof typeof ROLE_CONFIG]).toHaveProperty('displayName');
        expect(ROLE_CONFIG[role as keyof typeof ROLE_CONFIG]).toHaveProperty('primaryColor');
        expect(ROLE_CONFIG[role as keyof typeof ROLE_CONFIG]).toHaveProperty('description');
      }
    });

    it('colores deben ser gradientes válidos de Tailwind', () => {
      for (const [, config] of Object.entries(ROLE_CONFIG)) {
        expect(config.primaryColor).toMatch(/^from-\w+-\d+ to-\w+-\d+$/);
      }
    });
  });

  describe('Navegación por Rol - Coverage', () => {
    // Helper function to check if route is in all role sets
    const isRouteInAllRoles = (route: string, roleRouteSets: Record<string, Set<string>>, roleList: string[]) => {
      for (const role of roleList) {
        if (!roleRouteSets[role].has(route)) {
          return false;
        }
      }
      return true;
    };

    it('cada rol debe tener rutas únicas y compartidas', () => {
      const roles = ['admin', 'coordinador', 'profesor', 'estudiante'];
      const routesByRole: Record<string, Set<string>> = {};
      
      for (const role of roles) {
        const items = getNavigationByRole(role as any);
        routesByRole[role] = new Set(items.map(item => item.href));
      }
      
      console.log('\n📊 Análisis de rutas por rol:');
      
      // Rutas compartidas por todos
      const sharedRoutes = Array.from(routesByRole.admin).filter(route =>
        isRouteInAllRoles(route, routesByRole, roles)
      );
      
      console.log(`  🤝 Compartidas por todos: ${sharedRoutes.length}`);
      console.log(`     ${sharedRoutes.slice(0, 3).join(', ')}${sharedRoutes.length > 3 ? '...' : ''}`);
      
      // Rutas únicas de admin
      const adminOnlyRoutes = Array.from(routesByRole.admin).filter(route =>
        !routesByRole.coordinador.has(route) &&
        !routesByRole.profesor.has(route) &&
        !routesByRole.estudiante.has(route)
      );
      
      console.log(`  👑 Solo Admin: ${adminOnlyRoutes.length}`);
      console.log(`     ${adminOnlyRoutes.slice(0, 3).join(', ')}${adminOnlyRoutes.length > 3 ? '...' : ''}`);
      
      expect(sharedRoutes.length).toBeGreaterThan(0);
      expect(adminOnlyRoutes.length).toBeGreaterThan(0);
    });
  });

  describe('Performance - Navigation Queries', () => {
    it('getNavigationByRole debe ser rápido', () => {
      const iterations = 1000;
      const startTime = performance.now();
      
      for (let i = 0; i < iterations; i++) {
        getNavigationByRole('estudiante');
      }
      
      const endTime = performance.now();
      const avgTime = (endTime - startTime) / iterations;
      
      console.log(`⚡ getNavigationByRole avg: ${avgTime.toFixed(4)}ms`);
      
      expect(avgTime).toBeLessThan(1); // Debe ser sub-millisegundo
    });

    it('canAccessRoute debe ser muy rápido', () => {
      const iterations = 10000;
      const startTime = performance.now();
      
      for (let i = 0; i < iterations; i++) {
        canAccessRoute('estudiante', '/dashboard');
      }
      
      const endTime = performance.now();
      const avgTime = (endTime - startTime) / iterations;
      
      console.log(`⚡ canAccessRoute avg: ${avgTime.toFixed(4)}ms`);
      
      expect(avgTime).toBeLessThan(0.1); // Debe ser muy rápido
    });
  });
});

describe('Navigation Integration Tests', () => {
  it('rutas en navigation.ts deben coincidir con estructura esperada', () => {
    const expectedRoutePatterns = [
      /^\/$/,                    // Home
      /^\/dashboard/,            // Dashboards
      /^\/cursos/,               // Cursos
      /^\/admin/,                // Admin
      /^\/coordinador/,          // Coordinador
      /^\/profesor/,             // Profesor
      /^\/estudiante/,           // Estudiante
      /^\/avatar/,               // Avatar
      /^\/perfil/,               // Perfil
      /^\/logros/,               // Gamificación
      /^\/comunicacion/,         // Comunicación
      /^#/,                      // Anchor links
    ];
    
    const allRoutes = NAVIGATION_ITEMS.map(item => item.href);
    const uncategorized = allRoutes.filter(route =>
      !expectedRoutePatterns.some(pattern => pattern.test(route))
    );
    
    if (uncategorized.length > 0) {
      console.warn('⚠️  Rutas sin categorizar:', uncategorized);
    }
    
    // Al menos 90% de las rutas deben estar categorizadas
    const categorizationRate = ((allRoutes.length - uncategorized.length) / allRoutes.length) * 100;
    console.log(`📊 Categorization rate: ${categorizationRate.toFixed(1)}%`);
    
    expect(categorizationRate).toBeGreaterThan(90);
  });
});
