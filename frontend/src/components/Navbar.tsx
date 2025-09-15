import fondo from "../images/fondo.png";
import logo from "../images/icon.png";
import { useState } from "react";
import { motion } from "framer-motion";
import { FaMoon, FaSun } from 'react-icons/fa';

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [dark, setDark] = useState(false);

  return (
    <header className="w-full" style={{ backgroundImage: `url(${fondo})`, backgroundSize: 'cover' }}>
      <nav className="max-w-6xl mx-auto flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="bg-white p-2 rounded-full shadow-md flex items-center">
            <img src={logo} alt="Logo Acadify" className="h-10 w-10" />
          </div>
          <a href="/" className="text-xl font-bold text-acadify-purple">Acadify <span className="ml-1">✨</span></a>
        </div>

        <div className="hidden md:flex items-center gap-6 text-sm font-medium">
          <a href="/" className="text-gray-800 hover:text-acadify-green transition">Inicio</a>
          <a href="/about" className="text-gray-800 hover:text-acadify-green transition">Nosotros</a>
          <a href="/login" className="text-gray-800 hover:text-acadify-green transition">Iniciar sesión</a>
          <a href="/register" className="accent-btn">Crear cuenta</a>
        </div>

        <div className="flex items-center gap-3">
          <button onClick={() => setDark(!dark)} className="p-2 rounded-full hover:bg-gray-100">
            {dark ? <FaSun /> : <FaMoon />}
          </button>

          {/* User placeholder */}
          <motion.div whileTap={{ scale: 0.95 }} className="relative">
            <button onClick={() => setOpen(!open)} className="w-10 h-10 rounded-full bg-gradient-to-tr from-acadify-purple to-acadify-green flex items-center justify-center text-white shadow-md">
              U
            </button>

            {open && (
              <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} className="absolute right-0 mt-2 w-40 bg-white rounded-md shadow-lg p-2">
                <a href="/dashboard" className="block px-2 py-1 hover:bg-gray-50 rounded">Dashboard</a>
                <a href="/profile" className="block px-2 py-1 hover:bg-gray-50 rounded">Perfil</a>
                <a href="/settings" className="block px-2 py-1 hover:bg-gray-50 rounded">Configuración</a>
                <button className="w-full text-left px-2 py-1 hover:bg-gray-50 rounded">Cerrar sesión</button>
              </motion.div>
            )}
          </motion.div>

          <button className="md:hidden p-2" onClick={() => setOpen(!open)}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </nav>

      {/* Mobile menu */}
      <div className={`md:hidden ${open ? 'block' : 'hidden'} bg-white/60 backdrop-blur-sm`}> 
        <div className="max-w-6xl mx-auto px-4 py-4 flex flex-col gap-2">
          <a href="/" className="py-2">Inicio</a>
          <a href="/about" className="py-2">Nosotros</a>
          <a href="/login" className="py-2">Iniciar sesión</a>
          <a href="/register" className="py-2">Crear cuenta</a>
        </div>
      </div>
    </header>
  );
}
