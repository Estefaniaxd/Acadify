import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";

// Páginas
import HomePage from "./pages/HomePage";
import LoginPage from "./components/auth/Login";
import AboutPage from "./pages/AboutPage";
import RegisterPage from "./components/auth/Register";
import Preloader from "./components/Preloader";

export default function App() {
  // Estado que controla si se muestra el preloader
  const [loading, setLoading] = useState(true);

  return (
    <>
      {loading ? (
        // Mientras está cargando mostramos el Preloader
        <Preloader onFinish={() => setLoading(false)} />
      ) : (
        // Cuando termina, ya mostramos la app
        <Router>
          {/* Barra de navegación siempre visible */}
          <Navbar />

          {/* Contenido principal que cambia según la ruta */}
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/about" element={<AboutPage />} />
          </Routes>
        </Router>
      )}
    </>
  );
}
