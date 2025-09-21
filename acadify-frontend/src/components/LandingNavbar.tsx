import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X, ChevronDown, Sparkles, User, LogIn } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { NavigationItem } from '../types/landing';
import ThemeToggle from './ThemeToggle';

const LandingNavbar: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [activeSection, setActiveSection] = useState('home');

  const navigationItems: NavigationItem[] = [
    { name: 'Inicio', href: '#home' },
    { name: 'Características', href: '#features' },
    { name: 'Gamificación', href: '#gamification' },
    { name: 'Open Source', href: '#opensource' },
    { name: 'Testimonios', href: '#testimonials' },
  ];

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
      
      // Detectar sección activa
      const sections = ['home', 'features', 'gamification', 'opensource', 'testimonials'];
      sections.forEach(section => {
        const element = document.getElementById(section);
        if (element) {
          const rect = element.getBoundingClientRect();
          if (rect.top <= 100 && rect.bottom >= 100) {
            setActiveSection(section);
          }
        }
      });
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (href: string) => {
    const sectionId = href.replace('#', '');
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    setIsMenuOpen(false);
  };

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled 
          ? 'bg-white/95 dark:bg-dark-900/95 backdrop-blur-xl shadow-xl border-b border-gray-200 dark:border-gray-700' 
          : 'bg-white/10 dark:bg-dark-900/20 backdrop-blur-sm'
      }`}
    >
      <nav className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <motion.div 
            className="flex items-center space-x-3 cursor-pointer"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => scrollToSection('#home')}
          >
            <motion.div 
              className="w-12 h-12 bg-gradient-to-r from-primary-600 to-secondary-600 dark:from-neon-purple dark:to-neon-green rounded-xl flex items-center justify-center shadow-lg"
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ duration: 4, repeat: Infinity }}
            >
              <Sparkles className="w-7 h-7 text-white" />
            </motion.div>
            <div className="flex flex-col">
              <span className="text-2xl font-display font-bold bg-gradient-to-r from-primary-600 to-secondary-600 dark:from-neon-purple dark:to-neon-green bg-clip-text text-transparent">
                Acadify
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">
                con Rutilio 🐱
              </span>
            </div>
          </motion.div>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center space-x-1">
            {navigationItems.map((item, index) => {
              const sectionId = item.href.replace('#', '');
              const isActive = activeSection === sectionId;
              
              return (
                <motion.button
                  key={item.name}
                  onClick={() => scrollToSection(item.href)}
                  className={`relative px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                    isActive 
                      ? 'text-white dark:text-neon-purple bg-primary-600/20 dark:bg-neon-purple/20' 
                      : 'text-white/90 dark:text-gray-200 hover:text-white dark:hover:text-neon-green hover:bg-white/10 dark:hover:bg-neon-green/10'
                  }`}
                  whileHover={{ y: -2 }}
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  {item.name}
                  {isActive && (
                    <motion.div
                      className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-primary-600 to-secondary-600 dark:from-neon-purple dark:to-neon-green rounded-full"
                      layoutId="activeSection"
                    />
                  )}
                </motion.button>
              );
            })}
          </div>

          {/* CTA Buttons */}
          <div className="hidden lg:flex items-center space-x-4">
            <ThemeToggle />
            
            <motion.button
              className="flex items-center space-x-2 px-4 py-2 text-white/90 dark:text-gray-300 hover:text-white dark:hover:text-neon-green font-medium transition-colors duration-200"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <LogIn size={18} />
              <Link to="/login">
                <span>Iniciar Sesión</span>
              </Link>
            </motion.button>
            
            <motion.button
              className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-primary-600 to-secondary-600 dark:from-neon-purple dark:to-neon-green text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-200"
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
            >
              <User size={18} />
              <Link to="/register">
                <span>Comenzar Gratis</span>
              </Link>
            </motion.button>
          </div>

          {/* Mobile menu button */}
          <div className="lg:hidden flex items-center space-x-3">
            <ThemeToggle />
            <motion.button
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-700 transition-colors"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              whileTap={{ scale: 0.95 }}
            >
              <AnimatePresence mode="wait">
                {isMenuOpen ? (
                  <motion.div
                    key="close"
                    initial={{ rotate: 0 }}
                    animate={{ rotate: 180 }}
                    exit={{ rotate: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <X size={24} className="text-gray-700 dark:text-gray-300" />
                  </motion.div>
                ) : (
                  <motion.div
                    key="menu"
                    initial={{ rotate: 180 }}
                    animate={{ rotate: 0 }}
                    exit={{ rotate: 180 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Menu size={24} className="text-gray-700 dark:text-gray-300" />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <AnimatePresence>
          {isMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0, y: -20 }}
              animate={{ opacity: 1, height: 'auto', y: 0 }}
              exit={{ opacity: 0, height: 0, y: -20 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
              className="lg:hidden mt-4 bg-white/95 dark:bg-dark-800/95 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-200/20 dark:border-gray-700/20 overflow-hidden"
            >
              <div className="p-6 space-y-4">
                {navigationItems.map((item, index) => (
                  <motion.button
                    key={item.name}
                    onClick={() => scrollToSection(item.href)}
                    className="block w-full text-left py-3 px-4 text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-neon-green hover:bg-primary-50 dark:hover:bg-dark-700 rounded-lg font-medium transition-all duration-200"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    whileHover={{ x: 5 }}
                  >
                    {item.name}
                  </motion.button>
                ))}
                
                <div className="border-t border-gray-200 pt-4 space-y-3">
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 }}
                  >
                    <Link
                      to="/login"
                      className="flex items-center space-x-2 w-full py-3 px-4 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors"
                    >
                      <LogIn size={18} />
                      <span>Iniciar Sesión</span>
                    </Link>
                  </motion.div>
                  
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.7 }}
                  >
                    <Link
                      to="/register"
                      className="flex items-center justify-center space-x-2 w-full py-3 bg-gradient-primary text-white rounded-lg font-semibold shadow-lg"
                    >
                      <User size={18} />
                      <span>Comenzar Gratis</span>
                    </Link>
                  </motion.div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>
    </motion.header>
  );
};

export default LandingNavbar;