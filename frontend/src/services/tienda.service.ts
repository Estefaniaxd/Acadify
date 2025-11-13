/**
 * Servicio de Tienda de Puntos
 *
 * @module services/tienda.service
 * @description Servicio para interactuar con la API de la tienda de puntos
 */

import { api } from "../utils/api";

// ==================== INTERFACES ====================

/**
 * Categorías de productos disponibles
 */
export type CategoriaProducto = "temas" | "ropa" | "accesorios" | "efectos" | "insignias" | "todos";

/**
 * Rareza del producto
 */
export type RarezaProducto = "común" | "raro" | "épico" | "legendario";

/**
 * Estado de una compra
 */
export type EstadoCompra = "completada" | "pendiente" | "cancelada" | "reembolsada";

/**
 * Producto de la tienda
 */
export interface ProductoTienda {
  id: number;
  nombre: string;
  descripcion: string;
  categoria: CategoriaProducto;
  precio: number;
  imagen_url?: string;
  icono?: string;
  rareza: RarezaProducto;
  stock?: number;
  stock_ilimitado: boolean;
  popular: boolean;
  nuevo: boolean;
  descuento_porcentaje?: number;
  precio_original?: number;
  activo: boolean;
  fecha_creacion: string;
  fecha_actualizacion: string;
}

/**
 * Compra realizada por el usuario
 */
export interface CompraUsuario {
  id: number;
  usuario_id: number;
  producto_id: number;
  producto?: ProductoTienda;
  puntos_gastados: number;
  cantidad: number;
  estado: EstadoCompra;
  fecha_compra: string;
  fecha_activacion?: string;
  notas?: string;
}

/**
 * Item en el inventario del usuario
 */
export interface ItemInventario {
  id: number;
  usuario_id: number;
  producto_id: number;
  producto: ProductoTienda;
  cantidad: number;
  equipado: boolean;
  fecha_adquisicion: string;
}

/**
 * Respuesta paginada de productos
 */
export interface ProductosPaginados {
  productos: ProductoTienda[];
  total: number;
  pagina: number;
  por_pagina: number;
  total_paginas: number;
}

/**
 * Respuesta de compra
 */
export interface RespuestaCompra {
  compra: CompraUsuario;
  puntos_restantes: number;
  mensaje: string;
}

/**
 * Filtros para búsqueda de productos
 */
export interface FiltrosProductos {
  categoria?: CategoriaProducto;
  rareza?: RarezaProducto;
  precio_min?: number;
  precio_max?: number;
  busqueda?: string;
  popular?: boolean;
  nuevo?: boolean;
  solo_disponibles?: boolean;
  orden_por?: "precio_asc" | "precio_desc" | "nombre" | "popularidad" | "fecha_desc";
  pagina?: number;
  por_pagina?: number;
}

/**
 * Estadísticas de la tienda del usuario
 */
export interface EstadisticasTienda {
  total_gastado: number;
  total_compras: number;
  items_inventario: number;
  items_equipados: number;
  categoria_favorita: CategoriaProducto;
  producto_mas_usado?: ProductoTienda;
}

// ==================== UTILIDADES ====================

/**
 * Obtiene el color asociado a una rareza
 */
export const obtenerColorRareza = (rareza: RarezaProducto): string => {
  const colores: Record<RarezaProducto, string> = {
    común: "text-gray-600 dark:text-gray-400",
    raro: "text-blue-600 dark:text-blue-400",
    épico: "text-purple-600 dark:text-purple-400",
    legendario: "text-yellow-600 dark:text-yellow-400",
  };
  return colores[rareza] || colores.común;
};

/**
 * Obtiene el fondo asociado a una rareza
 */
export const obtenerBgRareza = (rareza: RarezaProducto): string => {
  const fondos: Record<RarezaProducto, string> = {
    común: "bg-gray-100 dark:bg-gray-800",
    raro: "bg-blue-100 dark:bg-blue-900",
    épico: "bg-purple-100 dark:bg-purple-900",
    legendario: "bg-yellow-100 dark:bg-yellow-900",
  };
  return fondos[rareza] || fondos.común;
};

/**
 * Obtiene el gradiente asociado a una rareza
 */
export const obtenerGradienteRareza = (rareza: RarezaProducto): string => {
  const gradientes: Record<RarezaProducto, string> = {
    común: "from-gray-400 to-gray-600",
    raro: "from-blue-400 to-blue-600",
    épico: "from-purple-400 to-purple-600",
    legendario: "from-yellow-400 to-orange-500",
  };
  return gradientes[rareza] || gradientes.común;
};

/**
 * Calcula el precio con descuento
 */
export const calcularPrecioFinal = (producto: ProductoTienda): number => {
  if (producto.descuento_porcentaje && producto.descuento_porcentaje > 0) {
    return Math.round(producto.precio * (1 - producto.descuento_porcentaje / 100));
  }
  return producto.precio;
};

/**
 * Formatea puntos con separadores de miles
 */
