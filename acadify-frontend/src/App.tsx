import { useState } from "react";
import { BrowserRouter as Router, Routes, Route, useLocation } from "react-router-dom";
import Navbar from "./components/Navbar";


// Páginas
import HomePage from "./pages/HomePage";
import LoginPage from "./components/auth/Login";
import AboutPage from "./pages/AboutPage";
import RegisterPage from "./components/auth/Register";
import Preloader from "./components/Preloader";
import Dashboard from "./pages/Dashboards/Dashboard"; 
import { Role } from "./utils/role"; // 👈 importa tu tipo Role

function AppContent() {
  const location = useLocation();
  const [currentRole] = useState<Role>("estudiante");

  const isDashboard = location.pathname.startsWith("/dashboard");

  return (
    <>
      {/* Mostrar navbar dependiendo de la ruta */}
      {isDashboard ? <Navbar /> : <Navbar />}

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route
          path="/dashboard"
          element={
            <Dashboard
              role={currentRole}
              onLogout={() => alert("Cerrar sesión desde Dashboard")}
            />
          }
        />
      </Routes>
    </>
  );
}

export default function App() {
  const [loading, setLoading] = useState(true);

  return (
    <>
      {loading ? (
        <Preloader onFinish={() => setLoading(false)} />
      ) : (
        <Router>
          <AppContent />
        </Router>
      )}
    </>
  );
}
