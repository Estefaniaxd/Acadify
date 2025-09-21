import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import Preloader from '../components/Preloader';
import HeroSection from '../components/HeroSection';
import FeaturesSection from '../components/FeaturesSection';
import GamificationSection from '../components/GamificationSection';
import OpenSourceSection from '../components/OpenSourceSection';
import TestimonialsSection from '../components/TestimonialsSection';
import CTASection from '../components/CTASection';
import Footer from '../components/Footer';

const HomePage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const { isAuthenticated, user } = useAuth();
  const { theme, toggleTheme } = useTheme();

  useEffect(() => {
    // Simular carga de recursos
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 3000); // 3 segundos de preloader

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return <Preloader onFinish={() => setIsLoading(false)} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 to-purple-700">
      {/* Header */}
      <header className="absolute top-0 w-full z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <span className="text-2xl font-bold text-white">Acadify</span>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={toggleTheme}
                className="p-2 rounded-md text-white hover:text-indigo-200 transition-colors"
              >
                {theme === 'dark' ? '☀️' : '🌙'}
              </button>
              
              {isAuthenticated ? (
                <div className="flex items-center space-x-4">
                  <span className="text-white">Hola, {user?.nombres}</span>
                  <Link
                    to="/dashboard"
                    className="bg-white text-indigo-600 px-4 py-2 rounded-md font-medium hover:bg-indigo-50 transition-colors"
                  >
                    Dashboard
                  </Link>
                </div>
              ) : (
                <div className="flex items-center space-x-4">
                  <Link
                    to="/login"
                    className="text-white hover:text-indigo-200 transition-colors"
                  >
                    Iniciar Sesión
                  </Link>
                  <Link
                    to="/register"
                    className="bg-white text-indigo-600 px-4 py-2 rounded-md font-medium hover:bg-indigo-50 transition-colors"
                  >
                    Registrarse
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content with proper spacing */}
      <main className="pt-20">
        {/* Hero Section */}
        <HeroSection />
        
        {/* Features Section */}
        <FeaturesSection />
        
        {/* Gamification Section */}
        <GamificationSection />
        
        {/* Open Source Section */}
        <OpenSourceSection />
        
        {/* Testimonials Section */}
        <TestimonialsSection />
        
        {/* Call to Action Section */}
        <CTASection />
      </main>
      
      {/* Footer */}
      <Footer />
    </div>
  );
};

export default HomePage;
