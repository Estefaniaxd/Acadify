import React, { useState } from 'react';
import { motion } from 'framer-motion';

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
    <section className="w-full py-20 bg-gradient-to-b from-white via-[#f3f0ff] to-[#f7f7fb] dark:from-[#18181b] dark:via-[#18181b] dark:to-black">
      <div className="max-w-2xl mx-auto px-4 flex flex-col items-center text-center">
        <motion.h2
          className="text-3xl md:text-4xl font-extrabold mb-4 text-primary dark:text-purple-200"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
        >
          ¿Eres una institución educativa?
        </motion.h2>
        <motion.p
          className="text-lg text-gray-700 dark:text-gray-300 mb-8"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2, duration: 0.7 }}
        >
          Solicita acceso institucional y nos pondremos en contacto para ayudarte a transformar la educación en tu comunidad.
        </motion.p>
        <motion.form
          onSubmit={handleSubmit}
          className="w-full bg-white/90 dark:bg-[#18181b] rounded-3xl shadow-2xl p-10 border border-gray-100 dark:border-gray-800 flex flex-col gap-6 backdrop-blur-xl"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3, duration: 0.7 }}
        >
          <div className="flex flex-col md:flex-row gap-6">
            <div className="flex-1">
              <input
                type="text"
                name="nombre"
                value={form.nombre}
                onChange={handleChange}
                required
                placeholder="Nombre de la institución *"
                className={`px-5 py-3 rounded-lg border-2 focus:ring-2 text-lg w-full bg-white dark:bg-[#23232b] text-gray-800 dark:text-gray-100 border-primary/30 dark:border-purple-400/30 focus:outline-none focus:ring-primary/40 ${errores.nombre ? 'border-red-400' : ''}`}
              />
              {errores.nombre && <span className="text-red-500 text-xs mt-1 block text-left">{errores.nombre}</span>}
            </div>
            <div className="flex-1">
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                required
                placeholder="Correo de contacto *"
                className={`px-5 py-3 rounded-lg border-2 focus:ring-2 text-lg w-full bg-white dark:bg-[#23232b] text-gray-800 dark:text-gray-100 border-primary/30 dark:border-purple-400/30 focus:outline-none focus:ring-primary/40 ${errores.email ? 'border-red-400' : ''}`}
              />
              {errores.email && <span className="text-red-500 text-xs mt-1 block text-left">{errores.email}</span>}
            </div>
          </div>
          <div className="flex flex-col md:flex-row gap-6">
            <div className="flex-1">
              <input
                type="tel"
                name="telefono"
                value={form.telefono}
                onChange={handleChange}
                required
                placeholder="Teléfono de contacto *"
                className={`px-5 py-3 rounded-lg border-2 focus:ring-2 text-lg w-full bg-white dark:bg-[#23232b] text-gray-800 dark:text-gray-100 border-primary/30 dark:border-purple-400/30 focus:outline-none focus:ring-primary/40 ${errores.telefono ? 'border-red-400' : ''}`}
              />
              {errores.telefono && <span className="text-red-500 text-xs mt-1 block text-left">{errores.telefono}</span>}
            </div>
            <div className="flex-1">
              <input
                type="url"
                name="web"
                value={form.web}
                onChange={handleChange}
                placeholder="Sitio web institucional"
                className={`px-5 py-3 rounded-lg border-2 focus:ring-2 text-lg w-full bg-white dark:bg-[#23232b] text-gray-800 dark:text-gray-100 border-primary/30 dark:border-purple-400/30 focus:outline-none focus:ring-primary/40 ${errores.web ? 'border-red-400' : ''}`}
              />
              {errores.web && <span className="text-red-500 text-xs mt-1 block text-left">{errores.web}</span>}
            </div>
          </div>
          <textarea
            name="mensaje"
            value={form.mensaje}
            onChange={handleChange}
            rows={4}
            placeholder="Mensaje adicional (opcional)"
            className="px-5 py-3 rounded-lg border-2 focus:ring-2 text-lg w-full bg-white dark:bg-[#23232b] text-gray-800 dark:text-gray-100 border-primary/30 dark:border-purple-400/30 focus:outline-none focus:ring-primary/40"
          />
          <motion.button
            type="submit"
            className="mt-2 px-10 py-4 rounded-2xl bg-gradient-to-r from-primary to-purple-600 text-white font-extrabold text-xl shadow-xl hover:scale-105 transition-transform drop-shadow-xl border-2 border-primary/30 dark:border-purple-400/30"
            whileTap={{ scale: 0.97 }}
            disabled={enviado}
          >
            {enviado ? '¡Solicitud enviada!' : 'Solicitar acceso institucional'}
          </motion.button>
        </motion.form>
        {enviado && (
          <motion.div
            className="mt-6 text-green-600 dark:text-green-400 font-semibold text-lg bg-green-50 dark:bg-green-900/30 px-6 py-3 rounded-xl shadow"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            ¡Gracias! Tu solicitud ha sido enviada al equipo de Acadify.
          </motion.div>
        )}
      </div>
    </section>
  );
}
