import React from 'react';
import { motion } from 'framer-motion';
import { Code, Component, Database, Github, GitBranch, Heart, Palette, Terminal, Users, Zap } from 'lucide-react';

const techs = [
  { name: 'React', icon: Component, color: 'from-sky-400 to-blue-500' },
  { name: 'FastAPI', icon: Zap, color: 'from-emerald-400 to-green-500' },
  { name: 'PostgreSQL', icon: Database, color: 'from-blue-600 to-indigo-700' },
  { name: 'Tailwind CSS', icon: Palette, color: 'from-cyan-400 to-teal-500' },
  { name: 'Vite', icon: Zap, color: 'from-yellow-400 to-orange-500' },
  { name: 'Python', icon: Terminal, color: 'from-yellow-500 to-amber-600' },
  { name: 'TypeScript', icon: Code, color: 'from-blue-500 to-violet-600' },
];

export default function OpenSourceSection() {
  return (
    <section className="relative w-full py-24 bg-gradient-to-b from-neutral-50 via-white to-neutral-100 dark:bg-gradient-to-b dark:from-neutral-950 dark:via-emerald-950/20 dark:to-neutral-950 overflow-hidden">
      {/* Fondos decorativos animados mejorados */}
      <motion.div
        className="absolute top-20 -left-20 w-96 h-96 rounded-full bg-gradient-to-br from-emerald-400/30 to-teal-500/30 dark:from-emerald-600/20 dark:to-teal-700/20 blur-3xl"
        animate={{ 
          scale: [1, 1.3, 1],
          x: [0, 50, 0],
          y: [0, 30, 0],
        }}
        transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="absolute bottom-20 -right-20 w-[500px] h-[500px] rounded-full bg-gradient-to-br from-cyan-400/30 to-blue-500/30 dark:from-cyan-600/20 dark:to-blue-700/20 blur-3xl"
        animate={{ 
          scale: [1.2, 1, 1.2],
          x: [0, -40, 0],
          y: [0, -50, 0],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-gradient-to-br from-violet-400/20 to-purple-500/20 dark:from-violet-600/15 dark:to-purple-700/15 blur-3xl"
        animate={{ 
          scale: [1, 1.15, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{ duration: 15, repeat: Infinity, ease: 'easeInOut' }}
      />
      {/* Código decorativo de fondo */}
      <div className="absolute inset-0 opacity-5 pointer-events-none select-none">
        <pre className="text-xs text-gray-500 dark:text-gray-400 transform rotate-12 mt-20 ml-20">
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
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-emerald-100 via-teal-100 to-cyan-100 dark:from-emerald-950/80 dark:via-teal-950/80 dark:to-cyan-950/80 border-2 border-emerald-300/50 dark:border-emerald-700/50 text-emerald-700 dark:text-emerald-300 font-semibold text-sm mb-6 shadow-lg shadow-emerald-500/20"
          >
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <Code className="w-4 h-4" />
            </motion.div>
            100% Código abierto
          </motion.div>
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-black text-neutral-900 dark:text-white mb-6 leading-tight">
            Construido con{' '}
            <span className="bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 dark:from-emerald-400 dark:via-teal-400 dark:to-cyan-400 bg-clip-text text-transparent drop-shadow-lg">
              tecnología moderna
            </span>
            <br />
            por la{' '}
            <span className="bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600 dark:from-violet-400 dark:via-purple-400 dark:to-fuchsia-400 bg-clip-text text-transparent drop-shadow-lg">
              comunidad
            </span>
          </h2>
          <p className="text-lg md:text-xl text-neutral-600 dark:text-neutral-300 max-w-3xl mx-auto leading-relaxed">
            Acadify está construido con las{' '}
            <span className="font-bold text-emerald-600 dark:text-emerald-400">mejores tecnologías</span>{' '}
            y es completamente{' '}
            <span className="font-bold text-teal-600 dark:text-teal-400">open source</span>.
            Únete a nuestra comunidad de desarrolladores apasionados por la educación.
          </p>
        </motion.div>

        {/* Grid de tecnologías mejorado */}
        <motion.div
          className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6 mb-16"
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
                className="group"
                initial={{ opacity: 0, scale: 0.8, y: 20 }}
                whileInView={{ opacity: 1, scale: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.05 * idx, duration: 0.5, type: "spring" }}
                whileHover={{ y: -8, scale: 1.05 }}
              >
                <div className="relative flex flex-col items-center justify-center gap-4 p-6 rounded-2xl bg-white/90 dark:bg-neutral-900/90 border-2 border-neutral-200/50 dark:border-neutral-800/50 shadow-lg backdrop-blur-md overflow-hidden transition-all duration-300 hover:shadow-2xl hover:border-emerald-400 dark:hover:border-emerald-500">
                  {/* Gradiente de fondo animado */}
                  <motion.div
                    className={`absolute inset-0 bg-gradient-to-br ${tech.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}
                  />
                  
                  {/* Brillo superior */}
                  <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/50 dark:via-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  
                  {/* Icono con contenedor mejorado */}
                  <motion.div 
                    className={`relative w-20 h-20 flex items-center justify-center rounded-2xl bg-gradient-to-br ${tech.color} shadow-xl group-hover:shadow-2xl transition-shadow duration-300`}
                    whileHover={{ rotate: [0, -5, 5, -5, 0], scale: 1.1 }}
                    transition={{ duration: 0.5 }}
                  >
                    <Icon className="w-10 h-10 text-white drop-shadow-2xl" />
                    {/* Efecto de brillo rotativo */}
                    <motion.div
                      className="absolute inset-0 rounded-2xl bg-gradient-to-tr from-white/0 via-white/30 to-white/0"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                    />
                  </motion.div>
                  
                  {/* Nombre con mejor tipografía */}
                  <div className="relative z-10 text-center">
                    <span className="text-base font-bold text-neutral-900 dark:text-white tracking-tight block group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors duration-300">
                      {tech.name}
                    </span>
                  </div>
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
            <h3 className="text-3xl md:text-4xl font-black text-neutral-900 dark:text-white mb-8 leading-tight">
              ¿Por qué{' '}
              <span className="bg-gradient-to-r from-emerald-600 to-teal-600 dark:from-emerald-400 dark:to-teal-400 bg-clip-text text-transparent">
                open source
              </span>
              ?
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[
                { icon: Users, title: 'Comunidad activa', description: 'Más de 500 contribuidores globales', color: 'from-blue-500 to-indigo-600' },
                { icon: GitBranch, title: 'Desarrollo transparente', description: 'Todo el código es 100% público', color: 'from-emerald-500 to-teal-600' },
                { icon: Code, title: 'Stack moderno', description: 'React, FastAPI, PostgreSQL', color: 'from-violet-500 to-purple-600' },
                { icon: Heart, title: 'Impacto social', description: 'Educación accesible para todos', color: 'from-pink-500 to-rose-600' }
              ].map((item, idx) => {
                const Icon = item.icon;
                return (
                  <motion.div
                    key={item.title}
                    className="group flex items-start gap-4 p-4 rounded-xl hover:bg-white/60 dark:hover:bg-neutral-900/60 transition-all duration-300"
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.8 + (idx * 0.1), duration: 0.6 }}
                    whileHover={{ x: 4 }}
                  >
                    <motion.div 
                      className={`w-14 h-14 rounded-xl bg-gradient-to-br ${item.color} flex items-center justify-center shadow-xl flex-shrink-0 group-hover:scale-110 transition-transform duration-300`}
                      whileHover={{ rotate: 5 }}
                    >
                      <Icon className="w-7 h-7 text-white drop-shadow-lg" />
                    </motion.div>
                    <div className="flex-1">
                      <h4 className="font-bold text-lg text-neutral-900 dark:text-white mb-1 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">
                        {item.title}
                      </h4>
                      <p className="text-neutral-600 dark:text-neutral-400 text-sm leading-relaxed">
                        {item.description}
                      </p>
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
            <div className="relative p-10 rounded-3xl bg-gradient-to-br from-neutral-900 via-emerald-900 to-teal-900 dark:from-neutral-950 dark:via-emerald-950 dark:to-teal-950 text-white overflow-hidden shadow-2xl border-2 border-emerald-500/20">
              {/* Elementos decorativos mejorados */}
              <div className="absolute top-0 right-0 w-40 h-40 rounded-full bg-gradient-to-br from-emerald-400/30 to-teal-500/30 blur-3xl" />
              <div className="absolute bottom-0 left-0 w-32 h-32 rounded-full bg-gradient-to-br from-cyan-400/30 to-blue-500/30 blur-3xl" />
              <motion.div
                className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 rounded-full bg-gradient-to-br from-violet-500/20 to-purple-600/20 blur-3xl"
                animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] }}
                transition={{ duration: 4, repeat: Infinity }}
              />
              
              {/* Grid pattern overlay */}
              <div className="absolute inset-0 opacity-10" style={{
                backgroundImage: 'linear-gradient(rgba(255,255,255,.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.05) 1px, transparent 1px)',
                backgroundSize: '30px 30px'
              }} />
              
              <div className="relative z-10">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  className="mb-6"
                >
                  <h3 className="text-3xl md:text-4xl font-black mb-4 leading-tight">
                    ¡Sé parte del{' '}
                    <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                      cambio
                    </span>
                    !
                  </h3>
                  <p className="text-white/90 text-lg mb-2 leading-relaxed">
                    Ayuda a mejorar la educación para millones de estudiantes. 
                  </p>
                  <p className="text-emerald-300 font-semibold text-base">
                    Cada línea de código cuenta en nuestra misión 💚
                  </p>
                </motion.div>
                
                <div className="flex flex-col sm:flex-row gap-4">
                  <motion.a
                    href="https://github.com/Estefaniaxd/Acadify"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-white text-neutral-900 font-bold hover:bg-neutral-100 transition-all duration-300 shadow-xl hover:shadow-2xl"
                    whileHover={{ scale: 1.03, y: -2 }}
                    whileTap={{ scale: 0.97 }}
                  >
                    <Github className="w-5 h-5" />
                    Ver en GitHub
                    <motion.div
                      animate={{ x: [0, 3, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    >
                      →
                    </motion.div>
                  </motion.a>
                  <motion.a
                    href="/docs"
                    className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl border-2 border-white/30 text-white font-semibold hover:bg-white/10 hover:border-white/50 transition-all duration-300 backdrop-blur-sm"
                    whileHover={{ scale: 1.03, y: -2 }}
                    whileTap={{ scale: 0.97 }}
                  >
                    <Code className="w-5 h-5" />
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
