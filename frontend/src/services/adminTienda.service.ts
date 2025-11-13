/**
 * Servicio de Administración de Tienda
 * 
 * @module services/adminTienda.service
 * @description Servicio para que administradores gestionen productos de la tienda
 */

import { api } from '../utils/api';
import { CategoriaProducto, RarezaProducto, ProductoTienda } from './tienda.service';

// ==================== INTERFACES ====================

/**
 * Request para crear un nuevo producto
 */
export interface CrearProductoRequest {
  nombre: string;
  descripcion?: string;
  categoria: CategoriaProducto;
  rareza: RarezaProducto;
  precio_puntos?: number;
  usar_precio_automatico?: boolean;
  nivel_minimo_requerido?: number;
  stock_limitado?: boolean;
  stock_disponible?: number;
  es_consumible?: boolean;
  usos_maximos?: number;
  disponible_desde?: string;
  disponible_hasta?: string;
  activo?: boolean;
  imagen_url?: string;
  preview_url?: string;
  color_hex?: string;
}

/**
 * Request para actualizar un producto existente
 */
export interface ActualizarProductoRequest {
  nombre?: string;
  descripcion?: string;
  precio_puntos?: number;
  rareza?: RarezaProducto;
  nivel_minimo_requerido?: number;
  stock_disponible?: number;
  disponible_desde?: string;
  disponible_hasta?: string;
  activo?: boolean;
  imagen_url?: string;
  preview_url?: string;
  color_hex?: string;
}

/**
 * Estadísticas de ventas de la tienda
 */
export interface EstadisticasVentas {
  total_ventas: number;
  puntos_totales_gastados: number;
  items_mas_vendidos: {
    item_id: number;
    nombre: string;
    categoria: CategoriaProducto;
    cantidad_vendida: number;
    puntos_generados: number;
  }[];
  ventas_por_categoria: {
    categoria: CategoriaProducto;
    cantidad: number;
    puntos_totales: number;
  }[];
  ventas_por_rareza: {
    rareza: RarezaProducto;
    cantidad: number;
    puntos_totales: number;
  }[];
  usuarios_activos_compradores: number;
  promedio_compra: number;
}

/**
 * Filtros para búsqueda de productos (admin)
 */
export interface FiltrosProductosAdmin {
  categoria?: CategoriaProducto;
  rareza?: RarezaProducto;
  activo?: boolean;
  stock_limitado?: boolean;
  busqueda?: string;
}

// ==================== SERVICIO ====================

class AdminTiendaService {
  /**
   * Crea un nuevo producto en la tienda
   */
  async crearProducto(data: CrearProductoRequest): Promise<ProductoTienda> {
    const response = await api.post('/admin/tienda/items', data);
    return response.data;
  }

  /**
   * Obtiene todos los productos (incluye inactivos)
   */
  async listarProductos(filtros?: FiltrosProductosAdmin): Promise<ProductoTienda[]> {
    const params = new URLSearchParams();
    
    if (filtros) {
      if (filtros.categoria && filtros.categoria !== 'todos') {
        params.append('categoria', filtros.categoria);
      }
      if (filtros.rareza) params.append('rareza', filtros.rareza);
      if (filtros.activo !== undefined) params.append('activo', filtros.activo.toString());
      if (filtros.stock_limitado !== undefined) params.append('stock_limitado', filtros.stock_limitado.toString());
      if (filtros.busqueda) params.append('busqueda', filtros.busqueda);
    }

    const response = await api.get(`/admin/tienda/items?${params.toString()}`);
    return response.data;
  }

  /**
   * Obtiene un producto específico por ID
   */
  async obtenerProducto(productoId: number): Promise<ProductoTienda> {
    const response = await api.get(`/admin/tienda/items/${productoId}`);
    return response.data;
  }

  /**
   * Actualiza un producto existente
   */
  async actualizarProducto(
    productoId: number,
    data: ActualizarProductoRequest
  ): Promise<ProductoTienda> {
    const response = await api.put(`/admin/tienda/items/${productoId}`, data);
    return response.data;
  }

  /**
   * Elimina un producto de la tienda
   */
  async eliminarProducto(productoId: number): Promise<void> {
    await api.delete(`/admin/tienda/items/${productoId}`);
  }

  /**
   * Obtiene estadísticas de ventas de la tienda
   */
  async obtenerEstadisticas(): Promise<EstadisticasVentas> {
    const response = await api.get('/admin/tienda/estadisticas');
    return response.data;
  }

  /**
   * Calcula el precio automático basado en rareza
   */
  calcularPrecioAutomatico(rareza: RarezaProducto): number {
    const precios: Record<RarezaProducto, number> = {
      común: 100,
      raro: 300,
      épico: 1000,
      legendario: 3000,
    };
    return precios[rareza] || 100;
  }
}

// Exportar instancia singleton
const adminTiendaService = new AdminTiendaService();
export default adminTiendaService;
