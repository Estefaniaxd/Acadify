/**
 * Tests de rendimiento para navegación y componentes críticos
 * Mide tiempos de render, re-renders y uso de memoria
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '../lib/queryClient';
import { ThemeProvider } from '../context/ThemeContext';
import { AuthProvider } from '../context/AuthContext';
import { ToastProvider } from '../context/ToastContext';

// Componentes a testear
import Nav from '../components/layout/Nav';
import SidebarLeft from '../components/nav/SidebarLeft';
import SidebarRight from '../components/nav/SidebarRight';
import { Home } from '../pages/home';

/**
 * Wrapper con todos los providers necesarios
 */
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <ToastProvider>
            <BrowserRouter>
              {children}
            </BrowserRouter>
          </ToastProvider>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

/**
 * Utility para medir tiempo de render
 */
function measureRenderTime(component: React.ReactElement): number {
  const startTime = performance.now();
  render(component, { wrapper: AllTheProviders });
  const endTime = performance.now();
  return endTime - startTime;
}

/**
 * Utility para medir memoria (si está disponible)
 */
function measureMemoryUsage(): number | null {
  if ('memory' in performance && (performance as any).memory) {
    return (performance as any).memory.usedJSHeapSize;
  }
  return null;
}

describe('Performance Tests - Navegación', () => {
  beforeEach(() => {
    // Limpiar cache de React Query antes de cada test
    queryClient.clear();
  });

  describe('Nav Component', () => {
    it('debe renderizar en menos de 100ms', () => {
      const renderTime = measureRenderTime(<Nav />);
      
      console.log(`⏱️  Nav render time: ${renderTime.toFixed(2)}ms`);
      expect(renderTime).toBeLessThan(100);
    });

    it('no debe causar memory leaks en múltiples renders', () => {
      const initialMemory = measureMemoryUsage();
      
      // Renderizar y desmontar 10 veces
      for (let i = 0; i < 10; i++) {
        const { unmount } = render(<Nav />, { wrapper: AllTheProviders });
        unmount();
      }
      
      const finalMemory = measureMemoryUsage();
      
      if (initialMemory !== null && finalMemory !== null) {
        const memoryIncrease = finalMemory - initialMemory;
        const memoryIncreaseMB = memoryIncrease / (1024 * 1024);
        
        console.log(`💾 Memory increase: ${memoryIncreaseMB.toFixed(2)}MB`);
        
        // No debería incrementar más de 5MB
        expect(memoryIncreaseMB).toBeLessThan(5);
      }
    });
  });

  describe('SidebarLeft Component', () => {
    it('debe renderizar en menos de 150ms', () => {
      const renderTime = measureRenderTime(
        <SidebarLeft open={true} onClose={() => {}} role="estudiante" />
      );
      
      console.log(`⏱️  SidebarLeft render time: ${renderTime.toFixed(2)}ms`);
      expect(renderTime).toBeLessThan(150);
    });

    it('debe renderizar rápido con diferentes roles', () => {
      const roles = ['admin', 'coordinador', 'profesor', 'estudiante'];
      
      for (const role of roles) {
        const renderTime = measureRenderTime(
          <SidebarLeft open={true} onClose={() => {}} role={role} />
        );
        
        console.log(`⏱️  SidebarLeft (${role}): ${renderTime.toFixed(2)}ms`);
        expect(renderTime).toBeLessThan(150);
      }
    });
  });

  describe('SidebarRight Component', () => {
    it('debe renderizar en menos de 150ms', () => {
      const renderTime = measureRenderTime(
        <SidebarRight open={true} onClose={() => {}} role="estudiante" />
      );
      
      console.log(`⏱️  SidebarRight render time: ${renderTime.toFixed(2)}ms`);
      expect(renderTime).toBeLessThan(150);
    });
  });
});

describe('Performance Tests - Páginas', () => {
  describe('Home Page', () => {
    it('debe renderizar en menos de 200ms', () => {
      const renderTime = measureRenderTime(<Home />);
      
      console.log(`⏱️  Home page render time: ${renderTime.toFixed(2)}ms`);
      expect(renderTime).toBeLessThan(200);
    });
  });
});

