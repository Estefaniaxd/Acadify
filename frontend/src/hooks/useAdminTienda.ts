/**
 * React Query Hooks para Administración de Tienda
 * 
 * @module hooks/useAdminTienda
 * @description Hooks para gestionar productos de la tienda desde el panel de admin
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import adminTiendaService, {
  CrearProductoRequest,
  ActualizarProductoRequest,
  FiltrosProductosAdmin,
  EstadisticasVentas,
} from '../services/adminTienda.service';
import { ProductoTienda } from '../services/tienda.service';
import { useToast } from '../context/ToastContext';

// ==================== QUERY KEYS ====================

export const adminTiendaKeys = {
  all: ['admin', 'tienda'] as const,
  productos: () => [...adminTiendaKeys.all, 'productos'] as const,
  productosList: (filtros?: FiltrosProductosAdmin) =>
    [...adminTiendaKeys.productos(), { filtros }] as const,
  producto: (id: number) => [...adminTiendaKeys.productos(), id] as const,
  estadisticas: () => [...adminTiendaKeys.all, 'estadisticas'] as const,
};

// ==================== QUERIES ====================

/**
 * Hook para obtener lista de productos (admin)
 */
export function useAdminProductos(filtros?: FiltrosProductosAdmin) {
  return useQuery({
    queryKey: adminTiendaKeys.productosList(filtros),
    queryFn: () => adminTiendaService.listarProductos(filtros),
    staleTime: 2 * 60 * 1000, // 2 minutos
  });
}

/**
 * Hook para obtener un producto específico
 */
export function useAdminProducto(productoId: number) {
  return useQuery({
    queryKey: adminTiendaKeys.producto(productoId),
    queryFn: () => adminTiendaService.obtenerProducto(productoId),
    enabled: !!productoId,
  });
}

/**
 * Hook para obtener estadísticas de ventas
 */
export function useEstadisticasVentas() {
  return useQuery<EstadisticasVentas>({
    queryKey: adminTiendaKeys.estadisticas(),
    queryFn: () => adminTiendaService.obtenerEstadisticas(),
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}

// ==================== MUTATIONS ====================

/**
 * Hook para crear un nuevo producto
 */
export function useCrearProducto() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: (data: CrearProductoRequest) => adminTiendaService.crearProducto(data),
    onSuccess: () => {
      // Invalida todas las queries de productos
      queryClient.invalidateQueries({ queryKey: adminTiendaKeys.productos() });
      queryClient.invalidateQueries({ queryKey: adminTiendaKeys.estadisticas() });
      
      toast.success('Producto creado exitosamente');
    },
    onError: (error: unknown) => {
      const mensaje = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Error al crear el producto';
      toast.error('Error', mensaje);
      console.error('Error al crear producto:', error);
    },
  });
}

/**
 * Hook para actualizar un producto existente
 */
export function useActualizarProducto() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: ({
      productoId,
      data,
    }: {
      productoId: number;
      data: ActualizarProductoRequest;
    }) => adminTiendaService.actualizarProducto(productoId, data),
    onMutate: async ({ productoId, data }) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: adminTiendaKeys.producto(productoId) });

      const previousProducto = queryClient.getQueryData<ProductoTienda>(
        adminTiendaKeys.producto(productoId)
      );

      if (previousProducto) {
        queryClient.setQueryData<ProductoTienda>(
          adminTiendaKeys.producto(productoId),
          { ...previousProducto, ...data }
        );
      }

      return { previousProducto };
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: adminTiendaKeys.productos() });
      queryClient.invalidateQueries({
        queryKey: adminTiendaKeys.producto(variables.productoId),
      });
      queryClient.invalidateQueries({ queryKey: adminTiendaKeys.estadisticas() });
      
      toast.success('Producto actualizado exitosamente');
    },
    onError: (error: unknown, variables, context) => {
      // Revertir optimistic update
      if (context?.previousProducto) {
        queryClient.setQueryData(
          adminTiendaKeys.producto(variables.productoId),
          context.previousProducto
        );
      }

      const mensaje = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Error al actualizar el producto';
      toast.error('Error', mensaje);
      console.error('Error al actualizar producto:', error);
    },
  });
}

/**
 * Hook para eliminar un producto
 */
export function useEliminarProducto() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: (productoId: number) => adminTiendaService.eliminarProducto(productoId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminTiendaKeys.productos() });
      queryClient.invalidateQueries({ queryKey: adminTiendaKeys.estadisticas() });
      
      toast.success('Producto eliminado exitosamente');
    },
    onError: (error: unknown) => {
      const mensaje = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Error al eliminar el producto';
      toast.error('Error', mensaje);
      console.error('Error al eliminar producto:', error);
    },
  });
}

/**
 * Hook para calcular precio automático
 */
export function useCalcularPrecio() {
  return {
    calcular: adminTiendaService.calcularPrecioAutomatico.bind(adminTiendaService),
  };
}
