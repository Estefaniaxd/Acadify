import { motion, AnimatePresence } from 'framer-motion';
import { useState, useMemo } from 'react';
import { 
  Plus, 
  Edit, 
  Trash2, 
  ShoppingBag, 
  Tag, 
  Image as ImageIcon,
  DollarSign,
  Package,
  Search,
  Filter,
  Loader,
  AlertCircle,
  X,
  Star
} from 'lucide-react';
import {
  useAdminProductos,
  useCrearProducto,
  useActualizarProducto,
  useEliminarProducto,
  useEstadisticasVentas,
  useCalcularPrecio,
} from '../../hooks/useAdminTienda';
import { 
  ProductoTienda, 
  CategoriaProducto, 
  RarezaProducto,
  obtenerBgRareza,
  formatearPuntos,
} from '../../services/tienda.service';
import { CrearProductoRequest, ActualizarProductoRequest } from '../../services/adminTienda.service';

// ==================== COMPONENTE PRINCIPAL ====================

export default function AdminTiendaPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategoria, setFilterCategoria] = useState<CategoriaProducto | 'todos'>('todos');
  const [filterRareza, setFilterRareza] = useState<RarezaProducto | 'todas'>('todas');
  const [filterActivo, setFilterActivo] = useState<boolean | undefined>(undefined);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedProducto, setSelectedProducto] = useState<ProductoTienda | null>(null);

  // Queries
  const { data: productos = [], isLoading, error } = useAdminProductos();
  const { data: estadisticas } = useEstadisticasVentas();

  // Mutations
  const crearMutation = useCrearProducto();
  const actualizarMutation = useActualizarProducto();
  const eliminarMutation = useEliminarProducto();

  const categorias: { value: CategoriaProducto | 'todos'; label: string }[] = [
    { value: 'todos', label: 'Todas las categorías' },
    { value: 'temas', label: '🎨 Temas' },
    { value: 'ropa', label: '👕 Ropa' },
    { value: 'accesorios', label: '👑 Accesorios' },
    { value: 'efectos', label: '✨ Efectos' },
    { value: 'insignias', label: '🏅 Insignias' },
  ];

  const rarezas: { value: RarezaProducto | 'todas'; label: string; color: string }[] = [
    { value: 'todas', label: 'Todas las rarezas', color: 'bg-gray-500' },
    { value: 'común', label: 'Común', color: 'bg-gray-500' },
    { value: 'raro', label: 'Raro', color: 'bg-blue-500' },
    { value: 'épico', label: 'Épico', color: 'bg-purple-500' },
    { value: 'legendario', label: 'Legendario', color: 'bg-amber-500' },
  ];

  // Productos filtrados
  const filteredProducts = useMemo(() => {
    return productos.filter(p => {
      const matchesSearch = p.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            p.descripcion?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategoria = filterCategoria === 'todos' || p.categoria === filterCategoria;
      const matchesRareza = filterRareza === 'todas' || p.rareza === filterRareza;
      const matchesActivo = filterActivo === undefined || p.activo === filterActivo;
      return matchesSearch && matchesCategoria && matchesRareza && matchesActivo;
    });
  }, [productos, searchTerm, filterCategoria, filterRareza, filterActivo]);

  const handleCreateProduct = () => {
    setSelectedProducto(null);
    setShowCreateModal(true);
  };

  const handleEditProduct = (producto: ProductoTienda) => {
    setSelectedProducto(producto);
    setShowEditModal(true);
  };

  const handleDeleteProduct = (id: number) => {
    if (confirm('¿Estás seguro de eliminar este producto? Esta acción no se puede deshacer.')) {
      eliminarMutation.mutate(id);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <Loader className="w-12 h-12 text-purple-600 dark:text-purple-400 animate-spin mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Cargando productos...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-8">
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 max-w-md w-full shadow-lg border border-red-200 dark:border-red-800">
          <AlertCircle className="w-12 h-12 text-red-600 dark:text-red-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-900 dark:text-white text-center mb-2">
            Error al cargar productos
          </h3>
          <p className="text-gray-600 dark:text-gray-400 text-center">
            {(error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Ha ocurrido un error inesperado'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center">
                  <ShoppingBag className="w-7 h-7 text-white" />
                </div>
                Gestión de Tienda
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                Administra productos, categorías y precios de la tienda de puntos
              </p>
            </div>
            <button
              onClick={handleCreateProduct}
              disabled={crearMutation.isPending}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl hover:shadow-lg transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Plus className="w-5 h-5" />
              Nuevo Producto
            </button>
          </div>
        </motion.div>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-2xl p-6 mb-6 shadow-lg border border-gray-200 dark:border-gray-700"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar productos..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 dark:text-white"
              />
            </div>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <select
                value={filterCategoria}
                onChange={(e) => setFilterCategoria(e.target.value as CategoriaProducto | 'todos')}
                className="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 dark:text-white appearance-none"
              >
                {categorias.map(cat => (
                  <option key={cat.value} value={cat.value}>{cat.label}</option>
                ))}
              </select>
            </div>
            <div className="relative">
              <Star className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <select
                value={filterRareza}
                onChange={(e) => setFilterRareza(e.target.value as RarezaProducto | 'todas')}
                className="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 dark:text-white appearance-none"
              >
                {rarezas.map(rar => (
                  <option key={rar.value} value={rar.value}>{rar.label}</option>
                ))}
              </select>
            </div>
            <div className="relative">
              <Package className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <select
                value={filterActivo === undefined ? 'todos' : filterActivo ? 'activos' : 'inactivos'}
                onChange={(e) => {
                  if (e.target.value === 'todos') setFilterActivo(undefined);
                  else if (e.target.value === 'activos') setFilterActivo(true);
                  else setFilterActivo(false);
                }}
                className="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 dark:text-white appearance-none"
              >
                <option value="todos">Todos los estados</option>
                <option value="activos">Solo activos</option>
                <option value="inactivos">Solo inactivos</option>
              </select>
            </div>
          </div>
        </motion.div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          {[
            { 
              label: 'Total Productos', 
              value: productos.length.toString(), 
              icon: Package, 
              color: 'from-blue-500 to-cyan-600' 
            },
            { 
              label: 'Productos Activos', 
              value: productos.filter(p => p.activo).length.toString(), 
              icon: ShoppingBag, 
              color: 'from-green-500 to-emerald-600' 
            },
            { 
              label: 'Total Ventas', 
              value: estadisticas?.total_ventas?.toString() || '0', 
              icon: DollarSign, 
              color: 'from-purple-500 to-pink-600' 
            },
            { 
              label: 'Puntos Generados', 
              value: formatearPuntos(estadisticas?.puntos_totales_gastados || 0), 
              icon: Tag, 
              color: 'from-amber-500 to-orange-600' 
            }
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{stat.value}</p>
                </div>
                <div className={`w-12 h-12 bg-gradient-to-r ${stat.color} rounded-xl flex items-center justify-center`}>
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Products Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {filteredProducts.map((producto, index) => (
            <motion.div
              key={producto.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white dark:bg-gray-800 rounded-2xl overflow-hidden shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
            >
              {/* Product Image */}
              <div className={`h-48 ${obtenerBgRareza(producto.rareza)} dark:opacity-80 flex items-center justify-center relative`}>
                {producto.imagen_url ? (
                  <img src={producto.imagen_url} alt={producto.nombre} className="w-full h-full object-cover" />
                ) : (
                  <ImageIcon className="w-16 h-16 text-gray-300 dark:text-gray-600" />
                )}
                <div className={`absolute top-3 right-3 px-3 py-1 ${rarezas.find(r => r.value === producto.rareza)?.color} text-white text-xs font-bold rounded-full`}>
                  {producto.rareza.toUpperCase()}
                </div>
                {!producto.activo && (
                  <div className="absolute top-3 left-3 px-3 py-1 bg-red-500 text-white text-xs font-bold rounded-full">
                    Inactivo
                  </div>
                )}
                {!producto.stock_ilimitado && producto.stock !== undefined && (
                  <div className="absolute bottom-3 left-3 px-3 py-1 bg-black/70 text-white text-xs font-bold rounded-full">
                    Stock: {producto.stock}
                  </div>
                )}
              </div>

              {/* Product Info */}
              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                      {producto.nombre}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                      {producto.descripcion || 'Sin descripción'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs font-medium text-purple-600 dark:text-purple-400 bg-purple-100 dark:bg-purple-900/30 px-3 py-1 rounded-full">
                    {categorias.find(c => c.value === producto.categoria)?.label || producto.categoria}
                  </span>
                  <span className="text-xl font-bold text-purple-600 dark:text-purple-400">
                    {formatearPuntos(producto.precio)} pts
                  </span>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEditProduct(producto)}
                    disabled={actualizarMutation.isPending}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-xl hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors disabled:opacity-50"
                  >
                    <Edit className="w-4 h-4" />
                    Editar
                  </button>
                  <button
                    onClick={() => handleDeleteProduct(producto.id)}
                    disabled={eliminarMutation.isPending}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-xl hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors disabled:opacity-50"
                  >
                    <Trash2 className="w-4 h-4" />
                    Eliminar
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Empty State */}
        {filteredProducts.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-white dark:bg-gray-800 rounded-2xl p-12 text-center shadow-lg border border-gray-200 dark:border-gray-700"
          >
            <ShoppingBag className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              No se encontraron productos
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              {searchTerm || filterCategoria !== 'todos' || filterRareza !== 'todas'
                ? 'Intenta ajustar los filtros de búsqueda'
                : 'Comienza agregando tu primer producto a la tienda'
              }
            </p>
            {!searchTerm && filterCategoria === 'todos' && filterRareza === 'todas' && (
              <button
                onClick={handleCreateProduct}
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl hover:shadow-lg transition-all duration-200"
              >
                Crear Primer Producto
              </button>
            )}
          </motion.div>
        )}

        {/* Modals */}
        <AnimatePresence>
          {showCreateModal && (
            <ProductoModal
              mode="create"
              onClose={() => setShowCreateModal(false)}
              onSubmit={(data) => {
                crearMutation.mutate(data as CrearProductoRequest, {
                  onSuccess: () => setShowCreateModal(false),
                });
              }}
              isLoading={crearMutation.isPending}
            />
          )}

          {showEditModal && selectedProducto && (
            <ProductoModal
              mode="edit"
              producto={selectedProducto}
              onClose={() => {
                setShowEditModal(false);
                setSelectedProducto(null);
              }}
              onSubmit={(data) => {
                actualizarMutation.mutate(
                  { productoId: selectedProducto.id, data },
                  {
                    onSuccess: () => {
                      setShowEditModal(false);
                      setSelectedProducto(null);
                    },
                  }
                );
              }}
              isLoading={actualizarMutation.isPending}
            />
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

// ==================== MODAL COMPONENT ====================

interface ProductoModalProps {
  mode: 'create' | 'edit';
  producto?: ProductoTienda;
  onClose: () => void;
  onSubmit: (data: CrearProductoRequest | ActualizarProductoRequest) => void;
  isLoading: boolean;
}

function ProductoModal({ mode, producto, onClose, onSubmit, isLoading }: ProductoModalProps) {
  const { calcular } = useCalcularPrecio();
  const [formData, setFormData] = useState<CrearProductoRequest>({
    nombre: producto?.nombre || '',
    descripcion: producto?.descripcion || '',
    categoria: producto?.categoria || 'ropa',
    rareza: producto?.rareza || 'común',
    precio_puntos: producto?.precio || undefined,
    usar_precio_automatico: false,
    nivel_minimo_requerido: 1,
    stock_limitado: !producto?.stock_ilimitado,
    stock_disponible: producto?.stock || undefined,
    es_consumible: false,
    activo: producto?.activo ?? true,
    imagen_url: producto?.imagen_url || '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const submitData = mode === 'create' ? formData : {
      nombre: formData.nombre,
      descripcion: formData.descripcion,
      precio_puntos: formData.precio_puntos,
      rareza: formData.rareza,
      nivel_minimo_requerido: formData.nivel_minimo_requerido,
      stock_disponible: formData.stock_disponible,
      activo: formData.activo,
      imagen_url: formData.imagen_url,
    };

    onSubmit(submitData);
  };

  const precioSugerido = calcular(formData.rareza);

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="bg-white dark:bg-gray-800 rounded-2xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            {mode === 'create' ? 'Nuevo Producto' : 'Editar Producto'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition-colors"
          >
            <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Nombre */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Nombre del producto *
            </label>
            <input
              type="text"
              required
              value={formData.nombre}
              onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 dark:text-white"
              placeholder="Ej: Cabello Fuego"
            />
          </div>

          {/* Descripción */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Descripción
            </label>
            <textarea
              value={formData.descripcion}
              onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
              rows={3}
              className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 dark:text-white"
              placeholder="Descripción del producto..."
            />
          </div>

          {/* Categoría y Rareza */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Categoría *
              </label>
              <select
                required
                disabled={mode === 'edit'}
                value={formData.categoria}
                onChange={(e) => setFormData({ ...formData, categoria: e.target.value as CategoriaProducto })}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 dark:text-white disabled:opacity-50"
              >
                <option value="temas">🎨 Temas</option>
                <option value="ropa">👕 Ropa</option>
                <option value="accesorios">👑 Accesorios</option>
                <option value="efectos">✨ Efectos</option>
                <option value="insignias">🏅 Insignias</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Rareza *
              </label>
              <select
                required
                value={formData.rareza}
                onChange={(e) => setFormData({ ...formData, rareza: e.target.value as RarezaProducto })}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 dark:text-white"
              >
                <option value="común">Común</option>
                <option value="raro">Raro</option>
                <option value="épico">Épico</option>
                <option value="legendario">Legendario</option>
              </select>
            </div>
          </div>

          {/* Precio */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Precio en puntos *
            </label>
            <div className="relative">
              <input
                type="number"
                required
                min="0"
                value={formData.precio_puntos || ''}
                onChange={(e) => setFormData({ ...formData, precio_puntos: parseInt(e.target.value) || undefined })}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 dark:text-white"
                placeholder={`Sugerido: ${precioSugerido} pts`}
              />
              <div className="absolute right-4 top-1/2 transform -translate-y-1/2 text-sm text-gray-500">
                pts
              </div>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Precio sugerido para {formData.rareza}: <strong>{precioSugerido} puntos</strong>
            </p>
          </div>

          {/* Stock */}
          {mode === 'create' && (
            <div>
              <label className="flex items-center gap-2 mb-2">
                <input
                  type="checkbox"
                  checked={formData.stock_limitado}
                  onChange={(e) => setFormData({ ...formData, stock_limitado: e.target.checked })}
                  className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Stock limitado
                </span>
              </label>
              {formData.stock_limitado && (
                <input
                  type="number"
                  min="0"
                  value={formData.stock_disponible || ''}
                  onChange={(e) => setFormData({ ...formData, stock_disponible: parseInt(e.target.value) || undefined })}
                  className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 dark:text-white"
                  placeholder="Cantidad disponible"
                />
              )}
            </div>
          )}

          {/* URL de imagen */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              URL de imagen
            </label>
            <input
              type="url"
              value={formData.imagen_url}
              onChange={(e) => setFormData({ ...formData, imagen_url: e.target.value })}
              className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 dark:text-white"
              placeholder="https://..."
            />
          </div>

          {/* Estado activo */}
          <div>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.activo}
                onChange={(e) => setFormData({ ...formData, activo: e.target.checked })}
                className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
              />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Producto activo y visible en la tienda
              </span>
            </label>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="flex-1 px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-xl hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl hover:shadow-lg transition-all duration-200 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Guardando...
                </>
              ) : (
                mode === 'create' ? 'Crear Producto' : 'Guardar Cambios'
              )}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
