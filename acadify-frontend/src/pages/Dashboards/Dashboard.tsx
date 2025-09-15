import { Role } from "../../utils/role";

// Importar los dashboards
import AdminDashboard from "./AdminDashboard";
import CoordinadorDashboard from "./CoordinadorDashboard";
import ProfesorDashboard from "./ProfesorDashboard";
import EstudianteDashboard from "./EstudianteDashboard";

interface DashboardProps {
  role: Role;
}

export default function Dashboard({ role }: DashboardProps) {
  switch (role) {
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
}
