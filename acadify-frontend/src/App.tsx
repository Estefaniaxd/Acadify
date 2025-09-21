import { useState } from "react";
import { BrowserRouter as Router, Routes, Route, useLocation } from "react-router-dom";
import Navbar from "./components/Navbar";
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Páginas
import HomePage from "./pages/HomePage";
import LoginForm from "./components/auth/LoginForm";
import RegisterForm from "./components/auth/RegisterForm";
import ForgotPasswordForm from "./components/auth/ForgotPasswordForm";
import AboutPage from "./pages/AboutPage";
import Dashboard from "./pages/Dashboard";
import Preloader from "./components/Preloader";

function AppContent() {
  const location = useLocation();
  const isHomePage = location.pathname === "/";

  return (
    <>
      {!isHomePage && <Navbar />}
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginForm />} />
        <Route path="/register" element={<RegisterForm />} />
        <Route path="/forgot-password" element={<ForgotPasswordForm />} />
        <Route path="/about" element={<AboutPage />} />
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
      </Routes>
    </>
  );
}

export default function App() {
  const [loading, setLoading] = useState(true);

  return (
    <ThemeProvider>
      <AuthProvider>
        {loading ? (
          <Preloader onFinish={() => setLoading(false)} />
        ) : (
          <Router>
            <AppContent />
          </Router>
        )}
      </AuthProvider>
    </ThemeProvider>
  );
}
