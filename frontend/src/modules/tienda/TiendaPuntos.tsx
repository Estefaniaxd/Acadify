import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiShoppingBag, FiStar, FiUser, FiImage, FiHeart, FiFilter, FiSearch, FiShoppingCart, FiCheck,
  FiTrendingUp, FiGift, FiZap, FiCamera, FiSmile, FiX
} from 'react-icons/fi';
import { 
  HiOutlineSparkles, HiOutlineColorSwatch, HiOutlineEmojiHappy 
} from 'react-icons/hi';

// Mock data para productos de la tienda
const productos = [
  // Temas visuales
  {
    id: 1,
    nombre: 'Tema Galaxia',
    categoria: 'temas',
    precio: 150,
    imagen: '🌌',
    descripcion: 'Tema oscuro con efectos de galaxia y estrellas',
    popular: true,
    nuevo: false,
    rareza: 'épico'
  },
  {
    id: 2,
    nombre: 'Tema Océano',
    categoria: 'temas',
    precio: 120,
    imagen: '🌊',
    descripcion: 'Tema azul con ondas y efectos acuáticos',
    popular: false,
    nuevo: true,
    rareza: 'raro'
  },
  {
    id: 3,
    nombre: 'Tema Primavera',
    categoria: 'temas',
    precio: 100,
    imagen: '🌸',
    descripcion: 'Tema colorido con flores y naturaleza',
    popular: false,
    nuevo: false,
    rareza: 'común'
  },
  // Ropa para avatares
  {
    id: 4,
    nombre: 'Gorra de Graduación',
    categoria: 'ropa',
    precio: 80,
    imagen: '🎓',
    descripcion: 'Gorra académica elegante',
    popular: true,
    nuevo: false,
    rareza: 'raro'
  },
  {
    id: 5,
    nombre: 'Chaqueta de Cuero',
    categoria: 'ropa',
    precio: 200,
    imagen: '🧥',
    descripcion: 'Chaqueta moderna y estilosa',
    popular: false,
    nuevo: true,
    rareza: 'épico'
  },
  {
    id: 6,
    nombre: 'Lentes de Sol',
    categoria: 'ropa',
    precio: 60,
    imagen: '🕶️',
    descripcion: 'Lentes oscuros geniales',
    popular: true,
    nuevo: false,
    rareza: 'común'
  },
  {
    id: 7,
    nombre: 'Corona Dorada',
    categoria: 'ropa',
    precio: 300,
    imagen: '👑',
    descripcion: 'Corona real para los mejores estudiantes',
    popular: false,
    nuevo: false,
    rareza: 'legendario'
  },
  // Stickers y fondos
  {
    id: 8,
    nombre: 'Pack Emojis Estudio',
    categoria: 'stickers',
    precio: 40,
    imagen: '📚',
    descripcion: 'Colección de emojis educativos',
    popular: true,
    nuevo: false,
    rareza: 'común'
  },
  {
    id: 9,
    nombre: 'Stickers Científicos',
    categoria: 'stickers',
    precio: 50,
    imagen: '🔬',
    descripcion: 'Stickers de laboratorio y ciencia',
    popular: false,
    nuevo: true,
    rareza: 'raro'
  },
  {
    id: 10,
    nombre: 'Fondo Biblioteca',
    categoria: 'fondos',
    precio: 90,
    imagen: '📖',
    descripcion: 'Fondo de biblioteca clásica',
    popular: false,
    nuevo: false,
    rareza: 'raro'
  },
  {
    id: 11,
    nombre: 'Fondo Laboratorio',
    categoria: 'fondos',
    precio: 110,
    imagen: '⚗️',
    descripcion: 'Fondo de laboratorio moderno',
    popular: false,
    nuevo: true,
    rareza: 'épico'
  },
  {
    id: 12,
    nombre: 'Pack Celebración',
    categoria: 'stickers',
    precio: 70,
    imagen: '🎉',
    descripcion: 'Stickers para celebrar logros',
    popular: true,
    nuevo: false,
    rareza: 'raro'
  }
];

const categorias = [
  { id: 'todos', nombre: 'Todos', icono: FiShoppingBag, color: 'from-purple-500 to-pink-500' },
  { id: 'temas', nombre: 'Temas', icono: HiOutlineColorSwatch, color: 'from-blue-500 to-cyan-500' },
  { id: 'ropa', nombre: 'Avatar', icono: FiUser, color: 'from-green-500 to-emerald-500' },
  { id: 'stickers', nombre: 'Stickers', icono: FiSmile, color: 'from-yellow-500 to-orange-500' },
  { id: 'fondos', nombre: 'Fondos', icono: FiImage, color: 'from-indigo-500 to-purple-500' }
];

