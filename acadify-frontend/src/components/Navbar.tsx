import fondo from "./images/fondo.png"; 
import logo from "./images/rutiliopensar.png";

export default function Navbar() {
  return (
    <nav
      className="relative flex items-center justify-between px-6 py-4 shadow-md bg-cover bg-center"
      style={{ backgroundImage: `url(${fondo})` }}
    >
      

      {/* Logo + Texto */}
      <div className="flex items-center gap-2">
  <div className="bg-white p-2 rounded-full shadow-md">
    <img src={logo} alt="Logo Acadify" className="h-12 w-12" />
  </div>
  <span className="text-xl font-bold text-indigo-950 ">Acadify</span>
</div>


      {/* Menú */}
      <div className="relative flex gap-6 text-white font-medium">
        <a href="/" className="hover:text-green-300 transition">Inicio</a>
        <a href="/register" className="hover:text-indigo-900 transition">Regístrate</a>
        <a href="/login" className="hover:text-green-300 transition">Iniciar sesión</a>
        <a href="/about" className="hover:text-indigo-900 transition">Sobre nosotros</a>
      </div>
    </nav>
  );
}
