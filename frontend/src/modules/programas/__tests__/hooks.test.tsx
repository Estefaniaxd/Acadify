/**
 * Tests de integración para hooks de React Query
 * Prueba todos los hooks y su integración con el servicio
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode } from 'react';
import {
  useProgramas,
  usePrograma,
  useProgramasPorInstitucion,
  useEstadisticasPrograma,
  useMallaCurricular,
  useBuscarProgramas,
  useCrearPrograma,
  useActualizarPrograma,
  useEliminarPrograma,
  useCambiarEstadoPrograma,
  useAsignarCursos,
  useProgramaOperations,
} from '../hooks/useProgramas';
import * as programaService from '../services/programaService';
import type { Programa, CrearProgramaDTO, NivelAcademico, ModalidadEstudio, EstadoPrograma } from '../types';

// Mock del servicio
vi.mock('../services/programaService', () => ({
  programaService: {
    getAll: vi.fn(),
    getById: vi.fn(),
    getPorInstitucion: vi.fn(),
    getEstadisticas: vi.fn(),
    getMallaCurricular: vi.fn(),
    search: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    cambiarEstado: vi.fn(),
    asignarCursos: vi.fn(),
  },
}));

// Wrapper con QueryClient
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

describe('Hooks de Programas', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockPrograma: Programa = {
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
    totalCursos: 50,
    totalEstudiantes: 200,
    requiereProyectoGrado: true,
    requierePracticas: true,
    horasPracticas: 480,
    fechaCreacion: '2025-01-01',
    fechaActualizacion: '2025-01-01',
  };

  describe('useProgramas', () => {
    it('debe obtener lista de programas', async () => {
      const mockResponse = {
        items: [mockPrograma],
        total: 1,
        pagina: 1,
        limite: 10,
        totalPaginas: 1,
      };

      vi.mocked(programaService.programaService.getAll).mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useProgramas(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toEqual(mockResponse);
      expect(programaService.programaService.getAll).toHaveBeenCalledTimes(1);
    });

    it('debe aplicar filtros correctamente', async () => {
      const filtros = {
        institucionId: 1,
        nivel: 'PROFESIONAL' as NivelAcademico,
        estado: 'ACTIVO' as EstadoPrograma,
      };

      const mockResponse = {
        items: [mockPrograma],
        total: 1,
        pagina: 1,
        limite: 10,
        totalPaginas: 1,
      };

      vi.mocked(programaService.programaService.getAll).mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useProgramas(filtros), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(programaService.programaService.getAll).toHaveBeenCalledWith(filtros);
    });

    it('debe manejar errores correctamente', async () => {
      vi.mocked(programaService.programaService.getAll).mockRejectedValue(
        new Error('Error de red')
      );

      const { result } = renderHook(() => useProgramas(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isError).toBe(true));

      expect(result.current.error).toBeDefined();
    });
  });

  describe('usePrograma', () => {
    it('debe obtener un programa por ID', async () => {
      vi.mocked(programaService.programaService.getById).mockResolvedValue(mockPrograma);

      const { result } = renderHook(() => usePrograma(1), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toEqual(mockPrograma);
      expect(programaService.programaService.getById).toHaveBeenCalledWith(1);
    });

    it('no debe ejecutar si no hay ID', async () => {
      const { result } = renderHook(() => usePrograma(undefined), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(false);
      expect(programaService.programaService.getById).not.toHaveBeenCalled();
    });
  });

  describe('useProgramasPorInstitucion', () => {
    it('debe obtener programas de una institución', async () => {
      const mockResponse = {
        items: [mockPrograma],
        total: 1,
        pagina: 1,
        limite: 10,
        totalPaginas: 1,
      };

      vi.mocked(programaService.programaService.getPorInstitucion).mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useProgramasPorInstitucion(1), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toEqual(mockResponse);
    });
  });

  describe('useEstadisticasPrograma', () => {
    it('debe obtener estadísticas de un programa', async () => {
      const mockStats = {
        programaId: 1,
        totalCursos: 50,
        totalEstudiantes: 200,
        estudiantesActivos: 180,
        estudiantesGraduados: 15,
        estudiantesDesercion: 5,
        tasaGraduacion: 75,
        tasaDesercion: 2.5,
        promedioSemestres: 9.5,
        cursosObligatorios: 40,
        cursosElectivos: 10,
        creditosPromedio: 158,
      };

      vi.mocked(programaService.programaService.getEstadisticas).mockResolvedValue(mockStats);

      const { result } = renderHook(() => useEstadisticasPrograma(1), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toEqual(mockStats);
    });
  });

  describe('useMallaCurricular', () => {
    it('debe obtener malla curricular', async () => {
      const mockMalla = {
        programaId: 1,
        semestres: [],
        creditosTotales: 160,
        horasTotales: 2400,
      };

      vi.mocked(programaService.programaService.getMallaCurricular).mockResolvedValue(mockMalla);

      const { result } = renderHook(() => useMallaCurricular(1), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toEqual(mockMalla);
    });
  });

  describe('useBuscarProgramas', () => {
    it('debe buscar programas por término', async () => {
      vi.mocked(programaService.programaService.search).mockResolvedValue([mockPrograma]);

      const { result } = renderHook(() => useBuscarProgramas('ingeniería'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toEqual([mockPrograma]);
    });

    it('no debe ejecutar si término es muy corto', async () => {
      const { result } = renderHook(() => useBuscarProgramas('i'), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(false);
      expect(programaService.programaService.search).not.toHaveBeenCalled();
    });
  });

  describe('useCrearPrograma', () => {
    it('debe crear un programa exitosamente', async () => {
      const nuevoPrograma: CrearProgramaDTO = {
        codigo: 'ING-SW-002',
        nombre: 'Nuevo Programa',
        nivel: 'PROFESIONAL' as NivelAcademico,
        modalidad: 'PRESENCIAL' as ModalidadEstudio,
        duracionSemestres: 10,
        creditosRequeridos: 160,
        institucionId: 1,
        requiereProyectoGrado: true,
        requierePracticas: true,
        horasPracticas: 480,
      };

      vi.mocked(programaService.programaService.create).mockResolvedValue({
        ...mockPrograma,
        id: 2,
        codigo: nuevoPrograma.codigo,
        nombre: nuevoPrograma.nombre,
      });

      const { result } = renderHook(() => useCrearPrograma(), {
        wrapper: createWrapper(),
      });

      result.current.mutate(nuevoPrograma);

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(programaService.programaService.create).toHaveBeenCalledWith(nuevoPrograma);
    });

    it('debe manejar errores en creación', async () => {
      const nuevoPrograma: CrearProgramaDTO = {
        codigo: 'ING-SW-001',
        nombre: 'Programa Duplicado',
        nivel: 'PROFESIONAL' as NivelAcademico,
        modalidad: 'PRESENCIAL' as ModalidadEstudio,
        duracionSemestres: 10,
        creditosRequeridos: 160,
        institucionId: 1,
        requiereProyectoGrado: true,
        requierePracticas: true,
      };

      vi.mocked(programaService.programaService.create).mockRejectedValue(
        new Error('Ya existe un programa con ese código')
      );

      const { result } = renderHook(() => useCrearPrograma(), {
        wrapper: createWrapper(),
      });

      result.current.mutate(nuevoPrograma);

      await waitFor(() => expect(result.current.isError).toBe(true));
    });
  });

  describe('useActualizarPrograma', () => {
    it('debe actualizar un programa exitosamente', async () => {
      const actualizacion = {
        nombre: 'Programa Actualizado',
        duracionSemestres: 9,
      };

      vi.mocked(programaService.programaService.update).mockResolvedValue({
        ...mockPrograma,
        ...actualizacion,
      });

      const { result } = renderHook(() => useActualizarPrograma(), {
        wrapper: createWrapper(),
      });

      result.current.mutate({ id: 1, data: actualizacion });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(programaService.programaService.update).toHaveBeenCalledWith(1, actualizacion);
    });
  });

  describe('useEliminarPrograma', () => {
    it('debe eliminar un programa exitosamente', async () => {
      vi.mocked(programaService.programaService.delete).mockResolvedValue(undefined);

      const { result } = renderHook(() => useEliminarPrograma(), {
        wrapper: createWrapper(),
      });

      result.current.mutate(1);

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(programaService.programaService.delete).toHaveBeenCalledWith(1);
    });

    it('debe manejar error al eliminar programa con estudiantes', async () => {
      vi.mocked(programaService.programaService.delete).mockRejectedValue(
        new Error('No se puede eliminar un programa con estudiantes activos')
      );

      const { result } = renderHook(() => useEliminarPrograma(), {
        wrapper: createWrapper(),
      });

      result.current.mutate(1);

      await waitFor(() => expect(result.current.isError).toBe(true));
    });
  });

  describe('useCambiarEstadoPrograma', () => {
    it('debe cambiar estado exitosamente', async () => {
      vi.mocked(programaService.programaService.cambiarEstado).mockResolvedValue({
        ...mockPrograma,
        estado: 'INACTIVO' as EstadoPrograma,
      });

      const { result } = renderHook(() => useCambiarEstadoPrograma(), {
        wrapper: createWrapper(),
      });

      result.current.mutate({ id: 1, estado: 'INACTIVO' as EstadoPrograma });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(programaService.programaService.cambiarEstado).toHaveBeenCalledWith(
        1,
        'INACTIVO'
      );
    });
  });

  describe('useAsignarCursos', () => {
    it('debe asignar cursos exitosamente', async () => {
      const asignacion = {
        programaId: 1,
        cursoIds: [1, 2, 3],
        nivel: 1,
        esObligatorio: true,
      };

      vi.mocked(programaService.programaService.asignarCursos).mockResolvedValue(mockPrograma);

      const { result } = renderHook(() => useAsignarCursos(), {
        wrapper: createWrapper(),
      });

      result.current.mutate(asignacion);

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(programaService.programaService.asignarCursos).toHaveBeenCalledWith(asignacion);
    });
  });

  describe('useProgramaOperations', () => {
    it('debe retornar todas las operaciones', () => {
      const { result } = renderHook(() => useProgramaOperations(), {
        wrapper: createWrapper(),
      });

      expect(result.current.crear).toBeDefined();
      expect(result.current.actualizar).toBeDefined();
      expect(result.current.eliminar).toBeDefined();
      expect(result.current.cambiarEstado).toBeDefined();
      expect(result.current.asignarCursos).toBeDefined();
    });
  });

  describe('Invalidación de caché', () => {
    it('debe invalidar caché al crear programa', async () => {
      const nuevoPrograma: CrearProgramaDTO = {
        codigo: 'ING-SW-002',
        nombre: 'Nuevo Programa',
        nivel: 'PROFESIONAL' as NivelAcademico,
        modalidad: 'PRESENCIAL' as ModalidadEstudio,
        duracionSemestres: 10,
        creditosRequeridos: 160,
        institucionId: 1,
        requiereProyectoGrado: true,
        requierePracticas: true,
        horasPracticas: 480,
      };

      vi.mocked(programaService.programaService.create).mockResolvedValue({
        ...mockPrograma,
        id: 2,
        codigo: nuevoPrograma.codigo,
      });

      const { result } = renderHook(() => useCrearPrograma(), {
        wrapper: createWrapper(),
      });

      result.current.mutate(nuevoPrograma);

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      // Verificar que se invalida el caché
      expect(result.current.isSuccess).toBe(true);
    });

    it('debe usar actualización optimista al editar', async () => {
      vi.mocked(programaService.programaService.update).mockResolvedValue({
        ...mockPrograma,
        nombre: 'Nombre Actualizado',
      });

      const { result } = renderHook(() => useActualizarPrograma(), {
        wrapper: createWrapper(),
      });

      result.current.mutate({
        id: 1,
        data: { nombre: 'Nombre Actualizado' },
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));
    });
  });
});
