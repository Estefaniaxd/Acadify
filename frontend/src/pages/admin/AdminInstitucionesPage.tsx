import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Building2, Plus, Search, Edit, Trash2, Users, BookOpen, MapPin, Mail, Phone, Shield, Loader, AlertCircle, X, Check, Send } from "lucide-react";
import { useInstituciones, useCrearInstitucion, useActualizarInstitucion, useEliminarInstitucion, useInvitarCoordinador } from "../../hooks/useInstituciones";
import type { Institucion, InstitucionCreate, InstitucionUpdate } from "../../services/instituciones.service";

export default function AdminInstitucionesPage(): JSX.Element {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTipo, setSelectedTipo] = useState<string>("todas");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [selectedInstitucion, setSelectedInstitucion] = useState<Institucion | null>(null);

  const { data: instituciones = [], isLoading, error } = useInstituciones();
  const crearMutation = useCrearInstitucion();
  const actualizarMutation = useActualizarInstitucion();
  const eliminarMutation = useEliminarInstitucion();
  const invitarMutation = useInvitarCoordinador();

  const filteredInstituciones = instituciones.filter((inst) => {
    const matchSearch =
      inst.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inst.codigo?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchTipo = selectedTipo === "todas" || inst.tipo_institucion === selectedTipo;
    return matchSearch && matchTipo;
  });

  const getTipoBadgeColor = (tipo: string) => {
    const colors = {
      universidad: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
      colegio: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300",
      instituto: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300",
      academia: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300",
      otro: "bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300",
    };
    return colors[tipo as keyof typeof colors] || colors.universidad;
  };

  const getEstadoBadgeColor = (estado: string) => {
    const colors = {
      activa: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300",
      inactiva: "bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300",
      pendiente: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300",
      suspendida: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300",
    };
    return colors[estado as keyof typeof colors] || colors.pendiente;
  };

  const handleEliminar = async (institucion: Institucion) => {
    if (!confirm(`¿Eliminar "${institucion.nombre}"? Esta acción no se puede deshacer.`)) return;
    await eliminarMutation.mutateAsync(institucion.institucion_id);
  };

  const handleInvitarCoordinador = (institucion: Institucion) => {
    setSelectedInstitucion(institucion);
    setShowInviteModal(true);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader className="w-8 h-8 animate-spin text-blue-600 mr-3" />
        <span className="text-gray-600 dark:text-gray-400">Cargando instituciones...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6 max-w-md">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-6 h-6 text-red-600" />
            <div>
              <h3 className="font-bold text-red-900 dark:text-red-100">Error al cargar instituciones</h3>
              <p className="text-sm text-red-700 dark:text-red-300 mt-1">
                {(error as Error).message || "Intenta nuevamente más tarde"}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4"
        >
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
              <Building2 className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              Gestión de Instituciones
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Administra todas las instituciones educativas del sistema
            </p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all"
          >
            <Plus className="w-5 h-5" />
            Nueva Institución
          </motion.button>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
        >
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar por nombre o código..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
              />
            </div>

            <select
              value={selectedTipo}
              onChange={(e) => setSelectedTipo(e.target.value)}
              className="px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
            >
              <option value="todas">Todos los tipos</option>
              <option value="universidad">Universidad</option>
              <option value="colegio">Colegio</option>
              <option value="instituto">Instituto</option>
              <option value="academia">Academia</option>
              <option value="otro">Otro</option>
            </select>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
            <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {instituciones.length}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Total</div>
            </div>
            <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                {instituciones.filter((i) => i.estado === "activa").length}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Activas</div>
            </div>
            <div className="text-center p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
              <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                {instituciones.reduce((sum, i) => sum + (i.total_usuarios || 0), 0)}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Usuarios</div>
            </div>
            <div className="text-center p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
              <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                {instituciones.reduce((sum, i) => sum + (i.total_cursos || 0), 0)}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Cursos</div>
            </div>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AnimatePresence>
            {filteredInstituciones.map((inst, index) => (
              <motion.div
                key={inst.institucion_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ delay: index * 0.05 }}
                className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-all"
              >
                <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-4 text-white">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                        <Building2 className="w-6 h-6" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold">{inst.nombre}</h3>
                        <p className="text-sm text-blue-100">
                          {inst.sigla ? `${inst.sigla} • ` : ""}Código: {inst.codigo}
                        </p>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getEstadoBadgeColor(inst.estado)}`}>
                      {inst.estado}
                    </span>
                  </div>
                </div>

                <div className="p-6 space-y-4">
                  <div className="flex items-center gap-2">
                    <Shield className="w-4 h-4 text-gray-400" />
                    <span className={`px-2 py-1 rounded-lg text-xs font-medium ${getTipoBadgeColor(inst.tipo_institucion)}`}>
                      {inst.tipo_institucion.replace(/_/g, ' ').charAt(0).toUpperCase() + inst.tipo_institucion.replace(/_/g, ' ').slice(1)}
                    </span>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <Mail className="w-4 h-4 flex-shrink-0" />
                      <span className="truncate">{inst.correo_institucional}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <Phone className="w-4 h-4 flex-shrink-0" />
                      {inst.telefono}
                    </div>
                    {(inst.direccion || inst.ciudad || inst.pais) && (
                      <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                        <MapPin className="w-4 h-4 flex-shrink-0" />
                        <span className="truncate">
                          {[inst.direccion, inst.ciudad, inst.pais].filter(Boolean).join(", ")}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <Users className="w-4 h-4" />
                      <span className="font-medium">{inst.total_usuarios || 0}</span> usuarios
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <BookOpen className="w-4 h-4" />
                      <span className="font-medium">{inst.total_cursos || 0}</span> cursos
                    </div>
                  </div>

                  <div className="flex items-center gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <button
                      onClick={() => handleInvitarCoordinador(inst)}
                      disabled={invitarMutation.isPending}
                      className="flex-1 px-4 py-2 bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 rounded-lg font-medium hover:bg-green-100 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                      <Send className="w-4 h-4" />
                      Invitar
                    </button>
                    <button
                      onClick={() => {
                        setSelectedInstitucion(inst);
                        setShowEditModal(true);
                      }}
                      className="px-4 py-2 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 transition-colors"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleEliminar(inst)}
                      disabled={eliminarMutation.isPending}
                      className="px-4 py-2 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-100 transition-colors disabled:opacity-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {filteredInstituciones.length === 0 && (
          <div className="text-center py-12">
            <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">No se encontraron instituciones</h3>
            <p className="text-gray-600 dark:text-gray-400">
              {instituciones.length === 0 ? "Crea tu primera institución" : "Intenta otros filtros"}
            </p>
          </div>
        )}
      </div>

      <AnimatePresence>
        {showCreateModal && (
          <InstitucionModal
            title="Nueva Institución"
            onClose={() => setShowCreateModal(false)}
            onSubmit={(data) => {
              crearMutation.mutate(data as InstitucionCreate, {
                onSuccess: () => setShowCreateModal(false),
              });
            }}
            isLoading={crearMutation.isPending}
          />
        )}

        {showEditModal && selectedInstitucion && (
          <InstitucionModal
            title="Editar Institución"
            initialData={selectedInstitucion}
            onClose={() => {
              setShowEditModal(false);
              setSelectedInstitucion(null);
            }}
            onSubmit={(data) => {
              actualizarMutation.mutate(
                { id: selectedInstitucion.institucion_id, data },
                {
                  onSuccess: () => {
                    setShowEditModal(false);
                    setSelectedInstitucion(null);
                  },
                }
              );
            }}
            isLoading={actualizarMutation.isPending}
          />
        )}

        {showInviteModal && selectedInstitucion && (
          <InvitarCoordinadorModal
            institucion={selectedInstitucion}
            onClose={() => {
              setShowInviteModal(false);
              setSelectedInstitucion(null);
            }}
            onSubmit={(email) => {
              invitarMutation.mutate(
                { institucionId: selectedInstitucion.institucion_id, data: { email_destino: email } },
                {
                  onSuccess: () => {
                    setShowInviteModal(false);
                    setSelectedInstitucion(null);
                  },
                }
              );
            }}
            isLoading={invitarMutation.isPending}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

function InstitucionModal({
  title,
  initialData,
  onClose,
  onSubmit,
  isLoading,
}: {
  title: string;
  initialData?: Institucion;
  onClose: () => void;
  onSubmit: (data: InstitucionCreate | InstitucionUpdate) => void;
  isLoading: boolean;
}) {
  const [formData, setFormData] = useState({
    nombre: initialData?.nombre || "",
    sigla: initialData?.sigla || "",
    lema: initialData?.lema || "",
    tipo_institucion: initialData?.tipo_institucion || "universidad",
    usa_programas: initialData?.usa_programas || false,
    nivel_educativo: (initialData?.nivel_educativo || "superior") as "basica" | "media" | "tecnica" | "tecnologica" | "superior",
    sector: (initialData?.sector || "publico") as "publico" | "privado",
    direccion: initialData?.direccion || "",
    ciudad: initialData?.ciudad || "",
    pais: initialData?.pais || "Colombia",
    correo_institucional: initialData?.correo_institucional || "",
    telefono: initialData?.telefono || "",
    nit: initialData?.nit || "",
    estado: initialData?.estado || "activa",
  });

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
      >
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold flex items-center gap-3">
            <Building2 className="w-6 h-6" />
            {title}
          </h2>
          <button onClick={onClose} className="p-2 hover:bg-white/20 rounded-lg transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            // Para crear, solo enviamos los campos necesarios para InstitucionCreate
            if (!initialData) {
              const createData = {
                nombre: formData.nombre,
                sigla: formData.sigla || undefined,
                lema: formData.lema || undefined,
                tipo_institucion: formData.tipo_institucion,
                usa_programas: formData.usa_programas,
                nivel_educativo: formData.nivel_educativo,
                sector: formData.sector,
                direccion: formData.direccion || undefined,
                ciudad: formData.ciudad || undefined,
                pais: formData.pais,
                correo_institucional: formData.correo_institucional,
                telefono: formData.telefono,
                nit: formData.nit || undefined,
              };
              onSubmit(createData as any);
            } else {
              onSubmit(formData as any);
            }
          }}
          className="p-6 space-y-6"
        >
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Nombre *</label>
              <input
                type="text"
                required
                value={formData.nombre}
                onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
                placeholder="Universidad Nacional"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Sigla</label>
              <input
                type="text"
                value={formData.sigla}
                onChange={(e) => setFormData({ ...formData, sigla: e.target.value })}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
                placeholder="UNAL"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Tipo *</label>
              <select
                required
                value={formData.tipo_institucion}
                onChange={(e) => setFormData({ ...formData, tipo_institucion: e.target.value as any })}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
              >
                <option value="universidad">Universidad</option>
                <option value="colegio">Colegio</option>
                <option value="instituto">Instituto</option>
                <option value="escuela">Escuela</option>
                <option value="academia">Academia</option>
                <option value="politecnico">Politécnico</option>
                <option value="centro_de_formacion">Centro de Formación</option>
                <option value="otro">Otro</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Email Institucional *</label>
              <input
                type="email"
                required
                value={formData.correo_institucional}
                onChange={(e) => setFormData({ ...formData, correo_institucional: e.target.value })}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
                placeholder="correo@institucion.edu"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Teléfono *</label>
              <input
                type="tel"
                required
                value={formData.telefono}
                onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
                placeholder="+57 1 234567"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Nivel Educativo *</label>
              <select
                required
                value={formData.nivel_educativo}
                onChange={(e) => setFormData({ ...formData, nivel_educativo: e.target.value as any })}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
              >
                <option value="basica">Básica</option>
                <option value="media">Media</option>
                <option value="tecnica">Técnica</option>
                <option value="tecnologica">Tecnológica</option>
                <option value="superior">Superior</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Sector *</label>
              <select
                required
                value={formData.sector}
                onChange={(e) => setFormData({ ...formData, sector: e.target.value as "publico" | "privado" })}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
              >
                <option value="publico">Público</option>
                <option value="privado">Privado</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">País *</label>
              <input
                type="text"
                required
                value={formData.pais}
                onChange={(e) => setFormData({ ...formData, pais: e.target.value })}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
                placeholder="Colombia"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Ciudad</label>
              <input
                type="text"
                value={formData.ciudad}
                onChange={(e) => setFormData({ ...formData, ciudad: e.target.value })}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
                placeholder="Bogotá"
              />
            </div>

            <div className="col-span-2">
              <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Dirección</label>
              <input
                type="text"
                value={formData.direccion}
                onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
                placeholder="Calle 123 # 45-67"
              />
            </div>

            <div className="col-span-2">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                <input
                  type="checkbox"
                  checked={formData.usa_programas}
                  onChange={(e) => setFormData({ ...formData, usa_programas: e.target.checked })}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                ¿Usa programas académicos?
              </label>
            </div>

            {initialData && (
              <div className="col-span-2">
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Estado</label>
                <select
                  value={formData.estado}
                  onChange={(e) => setFormData({ ...formData, estado: e.target.value as "activa" | "inactiva" | "pendiente" | "suspendida" })}
                  className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
                >
                  <option value="activa">Activa</option>
                  <option value="inactiva">Inactiva</option>
                  <option value="pendiente">Pendiente</option>
                  <option value="suspendida">Suspendida</option>
                </select>
              </div>
            )}
          </div>

          <div className="flex gap-4 pt-6 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="flex-1 px-6 py-3 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl font-medium hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Guardando...
                </>
              ) : (
                <>
                  <Check className="w-5 h-5" />
                  {initialData ? "Guardar" : "Crear"}
                </>
              )}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}

function InvitarCoordinadorModal({
  institucion,
  onClose,
  onSubmit,
  isLoading,
}: {
  institucion: Institucion;
  onClose: () => void;
  onSubmit: (email: string) => void;
  isLoading: boolean;
}) {
  const [email, setEmail] = useState("");

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full"
      >
        <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-6 rounded-t-2xl">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-xl font-bold flex items-center gap-2 mb-2">
                <Send className="w-5 h-5" />
                Invitar Coordinador
              </h2>
              <p className="text-sm text-green-100">
                Para: <strong>{institucion.nombre}</strong>
              </p>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-white/20 rounded-lg transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (email) onSubmit(email);
          }}
          className="p-6 space-y-4"
        >
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
              Email del coordinador *
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 dark:text-white"
              placeholder="coordinador@correo.com"
            />
          </div>

          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <p className="text-sm text-blue-900 dark:text-blue-100">
              💡 Se enviará un correo con un código de invitación. El coordinador debe registrarse con este código.
            </p>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="flex-1 px-6 py-3 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-xl font-medium hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Enviando...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Enviar Invitación
                </>
              )}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
