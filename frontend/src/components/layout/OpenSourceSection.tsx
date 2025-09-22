import React from 'react';
import { motion } from 'framer-motion';
import { SiReact, SiFastapi, SiPostgresql, SiTailwindcss, SiVite, SiGithub, SiPython, SiTypescript } from 'react-icons/si';
import { FiCode, FiGitBranch, FiUsers, FiHeart } from 'react-icons/fi';

const techs = [
  { name: 'React', icon: SiReact, color: 'from-sky-400 to-blue-500' },
  { name: 'FastAPI', icon: SiFastapi, color: 'from-emerald-400 to-green-500' },
  { name: 'PostgreSQL', icon: SiPostgresql, color: 'from-blue-600 to-indigo-700' },
  { name: 'Tailwind CSS', icon: SiTailwindcss, color: 'from-cyan-400 to-teal-500' },
  { name: 'Vite', icon: SiVite, color: 'from-yellow-400 to-orange-500' },
  { name: 'Python', icon: SiPython, color: 'from-yellow-500 to-amber-600' },
  { name: 'TypeScript', icon: SiTypescript, color: 'from-blue-500 to-violet-600' },
  { name: 'GitHub', icon: SiGithub, color: 'from-gray-700 to-gray-900' },
];

export default function OpenSourceSection() {
  return (
    <section className="relative w-full py-24 bg-gradient-to-b from-gray-50 via-white to-gray-100 overflow-hidden">
      {/* Elementos decorativos de fondo */}
      <div className="absolute inset-0">
        <motion.div
          className="absolute top-20 left-20 w-64 h-64 rounded-full bg-gradient-to-br from-violet-200/40 to-purple-300/40 blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 90, 0],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute bottom-20 right-20 w-80 h-80 rounded-full bg-gradient-to-br from-blue-200/40 to-indigo-300/40 blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            rotate: [180, 270, 180],
          }}
          transition={{
            duration: 18,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        
        {/* Código decorativo de fondo */}
        <div className="absolute inset-0 opacity-5">
          <pre className="text-xs text-gray-500 transform rotate-12 mt-20 ml-20">
{`function createEducation() {
  const innovation = useGameification();
  const community = buildOpenSource();
  
  return {
    learning: enhanced,
    fun: guaranteed,
    future: bright
  };
}`}
          </pre>
        </div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8">
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
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-emerald-100 to-teal-100 border border-emerald-200 text-emerald-700 font-medium text-sm mb-6"
          >
            <FiCode className="w-4 h-4" />
            100% Código abierto
          </motion.div>
          
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-black text-gray-900 mb-6">
            Construido por la{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600">
              comunidad
            </span>
          </h2>
          
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Acadify está desarrollado con tecnologías modernas y está completamente abierto. 
            Únete a nuestra comunidad de desarrolladores apasionados por la educación.
          </p>
        </motion.div>

        {/* Grid de tecnologías */}
        <motion.div
          className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-4 gap-6 mb-16"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4, duration: 0.8 }}
        >
          {techs.map((tech, idx) => {
            const Icon = tech.icon;
            return (
              <motion.div
                key={tech.name}
                className="group relative"
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 * idx, duration: 0.6 }}
                whileHover={{ y: -8, scale: 1.05 }}
              >
                {/* Tarjeta de tecnología */}
                <div className="relative p-6 rounded-2xl bg-white/90 backdrop-blur-sm border border-white/50 shadow-lg transition-all duration-300 group-hover:shadow-xl overflow-hidden">
                  {/* Fondo gradiente en hover */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${tech.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />
                  
                  {/* Icono */}
                  <motion.div
                    className="relative z-10 flex flex-col items-center"
                    whileHover={{ scale: 1.1 }}
                    transition={{ type: "spring", stiffness: 300 }}
                  >
                    <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${tech.color} flex items-center justify-center shadow-lg mb-3`}>
                      <Icon className="w-8 h-8 text-white" />
                    </div>
                    <span className="text-sm font-bold text-gray-700 group-hover:text-gray-900 transition-colors duration-300">
                      {tech.name}
                    </span>
                  </motion.div>

                  {/* Efecto de brillo */}
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent opacity-0 group-hover:opacity-100 -skew-x-12"
                    animate={{
                      x: ['-100%', '200%'],
                    }}
                    transition={{
                      duration: 1.5,
                      repeat: Infinity,
                      repeatDelay: 3,
                      ease: "easeInOut"
                    }}
                  />
                </div>
              </motion.div>
            );
          })}
        </motion.div>

        {/* Estadísticas y llamada a la acción */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Lado izquierdo - Estadísticas */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.6, duration: 0.8 }}
            className="space-y-8"
          >
            <h3 className="text-3xl md:text-4xl font-bold text-gray-900 mb-8">
              ¿Por qué elegir open source?
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[
                { 
                  icon: FiUsers, 
                  title: 'Comunidad activa',
                  description: 'Más de 500 contribuidores',
                  color: 'from-blue-500 to-indigo-600'
                },
                { 
                  icon: FiGitBranch, 
                  title: 'Desarrollo transparente',
                  description: 'Todo el código es público',
                  color: 'from-emerald-500 to-teal-600'
                },
                { 
                  icon: FiCode, 
                  title: 'Tecnología moderna',
                  description: 'Stack actualizado y robusto',
                  color: 'from-violet-500 to-purple-600'
                },
                { 
                  icon: FiHeart, 
                  title: 'Impacto social',
                  description: 'Educación accesible para todos',
                  color: 'from-pink-500 to-rose-600'
                }
              ].map((item, idx) => {
                const Icon = item.icon;
                return (
                  <motion.div
                    key={item.title}
                    className="flex items-start gap-4"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.8 + (idx * 0.1), duration: 0.6 }}
                  >
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${item.color} flex items-center justify-center shadow-lg flex-shrink-0`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-900 mb-1">{item.title}</h4>
                      <p className="text-gray-600 text-sm">{item.description}</p>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>

          {/* Lado derecho - Llamada a la acción */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.8, duration: 0.8 }}
            className="text-center lg:text-left"
          >
            <div className="relative p-8 rounded-3xl bg-gradient-to-br from-gray-900 via-violet-900 to-purple-900 text-white overflow-hidden">
              {/* Elementos decorativos */}
              <div className="absolute top-4 right-4 w-20 h-20 rounded-full bg-gradient-to-br from-violet-400/30 to-purple-500/30 blur-xl" />
              <div className="absolute bottom-4 left-4 w-16 h-16 rounded-full bg-gradient-to-br from-pink-400/30 to-rose-500/30 blur-xl" />
              
              <div className="relative z-10">
                <h3 className="text-2xl md:text-3xl font-bold mb-4">
                  ¡Contribuye al proyecto!
                </h3>
                <p className="text-white/90 mb-6 leading-relaxed">
                  Ayuda a mejorar la educación para millones de estudiantes. 
                  Cada línea de código cuenta en nuestra misión.
                </p>
                
                <div className="flex flex-col sm:flex-row gap-4">
                  <motion.a
                    href="https://github.com/Estefaniaxd/Acadify"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-white text-gray-900 font-bold hover:bg-gray-100 transition-colors duration-300"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <SiGithub className="w-5 h-5" />
                    Ver en GitHub
                  </motion.a>
                  
                  <motion.a
                    href="/docs"
                    className="inline-flex items-center gap-2 px-6 py-3 rounded-xl border border-white/30 text-white font-medium hover:bg-white/10 transition-colors duration-300"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <FiCode className="w-5 h-5" />
                    Documentación
                  </motion.a>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
