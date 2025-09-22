import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FiMail, FiPhone, FiGlobe, FiSend, FiCheckCircle } from 'react-icons/fi';
import { HiOutlineOfficeBuilding } from 'react-icons/hi';

export default function InstitutionRegisterSection() {
  const [form, setForm] = useState({
    nombre: '',
    email: '',
    telefono: '',
    web: '',
    mensaje: '',
  });
  const [enviado, setEnviado] = useState(false);
  const [errores, setErrores] = useState<{ [key: string]: string }>({});

  const validate = () => {
    const newErrors: { [key: string]: string } = {};
    if (!form.nombre.trim()) newErrors.nombre = 'El nombre de la institución es obligatorio.';
    if (!form.email.trim() || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email)) newErrors.email = 'Correo electrónico válido requerido.';
    if (!form.telefono.trim() || !/^\+?\d{7,15}$/.test(form.telefono)) newErrors.telefono = 'Teléfono válido requerido (ej: +573001234567).';
    if (form.web && !/^https?:\/\//.test(form.web)) newErrors.web = 'El sitio web debe iniciar con http:// o https://';
    return newErrors;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setErrores({ ...errores, [e.target.name]: '' });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) {
      setErrores(newErrors);
      return;
    }
    // Aquí iría la lógica real de envío (API, email, etc.)
    setEnviado(true);
    setTimeout(() => setEnviado(false), 4000);
    setForm({ nombre: '', email: '', telefono: '', web: '', mensaje: '' });
    setErrores({});
  };

  return (
    <section className="relative w-full py-24 bg-gradient-to-b from-violet-50 via-white to-gray-50 overflow-hidden">
      {/* Elementos decorativos de fondo */}
      <div className="absolute inset-0">
        <motion.div
          className="absolute top-32 left-20 w-64 h-64 rounded-full bg-gradient-to-br from-violet-200/30 to-purple-300/30 blur-3xl"
          animate={{
            scale: [1, 1.3, 1],
            rotate: [0, 180, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute bottom-32 right-20 w-80 h-80 rounded-full bg-gradient-to-br from-blue-200/30 to-indigo-300/30 blur-3xl"
          animate={{
            scale: [1.3, 1, 1.3],
            rotate: [180, 360, 180],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      </div>

      <div className="relative z-10 max-w-5xl mx-auto px-6 lg:px-8">
        {/* Header de sección */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-violet-100 to-purple-100 border border-violet-200 text-violet-700 font-medium text-sm mb-6"
          >
            <HiOutlineOfficeBuilding className="w-4 h-4" />
            Para instituciones educativas
          </motion.div>
          
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-black text-gray-900 mb-6">
            Transforma tu{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-600 via-purple-600 to-pink-600">
              institución
            </span>
          </h2>
          
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Únete a las instituciones educativas líderes que ya están revolucionando 
            la educación con Acadify. Solicita acceso institucional y descubre el poder 
            de la gamificación educativa.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">
          {/* Lado izquierdo - Beneficios */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="space-y-8"
          >
            <h3 className="text-3xl font-bold text-gray-900 mb-8">
              Beneficios institucionales
            </h3>
            
            {[
              {
                title: 'Dashboard administrativo',
                description: 'Panel completo para gestionar estudiantes, cursos y métricas en tiempo real.',
                color: 'from-blue-500 to-indigo-600'
              },
              {
                title: 'Integración LMS',
                description: 'Conecta Acadify con tu sistema de gestión de aprendizaje existente.',
                color: 'from-emerald-500 to-teal-600'
              },
              {
                title: 'Analíticas avanzadas',
                description: 'Reportes detallados sobre el progreso y engagement de tus estudiantes.',
                color: 'from-violet-500 to-purple-600'
              },
              {
                title: 'Soporte prioritario',
                description: 'Atención especializada y capacitación para tu equipo docente.',
                color: 'from-pink-500 to-rose-600'
              }
            ].map((benefit, idx) => (
              <motion.div
                key={benefit.title}
                className="flex items-start gap-4"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.6 + (idx * 0.1), duration: 0.6 }}
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${benefit.color} flex items-center justify-center shadow-lg flex-shrink-0`}>
                  <FiCheckCircle className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h4 className="font-bold text-gray-900 mb-2">{benefit.title}</h4>
                  <p className="text-gray-600">{benefit.description}</p>
                </div>
              </motion.div>
            ))}
          </motion.div>

          {/* Lado derecho - Formulario */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.6, duration: 0.8 }}
          >
            <div className="relative p-8 rounded-3xl bg-white/80 backdrop-blur-sm border border-white/50 shadow-2xl overflow-hidden">
              {/* Fondo gradiente sutil */}
              <div className="absolute inset-0 bg-gradient-to-br from-violet-50/50 to-purple-50/50" />
              
              <div className="relative z-10">
                <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
                  Solicita acceso institucional
                </h3>
                
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Primera fila - Nombre y Email */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <div className="relative">
                        <HiOutlineOfficeBuilding className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                          type="text"
                          name="nombre"
                          value={form.nombre}
                          onChange={handleChange}
                          required
                          placeholder="Nombre de la institución *"
                          className={`w-full pl-12 pr-4 py-3 rounded-xl border-2 bg-white/90 text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all duration-300 ${errores.nombre ? 'border-red-400' : 'border-gray-200'}`}
                        />
                      </div>
                      {errores.nombre && <span className="text-red-500 text-xs mt-1 block">{errores.nombre}</span>}
                    </div>
                    
                    <div>
                      <div className="relative">
                        <FiMail className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                          type="email"
                          name="email"
                          value={form.email}
                          onChange={handleChange}
                          required
                          placeholder="Correo de contacto *"
                          className={`w-full pl-12 pr-4 py-3 rounded-xl border-2 bg-white/90 text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all duration-300 ${errores.email ? 'border-red-400' : 'border-gray-200'}`}
                        />
                      </div>
                      {errores.email && <span className="text-red-500 text-xs mt-1 block">{errores.email}</span>}
                    </div>
                  </div>

                  {/* Segunda fila - Teléfono y Web */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <div className="relative">
                        <FiPhone className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                          type="tel"
                          name="telefono"
                          value={form.telefono}
                          onChange={handleChange}
                          required
                          placeholder="Teléfono de contacto *"
                          className={`w-full pl-12 pr-4 py-3 rounded-xl border-2 bg-white/90 text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all duration-300 ${errores.telefono ? 'border-red-400' : 'border-gray-200'}`}
                        />
                      </div>
                      {errores.telefono && <span className="text-red-500 text-xs mt-1 block">{errores.telefono}</span>}
                    </div>
                    
                    <div>
                      <div className="relative">
                        <FiGlobe className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                          type="url"
                          name="web"
                          value={form.web}
                          onChange={handleChange}
                          placeholder="Sitio web institucional"
                          className={`w-full pl-12 pr-4 py-3 rounded-xl border-2 bg-white/90 text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all duration-300 ${errores.web ? 'border-red-400' : 'border-gray-200'}`}
                        />
                      </div>
                      {errores.web && <span className="text-red-500 text-xs mt-1 block">{errores.web}</span>}
                    </div>
                  </div>

                  {/* Mensaje */}
                  <div>
                    <textarea
                      name="mensaje"
                      value={form.mensaje}
                      onChange={handleChange}
                      rows={4}
                      placeholder="Cuéntanos sobre tu institución y cómo planeas usar Acadify..."
                      className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 bg-white/90 text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all duration-300 resize-none"
                    />
                  </div>

                  {/* Botón de envío */}
                  <motion.button
                    type="submit"
                    className="w-full flex items-center justify-center gap-3 px-8 py-4 rounded-xl bg-gradient-to-r from-violet-600 to-purple-600 text-white font-bold text-lg shadow-xl transition-all duration-300 hover:shadow-2xl disabled:opacity-70"
                    whileHover={{ scale: enviado ? 1 : 1.02, y: enviado ? 0 : -2 }}
                    whileTap={{ scale: enviado ? 1 : 0.98 }}
                    disabled={enviado}
                  >
                    {enviado ? (
                      <>
                        <FiCheckCircle className="w-5 h-5" />
                        ¡Solicitud enviada!
                      </>
                    ) : (
                      <>
                        <FiSend className="w-5 h-5" />
                        Solicitar acceso institucional
                      </>
                    )}
                  </motion.button>
                </form>

                {enviado && (
                  <motion.div
                    className="mt-6 p-4 rounded-xl bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 text-emerald-700 text-center"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                  >
                    <div className="flex items-center justify-center gap-2 mb-2">
                      <FiCheckCircle className="w-5 h-5" />
                      <span className="font-bold">¡Perfecto!</span>
                    </div>
                    <p className="text-sm">
                      Tu solicitud ha sido enviada. Nuestro equipo se pondrá en contacto contigo 
                      en las próximas 24-48 horas.
                    </p>
                  </motion.div>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