const rarezas = {
  común: { color: 'text-gray-600 bg-gray-100', borde: 'border-gray-300' },
  raro: { color: 'text-blue-600 bg-blue-100', borde: 'border-blue-300' },
  épico: { color: 'text-purple-600 bg-purple-100', borde: 'border-purple-300' },
  legendario: { color: 'text-yellow-600 bg-yellow-100', borde: 'border-yellow-300' }
};

// Tienda de puntos completa y espectacular
export default function TiendaPuntos() {
  const [categoriaActiva, setCategoriaActiva] = useState('todos');
  const [busqueda, setBusqueda] = useState('');
  const [carrito, setCarrito] = useState<number[]>([]);
  const [puntosUsuario] = useState(500); // Mock puntos del usuario
  const [filtroRareza, setFiltroRareza] = useState<string>('');
  const [comprados, setComprados] = useState<number[]>([]);

  // Filtrar productos
  const productosFiltrados = useMemo(() => {
    return productos.filter(producto => {
      const coincideCategoria = categoriaActiva === 'todos' || producto.categoria === categoriaActiva;
      const coincideBusqueda = producto.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
                              producto.descripcion.toLowerCase().includes(busqueda.toLowerCase());
      const coincideRareza = !filtroRareza || producto.rareza === filtroRareza;
      return coincideCategoria && coincideBusqueda && coincideRareza;
    });
  }, [categoriaActiva, busqueda, filtroRareza]);

  const totalCarrito = carrito.reduce((total, id) => {
    const producto = productos.find(p => p.id === id);
    return total + (producto?.precio || 0);
  }, 0);

  const agregarAlCarrito = (id: number) => {
    if (!carrito.includes(id) && !comprados.includes(id)) {
      setCarrito([...carrito, id]);
    }
  };

  const quitarDelCarrito = (id: number) => {
    setCarrito(carrito.filter(item => item !== id));
  };

  const comprarCarrito = () => {
    if (totalCarrito <= puntosUsuario) {
      setComprados([...comprados, ...carrito]);
      setCarrito([]);
      // Aquí iría la lógica para descontar puntos
    }
  };

  return (
    <div className="bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900">
      {/* Header de la tienda */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="sticky top-0 z-10 bg-white/90 dark:bg-gray-800/90 backdrop-blur-xl border-b border-gray-200 dark:border-gray-700 mt-6"
      >
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            {/* Título y puntos */}
            <div className="flex items-center gap-4">
              <motion.div
                className="w-16 h-16 bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg"
                whileHover={{ scale: 1.05, rotate: 5 }}
              >
                <FiShoppingBag className="w-8 h-8 text-white" />
              </motion.div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                  Tienda Acadify
                </h1>
                <div className="flex items-center gap-2 mt-1">
                  <FiStar className="w-5 h-5 text-yellow-500" />
                  <span className="text-lg font-semibold text-yellow-600 dark:text-yellow-400">
                    {puntosUsuario} puntos
                  </span>
                </div>
              </div>
            </div>

            {/* Carrito */}
            <motion.div
              className="flex items-center gap-4"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="relative">
                <motion.button
                  className="relative p-3 bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => carrito.length > 0 && comprarCarrito()}
                  disabled={totalCarrito > puntosUsuario || carrito.length === 0}
                >
                  <FiShoppingCart className="w-6 h-6" />
                  {carrito.length > 0 && (
                    <span className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                      {carrito.length}
                    </span>
                  )}
                </motion.button>
                {carrito.length > 0 && (
                  <div className="absolute top-full right-0 mt-2 p-3 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 min-w-48">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      Total: {totalCarrito} puntos
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {carrito.length} artículos
                    </p>
                  </div>
                )}
              </div>
            </motion.div>
          </div>

          {/* Búsqueda y filtros */}
          <div className="flex flex-col lg:flex-row gap-4 mt-6">
            {/* Buscador */}
            <div className="relative flex-1">
              <FiSearch className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Buscar productos..."
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                className="w-full pl-12 pr-4 py-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all duration-300"
              />
            </div>

            {/* Filtro por rareza */}
            <select
              value={filtroRareza}
              onChange={(e) => setFiltroRareza(e.target.value)}
              className="px-4 py-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all duration-300"
            >
              <option value="">Todas las rarezas</option>
              <option value="común">Común</option>
              <option value="raro">Raro</option>
              <option value="épico">Épico</option>
              <option value="legendario">Legendario</option>
            </select>
          </div>
        </div>
      </motion.div>

      {/* Categorías */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex flex-wrap gap-3 mb-8"
        >
          {categorias.map((categoria, idx) => {
            const IconoCategoria = categoria.icono;
            const activa = categoriaActiva === categoria.id;
            return (
              <motion.button
                key={categoria.id}
                className={`flex items-center gap-3 px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${
                  activa
                    ? `bg-gradient-to-r ${categoria.color} text-white shadow-lg`
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700'
                }`}
                onClick={() => setCategoriaActiva(categoria.id)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 * idx }}
              >
                <IconoCategoria className="w-5 h-5" />
                {categoria.nombre}
              </motion.button>
            );
          })}
        </motion.div>

        {/* Grid de productos */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <AnimatePresence>
            {productosFiltrados.map((producto, idx) => {
              const enCarrito = carrito.includes(producto.id);
              const yaComprado = comprados.includes(producto.id);
              const puedeComprar = producto.precio <= puntosUsuario;
              const rareza = rarezas[producto.rareza as keyof typeof rarezas];

              return (
                <motion.div
                  key={producto.id}
                  layout
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ delay: 0.05 * idx }}
                  className={`group relative bg-white dark:bg-gray-800 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden border-2 ${rareza.borde}`}
                >
                  {/* Badges */}
                  <div className="absolute top-3 left-3 z-10 flex flex-col gap-2">
                    {producto.popular && (
                      <span className="px-2 py-1 bg-gradient-to-r from-orange-500 to-red-500 text-white text-xs font-bold rounded-lg flex items-center gap-1">
                        <FiTrendingUp className="w-3 h-3" />
                        Popular
                      </span>
                    )}
                    {producto.nuevo && (
                      <span className="px-2 py-1 bg-gradient-to-r from-green-500 to-emerald-500 text-white text-xs font-bold rounded-lg flex items-center gap-1">
                        <HiOutlineSparkles className="w-3 h-3" />
                        Nuevo
                      </span>
                    )}
                    <span className={`px-2 py-1 text-xs font-bold rounded-lg ${rareza.color}`}>
                      {producto.rareza}
                    </span>
                  </div>

                  {/* Imagen del producto */}
                  <div className="relative h-48 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 flex items-center justify-center">
                    <span className="text-6xl">{producto.imagen}</span>
                    <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
                  </div>

                  {/* Contenido */}
                  <div className="p-6">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2 group-hover:text-violet-600 dark:group-hover:text-violet-400 transition-colors duration-300">
                      {producto.nombre}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                      {producto.descripcion}
                    </p>

                    {/* Precio y botón */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1">
                        <FiStar className="w-4 h-4 text-yellow-500" />
                        <span className="text-lg font-bold text-gray-900 dark:text-white">
                          {producto.precio}
                        </span>
                      </div>

                      {yaComprado ? (
                        <div className="flex items-center gap-2 px-4 py-2 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-lg">
                          <FiCheck className="w-4 h-4" />
                          <span className="text-sm font-medium">Comprado</span>
                        </div>
                      ) : (
                        <motion.button
                          className={`px-4 py-2 rounded-lg font-semibold transition-all duration-300 flex items-center gap-2 ${
                            enCarrito
                              ? 'bg-red-500 hover:bg-red-600 text-white'
                              : puedeComprar
                              ? 'bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white shadow-lg'
                              : 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                          }`}
                          onClick={() => enCarrito ? quitarDelCarrito(producto.id) : agregarAlCarrito(producto.id)}
                          disabled={!puedeComprar && !enCarrito}
                          whileHover={puedeComprar || enCarrito ? { scale: 1.05 } : {}}
                          whileTap={puedeComprar || enCarrito ? { scale: 0.95 } : {}}
                        >
                          {enCarrito ? (
                            <>
                              <FiX className="w-4 h-4" />
                              Quitar
                            </>
                          ) : puedeComprar ? (
                            <>
                              <FiShoppingCart className="w-4 h-4" />
                              Agregar
                            </>
                          ) : (
                            'Sin puntos'
                          )}
                        </motion.button>
                      )}
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </motion.div>

        {/* Mensaje cuando no hay productos */}
        {productosFiltrados.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-16"
          >
            <FiSearch className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-600 dark:text-gray-400 mb-2">
              No se encontraron productos
            </h3>
            <p className="text-gray-500 dark:text-gray-500">
              Intenta cambiar los filtros o la búsqueda
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
