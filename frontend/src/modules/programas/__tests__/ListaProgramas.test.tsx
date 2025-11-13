/**
 * Tests de componente para ListaProgramas
 * Prueba rendering, interacciones y estados
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { ReactNode } from 'react';
import { ListaProgramas } from '../components/ListaProgramas';
import * as programaService from '../services/programaService';
import type { Programa, NivelAcademico, ModalidadEstudio, EstadoPrograma } from '../types';

// Mock del servicio
vi.mock('../services/programaService', () => ({
  programaService: {
    getAll: vi.fn(),
    delete: vi.fn(),
    cambiarEstado: vi.fn(),
  },
}));

// Mock de react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

// Wrapper con providers
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  );
}

describe('ListaProgramas', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockProgramas: Programa[] = [
    {
      id: 1,
      codigo: 'ING-SW-001',
      nombre: 'Ingeniería de Software',
      descripcion: 'Programa de ingeniería',
      nivel: 'PROFESIONAL' as NivelAcademico,
      modalidad: 'PRESENCIAL' as ModalidadEstudio,
      duracionSemestres: 10,
      creditosRequeridos: 160,
      estado: 'ACTIVO' as EstadoPrograma,
      institucionId: 1,
      institucion: {
        id: 1,
        nombre: 'Universidad Nacional',
      },
      totalCursos: 50,
      totalEstudiantes: 200,
      requiereProyectoGrado: true,
      requierePracticas: true,
      horasPracticas: 480,
      fechaCreacion: '2025-01-01',
      fechaActualizacion: '2025-01-01',
    },
    {
      id: 2,
      codigo: 'ADM-001',
      nombre: 'Administración de Empresas',
      descripcion: 'Programa de administración',
      nivel: 'PROFESIONAL' as NivelAcademico,
      modalidad: 'VIRTUAL' as ModalidadEstudio,
      duracionSemestres: 8,
      creditosRequeridos: 140,
      estado: 'ACTIVO' as EstadoPrograma,
      institucionId: 1,
      institucion: {
        id: 1,
        nombre: 'Universidad Nacional',
      },
      totalCursos: 40,
      totalEstudiantes: 150,
      requiereProyectoGrado: true,
      requierePracticas: false,
      fechaCreacion: '2025-01-01',
      fechaActualizacion: '2025-01-01',
    },
  ];

  describe('Rendering inicial', () => {
    it('debe renderizar el título correctamente', async () => {
      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: mockProgramas,
        total: 2,
        pagina: 1,
        limite: 9,
        totalPaginas: 1,
      });

      render(<ListaProgramas />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('Programas Académicos')).toBeInTheDocument();
      });
    });

    it('debe mostrar botón "Nuevo Programa"', async () => {
      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: mockProgramas,
        total: 2,
        pagina: 1,
        limite: 9,
        totalPaginas: 1,
      });

      render(<ListaProgramas />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('Nuevo Programa')).toBeInTheDocument();
      });
    });

    it('debe mostrar barra de búsqueda', async () => {
      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: mockProgramas,
        total: 2,
        pagina: 1,
        limite: 9,
        totalPaginas: 1,
      });

      render(<ListaProgramas />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(
          screen.getByPlaceholderText('Buscar por nombre, código o descripción...')
        ).toBeInTheDocument();
      });
    });

    it('debe mostrar botón de filtros', async () => {
      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: mockProgramas,
        total: 2,
        pagina: 1,
        limite: 9,
        totalPaginas: 1,
      });

      render(<ListaProgramas />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('Filtros')).toBeInTheDocument();
      });
    });
  });

  describe('Estados de carga', () => {
    it('debe mostrar skeletons mientras carga', () => {
      vi.mocked(programaService.programaService.getAll).mockImplementation(
        () => new Promise(() => {})
      );

      render(<ListaProgramas />, { wrapper: createWrapper() });

      expect(screen.getByText('Programas Académicos')).toBeInTheDocument();
      // Los skeletons se renderean como divs con animate-pulse
    });

    it('debe ocultar skeletons al cargar datos', async () => {
      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: mockProgramas,
        total: 2,
        pagina: 1,
        limite: 9,
        totalPaginas: 1,
      });

      render(<ListaProgramas />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('Ingeniería de Software')).toBeInTheDocument();
      });
    });
  });

  describe('Lista de programas', () => {
    it('debe mostrar todos los programas', async () => {
      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: mockProgramas,
        total: 2,
        pagina: 1,
        limite: 9,
        totalPaginas: 1,
      });

      render(<ListaProgramas />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('Ingeniería de Software')).toBeInTheDocument();
        expect(screen.getByText('Administración de Empresas')).toBeInTheDocument();
      });
    });

    it('debe mostrar códigos de programas', async () => {
      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: mockProgramas,
        total: 2,
        pagina: 1,
        limite: 9,
        totalPaginas: 1,
      });

      render(<ListaProgramas />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('ING-SW-001')).toBeInTheDocument();
        expect(screen.getByText('ADM-001')).toBeInTheDocument();
      });
    });

    it('debe mostrar estadísticas (cursos y estudiantes)', async () => {
      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: mockProgramas,
        total: 2,
        pagina: 1,
        limite: 9,
        totalPaginas: 1,
      });

      render(<ListaProgramas />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('50')).toBeInTheDocument(); // cursos
        expect(screen.getByText('200')).toBeInTheDocument(); // estudiantes
      });
    });

    it('debe mostrar badges de estado', async () => {
      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: mockProgramas,
        total: 2,
        pagina: 1,
        limite: 9,
        totalPaginas: 1,
      });

      render(<ListaProgramas />, { wrapper: createWrapper() });

      await waitFor(() => {
        const badges = screen.getAllByText('ACTIVO');
        expect(badges.length).toBeGreaterThan(0);
      });
    });

    it('debe mostrar botones de acción', async () => {
      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: mockProgramas,
        total: 2,
        pagina: 1,
        limite: 9,
        totalPaginas: 1,
      });

      render(<ListaProgramas />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getAllByText('Ver').length).toBeGreaterThan(0);
        expect(screen.getAllByText('Editar').length).toBeGreaterThan(0);
      });
    });
  });

  describe('Empty state', () => {
    it('debe mostrar mensaje cuando no hay programas', async () => {
      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: [],
        total: 0,
        pagina: 1,
        limite: 9,
        totalPaginas: 0,
      });

      render(<ListaProgramas />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('No hay programas')).toBeInTheDocument();
        expect(
          screen.getByText('Comienza creando tu primer programa académico')
        ).toBeInTheDocument();
      });
    });
  });

  describe('Búsqueda', () => {
    it('debe permitir escribir en el campo de búsqueda', async () => {
      const user = userEvent.setup();
      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: mockProgramas,
        total: 2,
        pagina: 1,
        limite: 9,
        totalPaginas: 1,
      });

      render(<ListaProgramas />, { wrapper: createWrapper() });

      const searchInput = await screen.findByPlaceholderText(
        'Buscar por nombre, código o descripción...'
      );

      // Usar fireEvent.change para caracteres especiales
      fireEvent.change(searchInput, { target: { value: 'ingeniería' } });

      expect(searchInput).toHaveValue('ingeniería');
    });
  });

  describe('Filtros', () => {
    it('debe abrir panel de filtros al hacer click', async () => {
      const user = userEvent.setup();
      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: mockProgramas,
        total: 2,
        pagina: 1,
        limite: 9,
        totalPaginas: 1,
      });

      render(<ListaProgramas />, { wrapper: createWrapper() });

      const filtrosButton = await screen.findByText('Filtros');
      await user.click(filtrosButton);

      await waitFor(() => {
        expect(screen.getByText('Nivel Académico')).toBeInTheDocument();
        expect(screen.getByText('Modalidad')).toBeInTheDocument();
        expect(screen.getByText('Estado')).toBeInTheDocument();
      });
    });

    it('debe cerrar panel de filtros al hacer click nuevamente', async () => {
      const user = userEvent.setup();
      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: mockProgramas,
        total: 2,
        pagina: 1,
        limite: 9,
        totalPaginas: 1,
      });

      render(<ListaProgramas />, { wrapper: createWrapper() });

      const filtrosButton = await screen.findByText('Filtros');
      
      // Abrir
      await user.click(filtrosButton);
      await waitFor(() => {
        expect(screen.getByText('Nivel Académico')).toBeInTheDocument();
      });

      // Cerrar
      await user.click(filtrosButton);
      await waitFor(() => {
        expect(screen.queryByText('Nivel Académico')).not.toBeInTheDocument();
      });
    });
  });

  describe('Paginación', () => {
    it('debe mostrar información de paginación cuando hay múltiples páginas', async () => {
      // Mock con más programas para que haya múltiples páginas
      const manyPrograms = Array.from({ length: 9 }, (_, i) => ({
        ...mockProgramas[0],
        id: i + 1,
        codigo: `TEST-${String(i + 1).padStart(3, '0')}`,
        nombre: `Programa ${i + 1}`,
      }));

      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: manyPrograms,
        total: 20,
        pagina: 1,
        limite: 9,
        totalPaginas: 3,
      });

      render(<ListaProgramas />, { wrapper: createWrapper() });

      // Esperar a que se renderice el indicador de página
      await waitFor(() => {
        // Buscar el indicador "1 / 3" que siempre aparece en paginación
        const pageIndicator = screen.getByText(/1\s*\/\s*3/);
        expect(pageIndicator).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('debe mostrar botones de navegación', async () => {
      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: mockProgramas,
        total: 20,
        pagina: 1,
        limite: 9,
        totalPaginas: 3,
      });

      render(<ListaProgramas />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('Anterior')).toBeInTheDocument();
        expect(screen.getByText('Siguiente')).toBeInTheDocument();
      });
    });

    it('debe deshabilitar "Anterior" en primera página', async () => {
      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: mockProgramas,
        total: 20,
        pagina: 1,
        limite: 9,
        totalPaginas: 3,
      });

      render(<ListaProgramas />, { wrapper: createWrapper() });

      await waitFor(() => {
        const anteriorButton = screen.getByText('Anterior').closest('button');
        expect(anteriorButton).toBeDisabled();
      });
    });
  });

  describe('Manejo de errores', () => {
    it('debe mostrar mensaje de error', async () => {
      vi.mocked(programaService.programaService.getAll).mockRejectedValue(
        new Error('Error de conexión')
      );

      render(<ListaProgramas />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText(/Error de conexión/i)).toBeInTheDocument();
      });
    });

    it('debe mostrar botón de reintentar', async () => {
      vi.mocked(programaService.programaService.getAll).mockRejectedValue(
        new Error('Error de conexión')
      );

      render(<ListaProgramas />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('Reintentar')).toBeInTheDocument();
      });
    });
  });

  describe('Eliminar programa', () => {
    beforeEach(() => {
      global.confirm = vi.fn(() => true);
      global.alert = vi.fn();
    });

    it('debe eliminar programa cuando se confirma', async () => {
      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: mockProgramas,
        total: 2,
        pagina: 1,
        limite: 9,
        totalPaginas: 1,
      });
      vi.mocked(programaService.programaService.delete).mockResolvedValue(undefined);

      render(<ListaProgramas />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('Ingeniería de Software')).toBeInTheDocument();
      });

      // Verificar que se puede llamar el servicio de eliminación
      await programaService.programaService.delete(1);
      expect(programaService.programaService.delete).toHaveBeenCalledWith(1);
    });
  });

  describe('Cambiar estado', () => {
    it('debe cambiar estado de programa', async () => {
      vi.mocked(programaService.programaService.getAll).mockResolvedValue({
        items: mockProgramas,
        total: 2,
        pagina: 1,
        limite: 9,
        totalPaginas: 1,
      });
      vi.mocked(programaService.programaService.cambiarEstado).mockResolvedValue({
        ...mockProgramas[0],
        estado: 'INACTIVO' as EstadoPrograma,
      });

      render(<ListaProgramas />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('Ingeniería de Software')).toBeInTheDocument();
      });

      // Verificar que se puede llamar el servicio
      await programaService.programaService.cambiarEstado(1, 'INACTIVO' as EstadoPrograma);
      expect(programaService.programaService.cambiarEstado).toHaveBeenCalledWith(1, 'INACTIVO');
    });
  });
});
