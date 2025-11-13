/**
 * Tests para los hooks de instituciones
 * Pruebas de integración con React Query
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode } from 'react';
import {
  useInstituciones,
  useInstitucion,
  useCrearInstitucion,
  useActualizarInstitucion,
  useEliminarInstitucion,
} from '../hooks/useInstituciones';
import { institucionService } from '../services/institucionService';

// Mock del servicio
vi.mock('../services/institucionService');

// Wrapper para React Query
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('Hooks de Instituciones', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('useInstituciones', () => {
    it('debe obtener lista de instituciones', async () => {
      const mockData = {
        items: [
          { id: '1', nombre: 'Universidad A', activo: true, fechaCreacion: '2025-10-31' },
          { id: '2', nombre: 'Universidad B', activo: true, fechaCreacion: '2025-10-31' },
        ],
        total: 2,
        pagina: 1,
        limite: 10,
        totalPaginas: 1,
      };

      vi.mocked(institucionService.getAll).mockResolvedValue(mockData);

      const { result } = renderHook(() => useInstituciones(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(true);

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.data?.items).toHaveLength(2);
      expect(result.current.data?.total).toBe(2);
    });

    it('debe aplicar filtros', async () => {
      const mockData = {
        items: [
          { id: '1', nombre: 'Universidad Activa', activo: true, fechaCreacion: '2025-10-31' },
        ],
        total: 1,
        pagina: 1,
        limite: 10,
        totalPaginas: 1,
      };

      vi.mocked(institucionService.getAll).mockResolvedValue(mockData);

      const { result } = renderHook(
        () =>
          useInstituciones({
            activo: true,
            busqueda: 'Universidad',
          }),
        {
          wrapper: createWrapper(),
        }
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.data?.items).toHaveLength(1);
      expect(institucionService.getAll).toHaveBeenCalledWith({
        activo: true,
        busqueda: 'Universidad',
      });
    });

    it('debe manejar errores', async () => {
      vi.mocked(institucionService.getAll).mockRejectedValue(
        new Error('Error de red')
      );

      const { result } = renderHook(() => useInstituciones(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBeDefined();
    });
  });

  describe('useInstitucion', () => {
    it('debe obtener una institución por ID', async () => {
      const mockInstitucion = {
        id: '1',
        nombre: 'Universidad Test',
        descripcion: 'Descripción test',
        activo: true,
        fechaCreacion: '2025-10-31',
      };

      vi.mocked(institucionService.getById).mockResolvedValue(mockInstitucion);

      const { result } = renderHook(() => useInstitucion('1'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.data?.nombre).toBe('Universidad Test');
    });

    it('no debe ejecutar query si no hay ID', () => {
      const { result } = renderHook(() => useInstitucion(undefined), {
        wrapper: createWrapper(),
      });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.data).toBeUndefined();
    });
  });

  describe('useCrearInstitucion', () => {
    it('debe crear una institución', async () => {
      const nuevaInstitucion = {
        nombre: 'Nueva Universidad',
        email: 'test@universidad.edu',
        colorPrimario: '#3B82F6',
        colorSecundario: '#8B5CF6',
      };

      const mockResponse = {
        id: '1',
        ...nuevaInstitucion,
        activo: true,
        fechaCreacion: '2025-10-31',
      };

      vi.mocked(institucionService.create).mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useCrearInstitucion(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isPending).toBe(false);

      result.current.mutate(nuevaInstitucion);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(institucionService.create).toHaveBeenCalledWith(nuevaInstitucion);
    });

    it('debe manejar errores al crear', async () => {
      vi.mocked(institucionService.create).mockRejectedValue(
        new Error('Datos inválidos')
      );

      const { result } = renderHook(() => useCrearInstitucion(), {
        wrapper: createWrapper(),
      });

      result.current.mutate({
        nombre: 'Test',
        colorPrimario: '#3B82F6',
        colorSecundario: '#8B5CF6',
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBeDefined();
    });
  });

  describe('useActualizarInstitucion', () => {
    it('debe actualizar una institución', async () => {
      const datosActualizacion = {
        id: '1',
        data: { nombre: 'Universidad Actualizada' },
      };

      const mockResponse = {
        id: '1',
        nombre: 'Universidad Actualizada',
        activo: true,
        fechaCreacion: '2025-10-31',
        fechaActualizacion: '2025-10-31',
      };

      vi.mocked(institucionService.update).mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useActualizarInstitucion(), {
        wrapper: createWrapper(),
      });

      result.current.mutate(datosActualizacion);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(institucionService.update).toHaveBeenCalledWith(
        '1',
        { nombre: 'Universidad Actualizada' }
      );
    });
  });

  describe('useEliminarInstitucion', () => {
    it('debe eliminar una institución', async () => {
      vi.mocked(institucionService.delete).mockResolvedValue();

      const { result } = renderHook(() => useEliminarInstitucion(), {
        wrapper: createWrapper(),
      });

      result.current.mutate('1');

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(institucionService.delete).toHaveBeenCalledWith('1');
    });

    it('debe manejar errores al eliminar', async () => {
      vi.mocked(institucionService.delete).mockRejectedValue(
        new Error('No tienes permisos')
      );

      const { result } = renderHook(() => useEliminarInstitucion(), {
        wrapper: createWrapper(),
      });

      result.current.mutate('1');

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      expect(result.current.error).toBeDefined();
    });
  });

  describe('Invalidación de caché', () => {
    it('debe invalidar caché al crear institución', async () => {
      const queryClient = new QueryClient({
        defaultOptions: {
          queries: { retry: false },
          mutations: { retry: false },
        },
      });

      const invalidateQueriesSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const mockResponse = {
        id: '1',
        nombre: 'Nueva',
        activo: true,
        fechaCreacion: '2025-10-31',
      };

      vi.mocked(institucionService.create).mockResolvedValue(mockResponse);

      const wrapper = ({ children }: { children: ReactNode }) => (
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
      );

      const { result } = renderHook(() => useCrearInstitucion(), { wrapper });

      result.current.mutate({
        nombre: 'Nueva',
        colorPrimario: '#3B82F6',
        colorSecundario: '#8B5CF6',
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // Verificar que se invalidó el caché
      expect(invalidateQueriesSpy).toHaveBeenCalled();
    });
  });

  describe('Optimistic updates', () => {
    it('debe actualizar el caché optimistamente', async () => {
      const queryClient = new QueryClient({
        defaultOptions: {
          queries: { retry: false },
          mutations: { retry: false },
        },
      });

      const setQueryDataSpy = vi.spyOn(queryClient, 'setQueryData');

      const mockResponse = {
        id: '1',
        nombre: 'Universidad Actualizada',
        activo: true,
        fechaCreacion: '2025-10-31',
        fechaActualizacion: '2025-10-31',
      };

      vi.mocked(institucionService.update).mockResolvedValue(mockResponse);

      const wrapper = ({ children }: { children: ReactNode }) => (
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
      );

      const { result } = renderHook(() => useActualizarInstitucion(), { wrapper });

      result.current.mutate({
        id: '1',
        data: { nombre: 'Universidad Actualizada' },
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // Verificar que se actualizó el caché
      expect(setQueryDataSpy).toHaveBeenCalled();
    });
  });
});
