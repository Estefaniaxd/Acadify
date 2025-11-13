/**
 * Script de auditoría de navegación
 * Verifica consistencia entre rutas definidas y rutas implementadas
 */

import { NAVIGATION_ITEMS } from '../src/config/navigation';

// Rutas definidas en App.tsx (extraídas manualmente)
const appRoutes = [
  '/',
  '/login',
  '/register',
  '/recover',
  '/reset-password',
  '/dashboard',
  '/dashboard-admin',
  '/dashboard-coordinador',
  '/dashboard-teacher',
  '/dashboard-student',
  '/notificaciones',
  '/mensajes',
  '/comunicacion',
  '/cursos',
  '/clase/:id',
  '/evaluaciones',
  '/clase/:id/tablon',
  '/clase/:id/materiales',
  '/clase/:id/tareas',
  '/clase/:id/calificaciones',
  '/clase/:id/personas',
  '/clase/:id/chat',
  '/logros',
  '/insignias',
  '/logros-usuario',
  '/puntos',
  '/niveles',
  '/tienda',
  '/perfil',
  '/perfil/:userId',
  '/ajustes',
  '/ayuda',
  '/avatar',
  '/editor-avatar',
  '/tratamiento-datos',
  '/consentimiento',
];

// Rutas en navigation.ts
const navigationRoutes = NAVIGATION_ITEMS.map(item => item.href);

interface AuditResult {
  inNavigationButNotInApp: string[];
  inAppButNotInNavigation: string[];
  duplicatesInNavigation: string[];
  routesBySection: Record<string, number>;
  routesByRole: Record<string, number>;
  totalRoutes: {
    navigation: number;
    app: number;
  };
}

export function auditNavigation(): AuditResult {
  // Rutas en navigation.ts pero no en App.tsx
  const inNavigationButNotInApp = navigationRoutes.filter(
    route => !appRoutes.includes(route) && !route.includes('#')
  );

  // Rutas en App.tsx pero no en navigation.ts
  const inAppButNotInNavigation = appRoutes.filter(
    route => !navigationRoutes.includes(route)
  );

  // Duplicados en navigation.ts
  const routeCounts = new Map<string, number>();
  for (const route of navigationRoutes) {
    routeCounts.set(route, (routeCounts.get(route) || 0) + 1);
  }
  const duplicatesInNavigation = Array.from(routeCounts.entries())
    .filter(([, count]) => count > 1)
    .map(([route]) => route);

  // Contar rutas por sección
  const routesBySection: Record<string, number> = {};
  for (const item of NAVIGATION_ITEMS) {
    const section = item.section || 'unknown';
    routesBySection[section] = (routesBySection[section] || 0) + 1;
  }

  // Contar rutas por rol
  const routesByRole: Record<string, number> = {};
  for (const item of NAVIGATION_ITEMS) {
    for (const role of item.roles) {
      routesByRole[role] = (routesByRole[role] || 0) + 1;
    }
  }

  return {
    inNavigationButNotInApp,
    inAppButNotInNavigation,
    duplicatesInNavigation,
    routesBySection,
    routesByRole,
    totalRoutes: {
      navigation: navigationRoutes.length,
      app: appRoutes.length,
    },
  };
}

// Ejecutar auditoría si se corre directamente
if (require.main === module) {
  const result = auditNavigation();
  
  console.log('🔍 AUDITORÍA DE NAVEGACIÓN\n');
  console.log('═'.repeat(60));
  
  console.log('\n📊 Resumen:');
  console.log(`  Total rutas en navigation.ts: ${result.totalRoutes.navigation}`);
  console.log(`  Total rutas en App.tsx: ${result.totalRoutes.app}`);
  
  if (result.inNavigationButNotInApp.length > 0) {
    console.log('\n⚠️  Rutas en navigation.ts sin implementar en App.tsx:');
    for (const route of result.inNavigationButNotInApp) {
      console.log(`    ❌ ${route}`);
    }
  }
  
  if (result.inAppButNotInNavigation.length > 0) {
    console.log('\n⚠️  Rutas en App.tsx sin definir en navigation.ts:');
    for (const route of result.inAppButNotInNavigation) {
      console.log(`    ⚠️  ${route}`);
    }
  }
  
  if (result.duplicatesInNavigation.length > 0) {
    console.log('\n🔴 Rutas duplicadas en navigation.ts:');
    for (const route of result.duplicatesInNavigation) {
      console.log(`    🔁 ${route}`);
    }
  }
  
  console.log('\n📂 Rutas por sección:');
  for (const [section, count] of Object.entries(result.routesBySection)) {
    console.log(`    ${section}: ${count} rutas`);
  }
  
  console.log('\n👥 Rutas accesibles por rol:');
  for (const [role, count] of Object.entries(result.routesByRole)) {
    console.log(`    ${role}: ${count} rutas`);
  }
  
  console.log('\n' + '═'.repeat(60));
  
  // Exit code basado en problemas encontrados
  const hasIssues = 
    result.inNavigationButNotInApp.length > 0 ||
    result.duplicatesInNavigation.length > 0;
  
  if (hasIssues) {
    console.log('\n❌ Auditoría completada con problemas');
    process.exit(1);
  } else {
    console.log('\n✅ Auditoría completada sin problemas críticos');
    process.exit(0);
  }
}

export default auditNavigation;