describe('Performance Tests - React Query', () => {
  it('cache debe funcionar correctamente', async () => {
    // Mock de datos para cache
    queryClient.setQueryData(['test-key'], { data: 'cached data' });
    
    const startTime = performance.now();
    const cachedData = queryClient.getQueryData(['test-key']);
    const endTime = performance.now();
    
    const accessTime = endTime - startTime;
    
    console.log(`⚡ Cache access time: ${accessTime.toFixed(4)}ms`);
    
    expect(cachedData).toEqual({ data: 'cached data' });
    expect(accessTime).toBeLessThan(1); // Debe ser casi instantáneo
  });

  it('invalidación de cache debe ser rápida', () => {
    queryClient.setQueryData(['test-key'], { data: 'cached data' });
    
    const startTime = performance.now();
    queryClient.invalidateQueries({ queryKey: ['test-key'] });
    const endTime = performance.now();
    
    const invalidateTime = endTime - startTime;
    
    console.log(`🔄 Cache invalidate time: ${invalidateTime.toFixed(4)}ms`);
    expect(invalidateTime).toBeLessThan(5);
  });
});

describe('Performance Tests - Theme Context', () => {
  it('toggle de tema debe ser instantáneo', async () => {
    const { rerender } = render(
      <ThemeProvider>
        <div>Test</div>
      </ThemeProvider>
    );
    
    const startTime = performance.now();
    
    // Simular toggle de tema
    document.documentElement.classList.toggle('dark');
    
    rerender(
      <ThemeProvider>
        <div>Test</div>
      </ThemeProvider>
    );
    
    const endTime = performance.now();
    const toggleTime = endTime - startTime;
    
    console.log(`🌓 Theme toggle time: ${toggleTime.toFixed(2)}ms`);
    expect(toggleTime).toBeLessThan(50);
  });
});

/**
 * Test de bundle size (informativo)
 */
describe('Bundle Size Tests', () => {
  it('debería reportar tamaños de componentes principales', () => {
    const components = {
      Nav,
      SidebarLeft,
      SidebarRight,
      Home,
    };
    
    console.log('\n📦 Component Sizes (approximate):');
    for (const [name, Component] of Object.entries(components)) {
      const str = Component.toString();
      const sizeKB = new Blob([str]).size / 1024;
      console.log(`  ${name}: ~${sizeKB.toFixed(2)}KB`);
    }
  });
});

/**
 * Test de re-renders
 */
describe('Re-render Tests', () => {
  it('Nav no debe re-renderizar innecesariamente', () => {
    let renderCount = 0;
    
    const NavWithCounter = () => {
      renderCount++;
      return <Nav />;
    };
    
    const { rerender } = render(<NavWithCounter />, { wrapper: AllTheProviders });
    
    const initialRenderCount = renderCount;
    
    // Forzar re-render sin cambios de props
    rerender(<NavWithCounter />);
    rerender(<NavWithCounter />);
    rerender(<NavWithCounter />);
    
    const finalRenderCount = renderCount;
    const additionalRenders = finalRenderCount - initialRenderCount;
    
    console.log(`🔄 Additional re-renders: ${additionalRenders}`);
    
    // Debería renderizar máximo 4 veces (1 inicial + 3 forzados)
    expect(finalRenderCount).toBeLessThanOrEqual(4);
  });
});

/**
 * Test de carga inicial
 */
describe('Initial Load Performance', () => {
  it('app completa debe cargar en tiempo razonable', () => {
    const startTime = performance.now();
    
    render(
      <AllTheProviders>
        <Nav />
        <SidebarLeft open={false} onClose={() => {}} role="estudiante" />
        <SidebarRight open={false} onClose={() => {}} role="estudiante" />
      </AllTheProviders>
    );
    
    const endTime = performance.now();
    const loadTime = endTime - startTime;
    
    console.log(`🚀 Full app initial load: ${loadTime.toFixed(2)}ms`);
    
    // Carga completa debe ser menos de 500ms
    expect(loadTime).toBeLessThan(500);
  });
});
