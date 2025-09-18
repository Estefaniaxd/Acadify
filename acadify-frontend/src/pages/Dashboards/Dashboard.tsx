import { useState } from "react";
import { Role } from "../../utils/role";

// Importar dashboards
import AdminDashboard from "./AdminDashboard";
import CoordinadorDashboard from "./CoordinadorDashboard";
import ProfesorDashboard from "./ProfesorDashboard";
import EstudianteDashboard from "./EstudianteDashboard";
interface DashboardProps {
  role: Role;
  onLogout: () => void; // callback para cerrar sesión
}




export default function Dashboard({ role, onLogout }: DashboardProps) {
  const [activeRole, setActiveRole] = useState<Role>(role);
  const [isOpen, setIsOpen] = useState(true);

  const renderDashboard = () => {
    switch (activeRole) {
      case "admin":
        return <AdminDashboard />;
      case "coordinador":
        return <CoordinadorDashboard />;
      case "profesor":
        return <ProfesorDashboard />;
      case "estudiante":
        return <EstudianteDashboard />;
      default:
        return (
          <div className="p-6 text-center">
            <h1 className="text-2xl font-bold text-gray-600">Rol no reconocido</h1>
          </div>
        );
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside
        className={`${
          isOpen ? "w-64" : "w-20"
        } bg-gradient-to-b from-violet-700 to-indigo-800 text-white flex flex-col p-4 transition-all duration-300`}
      >
        {/* Botón toggle */}
        <div className="flex justify-end mb-6">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="p-2 rounded hover:bg-violet-600"
          >
            {isOpen ? "Cerrar ⌧" : "☰"}
          </button>
        </div>

        <nav className="flex flex-col gap-3 flex-1">
          <button
            className={`flex items-center gap-2 p-2 rounded ${
              activeRole === "admin" ? "bg-violet-600" : "hover:bg-indigo-600"
            }`}
            onClick={() => setActiveRole("admin")}
          >
            <span>Ⅰ</span>
            {isOpen && "Administrador"}
          </button>
          <button
            className={`flex items-center gap-2 p-2 rounded ${
              activeRole === "coordinador"
                ? "bg-violet-600"
                : "hover:bg-indigo-600"
            }`}
            onClick={() => setActiveRole("coordinador")}
          >
            <span>Ⅱ</span>
            {isOpen && "Coordinador"}
          </button>
          <button
            className={`flex items-center gap-2 p-2 rounded ${
              activeRole === "profesor" ? "bg-violet-600" : "hover:bg-indigo-600"
            }`}
            onClick={() => setActiveRole("profesor")}
          >
            <span>Ⅲ</span>
            {isOpen && "Profesor"}
          </button>
          <button
            className={`flex items-center gap-2 p-2 rounded ${
              activeRole === "estudiante"
                ? "bg-violet-600"
                : "hover:bg-violet-600"
            }`}
            onClick={() => setActiveRole("estudiante")}
          >
            <span>Ⅳ</span>
            {isOpen && "Estudiante"}
          </button>
        </nav>

        {/* Logout */}
        <button
          onClick={onLogout}
          className="flex items-center gap-2 p-2 mt-6 bg-red-600 hover:bg-red-700 rounded"
        >
          <span>Ⅵ</span>
          {isOpen && "Cerrar sesión"}
        </button>
      </aside>

      {/* Contenido dinámico */}
      <main className="flex-1 bg-gray-100 p-6 transition-all duration-300">
        {renderDashboard()}
      </main>
    </div>
  );
}
