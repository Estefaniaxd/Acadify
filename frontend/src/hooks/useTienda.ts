/**
 * Custom Hooks para Tienda
 * 
 * @module hooks/useTienda
 * @description Hooks personalizados para gestionar la tienda con React Query
 */

import { useQuery, useMutation, useQueryClient, UseQueryResult } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';
import tiendaService, {
  ProductoTienda,
  ProductosPaginados,
  CompraUsuario,
  ItemInventario,
  FiltrosProductos,
  RespuestaCompra,
  EstadisticasTienda,
} from '../services/tienda.service';
import { toast } from 'react-hot-toast';

// ==================== QUERY KEYS ====================

export const TIENDA_KEYS = {
  all: ['tienda'] as const,
  productos: (filtros?: FiltrosProductos) => [...TIENDA_KEYS.all, 'productos', filtros] as const,
  producto: (id: number) => [...TIENDA_KEYS.all, 'producto', id] as const,
  destacados: () => [...TIENDA_KEYS.all, 'destacados'] as const,
  compras: (pagina: number, porPagina: number) => [...TIENDA_KEYS.all, 'compras', pagina, porPagina] as const,
  compra: (id: number) => [...TIENDA_KEYS.all, 'compra', id] as const,
  inventario: () => [...TIENDA_KEYS.all, 'inventario'] as const,
  itemInventario: (id: number) => [...TIENDA_KEYS.all, 'item-inventario', id] as const,
  estadisticas: () => [...TIENDA_KEYS.all, 'estadisticas'] as const,
  categorias: () => [...TIENDA_KEYS.all, 'categorias'] as const,
  disponibilidad: (productoId: number, cantidad: number) => 
    [...TIENDA_KEYS.all, 'disponibilidad', productoId, cantidad] as const,
};

// ==================== HOOKS - PRODUCTOS ====================

/**
 * Hook para obtener productos con filtros
 */
export function useProductos(filtros?: FiltrosProductos) {
  return useQuery({
    queryKey: TIENDA_KEYS.productos(filtros),
    queryFn: () => tiendaService.obtenerProductos(filtros),
    staleTime: 2 * 60 * 1000, // 2 minutos
    gcTime: 5 * 60 * 1000, // 5 minutos
  });
}

/**
 * Hook para obtener un producto específico
 */
export function useProducto(productoId: number): UseQueryResult<ProductoTienda, Error> {
  return useQuery({
    queryKey: TIENDA_KEYS.producto(productoId),
    queryFn: () => tiendaService.obtenerProducto(productoId),
    enabled: !!productoId,
    staleTime: 5 * 60 * 1000, // 5 minutos
    gcTime: 10 * 60 * 1000, // 10 minutos
  });
}

/**
 * Hook para obtener productos destacados
 */
export function useProductosDestacados() {
  return useQuery({
    queryKey: TIENDA_KEYS.destacados(),
    queryFn: () => tiendaService.obtenerProductosDestacados(),
    staleTime: 5 * 60 * 1000, // 5 minutos
    gcTime: 10 * 60 * 1000,
  });
}

/**
 * Hook para obtener categorías
 */
export function useCategorias() {
  return useQuery({
    queryKey: TIENDA_KEYS.categorias(),
    queryFn: () => tiendaService.obtenerCategorias(),
    staleTime: 10 * 60 * 1000, // 10 minutos (no cambian frecuentemente)
    gcTime: 30 * 60 * 1000,
  });
}

// ==================== HOOKS - COMPRAS ====================

/**
 * Hook para realizar una compra
 */
export function useComprarProducto() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ productoId, cantidad = 1 }: { productoId: number; cantidad?: number }) =>
      tiendaService.comprarProducto(productoId, cantidad),
    onSuccess: (data: RespuestaCompra) => {
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: TIENDA_KEYS.inventario() });
      queryClient.invalidateQueries({ queryKey: TIENDA_KEYS.compras(1, 20) });
      queryClient.invalidateQueries({ queryKey: TIENDA_KEYS.estadisticas() });
      queryClient.invalidateQueries({ queryKey: ['gamificacion', 'mis-puntos'] }); // Actualizar puntos

      // Mostrar toast de éxito
      toast.success(data.mensaje || '¡Compra realizada con éxito!', {
        icon: '🎉',
        duration: 4000,
      });
    },
    onError: (error: any) => {
      const mensaje = error.response?.data?.detail || 'Error al realizar la compra';
      toast.error(mensaje, {
        icon: '❌',
        duration: 4000,
      });
    },
  });
}