export const formatearPuntos = (puntos: number): string => {
  return new Intl.NumberFormat("es-ES").format(puntos);
};

// ==================== SERVICIOS ====================

class TiendaService {
  /**
   * Obtiene todos los productos de la tienda con filtros opcionales
   */
  async obtenerProductos(filtros?: FiltrosProductos): Promise<ProductosPaginados> {
    const params = new URLSearchParams();

    if (filtros) {
      if (filtros.categoria && filtros.categoria !== "todos") {
        params.append("categoria", filtros.categoria);
      }
      if (filtros.rareza) params.append("rareza", filtros.rareza);
      if (filtros.precio_min !== undefined)
        params.append("precio_min", filtros.precio_min.toString());
      if (filtros.precio_max !== undefined)
        params.append("precio_max", filtros.precio_max.toString());
      if (filtros.busqueda) params.append("busqueda", filtros.busqueda);
      if (filtros.popular !== undefined) params.append("popular", filtros.popular.toString());
      if (filtros.nuevo !== undefined) params.append("nuevo", filtros.nuevo.toString());
      if (filtros.solo_disponibles !== undefined)
        params.append("solo_disponibles", filtros.solo_disponibles.toString());
      if (filtros.orden_por) params.append("orden_por", filtros.orden_por);
      if (filtros.pagina) params.append("pagina", filtros.pagina.toString());
      if (filtros.por_pagina) params.append("por_pagina", filtros.por_pagina.toString());
    }

    const response = await api.get(`/tienda/productos?${params.toString()}`);
    return response.data;
  }

  /**
   * Obtiene un producto específico por ID
   */
  async obtenerProducto(productoId: number): Promise<ProductoTienda> {
    const response = await api.get(`/tienda/productos/${productoId}`);
    return response.data;
  }

  /**
   * Obtiene productos destacados (populares y nuevos)
   */
  async obtenerProductosDestacados(): Promise<{
    populares: ProductoTienda[];
    nuevos: ProductoTienda[];
    descuentos: ProductoTienda[];
  }> {
    const response = await api.get("/tienda/productos/destacados");
    return response.data;
  }

  /**
   * Compra un producto de la tienda
   */
  async comprarProducto(productoId: number, cantidad: number = 1): Promise<RespuestaCompra> {
    const response = await api.post("/tienda/comprar", {
      producto_id: productoId,
      cantidad,
    });
    return response.data;
  }

  /**
   * Obtiene el historial de compras del usuario
   */
  async obtenerHistorialCompras(
    pagina: number = 1,
    porPagina: number = 20
  ): Promise<{
    compras: CompraUsuario[];
    total: number;
    pagina: number;
    por_pagina: number;
    total_paginas: number;
  }> {
    const response = await api.get("/tienda/compras", {
      params: { pagina, por_pagina: porPagina },
    });
    return response.data;
  }

  /**
   * Obtiene una compra específica
   */
  async obtenerCompra(compraId: number): Promise<CompraUsuario> {
    const response = await api.get(`/tienda/compras/${compraId}`);
    return response.data;
  }

  /**
   * Obtiene el inventario del usuario
   */
  async obtenerInventario(): Promise<ItemInventario[]> {
    const response = await api.get("/tienda/inventario");
    return response.data;
  }

  /**
   * Obtiene un item específico del inventario
   */
  async obtenerItemInventario(itemId: number): Promise<ItemInventario> {
    const response = await api.get(`/tienda/inventario/${itemId}`);
    return response.data;
  }

  /**
   * Equipa un item del inventario
   */
  async equiparItem(itemId: number): Promise<{
    mensaje: string;
    item: ItemInventario;
  }> {
    const response = await api.post(`/tienda/inventario/${itemId}/equipar`);
    return response.data;
  }

  /**
   * Desequipa un item del inventario
   */
  async desequiparItem(itemId: number): Promise<{
    mensaje: string;
    item: ItemInventario;
  }> {
    const response = await api.post(`/tienda/inventario/${itemId}/desequipar`);
    return response.data;
  }

  /**
   * Verifica si el usuario puede comprar un producto
   */
  async verificarDisponibilidad(
    productoId: number,
    cantidad: number = 1
  ): Promise<{
    puede_comprar: boolean;
    razon?: string;
    puntos_faltantes?: number;
  }> {
    const response = await api.get(`/tienda/productos/${productoId}/disponibilidad`, {
      params: { cantidad },
    });
    return response.data;
  }

  /**
   * Obtiene las estadísticas de tienda del usuario
   */
  async obtenerEstadisticas(): Promise<EstadisticasTienda> {
    const response = await api.get("/tienda/estadisticas");
    return response.data;
  }

  /**
   * Obtiene categorías disponibles con conteo de productos
   */
  async obtenerCategorias(): Promise<
    {
      categoria: CategoriaProducto;
      nombre: string;
      total_productos: number;
    }[]
  > {
    const response = await api.get("/tienda/categorias");
    return response.data;
  }
}

// Exportar instancia singleton
const tiendaService = new TiendaService();
export default tiendaService;
