import React, { useEffect } from 'react';

interface PreloaderProps {
  onFinish: () => void;
}

const Preloader: React.FC<PreloaderProps> = ({ onFinish }) => {
  useEffect(() => {
    const timer = setTimeout(onFinish, 2000);
    return () => clearTimeout(timer);
  }, [onFinish]);

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-indigo-600 to-purple-700 flex items-center justify-center z-50">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-white mb-4">Acadify</h1>
        <p className="text-xl text-indigo-200 mb-8">Cargando...</p>
        <div className="flex justify-center space-x-2">
          <div className="w-3 h-3 bg-white rounded-full animate-bounce"></div>
          <div className="w-3 h-3 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-3 h-3 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
      </div>
    </div>
  );
};

export default Preloader;