/**
 * Hook para obtener historial de compras
 */
export function useHistorialCompras(pagina: number = 1, porPagina: number = 20) {
  const { user } = useAuth();

  return useQuery({
    queryKey: TIENDA_KEYS.compras(pagina, porPagina),
    queryFn: () => tiendaService.obtenerHistorialCompras(pagina, porPagina),
    enabled: !!user,
    staleTime: 60 * 1000, // 1 minuto
    gcTime: 5 * 60 * 1000,
  });
}

/**
 * Hook para obtener una compra específica
 */
export function useCompra(compraId: number): UseQueryResult<CompraUsuario, Error> {
  return useQuery({
    queryKey: TIENDA_KEYS.compra(compraId),
    queryFn: () => tiendaService.obtenerCompra(compraId),
    enabled: !!compraId,
    staleTime: 5 * 60 * 1000,
  });
}

// ==================== HOOKS - INVENTARIO ====================

/**
 * Hook para obtener el inventario del usuario
 */
export function useInventario(): UseQueryResult<ItemInventario[], Error> {
  const { user } = useAuth();

  return useQuery({
    queryKey: TIENDA_KEYS.inventario(),
    queryFn: () => tiendaService.obtenerInventario(),
    enabled: !!user,
    staleTime: 30 * 1000, // 30 segundos
    gcTime: 5 * 60 * 1000,
  });
}

/**
 * Hook para obtener un item del inventario
 */
export function useItemInventario(itemId: number): UseQueryResult<ItemInventario, Error> {
  return useQuery({
    queryKey: TIENDA_KEYS.itemInventario(itemId),
    queryFn: () => tiendaService.obtenerItemInventario(itemId),
    enabled: !!itemId,
    staleTime: 60 * 1000,
  });
}

/**
 * Hook para equipar un item
 */
export function useEquiparItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (itemId: number) => tiendaService.equiparItem(itemId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: TIENDA_KEYS.inventario() });
      queryClient.invalidateQueries({ queryKey: TIENDA_KEYS.itemInventario(data.item.id) });
      
      toast.success(data.mensaje || 'Item equipado', {
        icon: '✨',
      });
    },
    onError: (error: any) => {
      const mensaje = error.response?.data?.detail || 'Error al equipar item';
      toast.error(mensaje);
    },
  });
}

/**
 * Hook para desequipar un item
 */
export function useDesequiparItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (itemId: number) => tiendaService.desequiparItem(itemId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: TIENDA_KEYS.inventario() });
      queryClient.invalidateQueries({ queryKey: TIENDA_KEYS.itemInventario(data.item.id) });
      
      toast.success(data.mensaje || 'Item desequipado', {
        icon: '📦',
      });
    },
    onError: (error: any) => {
      const mensaje = error.response?.data?.detail || 'Error al desequipar item';
      toast.error(mensaje);
    },
  });
}

// ==================== HOOKS - ESTADÍSTICAS ====================

/**
 * Hook para obtener estadísticas de la tienda del usuario
 */
export function useEstadisticasTienda(): UseQueryResult<EstadisticasTienda, Error> {
  const { user } = useAuth();

  return useQuery({
    queryKey: TIENDA_KEYS.estadisticas(),
    queryFn: () => tiendaService.obtenerEstadisticas(),
    enabled: !!user,
    staleTime: 2 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

/**
 * Hook para verificar disponibilidad de compra
 */
export function useVerificarDisponibilidad(productoId: number, cantidad: number = 1) {
  return useQuery({
    queryKey: TIENDA_KEYS.disponibilidad(productoId, cantidad),
    queryFn: () => tiendaService.verificarDisponibilidad(productoId, cantidad),
    enabled: !!productoId,
    staleTime: 10 * 1000, // 10 segundos (cambia rápido)
    gcTime: 60 * 1000,
  });
}

// ==================== HOOK COMBINADO ====================

/**
 * Hook que combina datos principales de la tienda
 * Ideal para páginas principales
 */
export function useResumenTienda() {
  const productos = useProductos({ pagina: 1, por_pagina: 12 });
  const destacados = useProductosDestacados();
  const inventario = useInventario();
  const estadisticas = useEstadisticasTienda();

  return {
    productos: productos.data,
    destacados: destacados.data,
    inventario: inventario.data,
    estadisticas: estadisticas.data,
    isLoading: productos.isLoading || destacados.isLoading || inventario.isLoading || estadisticas.isLoading,
    isError: productos.isError || destacados.isError || inventario.isError || estadisticas.isError,
  };
}
