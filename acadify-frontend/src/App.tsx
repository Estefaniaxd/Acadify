import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";

// Páginas
import HomePage from "./pages/HomePage";
import LoginPage from "./components/auth/Login";
import AboutPage from "./pages/AboutPage";
import RegisterPage from "./components/auth/Register";
import Preloader from "./components/Preloader";
import Dashboard from "./pages/Dashboards/Dashboard"; // 👈 importa tu dashboard
import { Role } from "./utils/role"; // 👈 importa tu tipo Role

export default function App() {
  // Estado que controla si se muestra el preloader
  const [loading, setLoading] = useState(true);

  // Estado del rol actual
  const [currentRole, setCurrentRole] = useState<Role>("estudiante");

  return (
    <>
      {loading ? (
        <Preloader onFinish={() => setLoading(false)} />
      ) : (
        <Router>
          <Navbar />

          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/dashboard" element={<Dashboard role={currentRole} />} />
          </Routes>
        </Router>
      )}
    </>
  );
}
