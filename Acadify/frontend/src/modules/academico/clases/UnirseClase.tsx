import React, { useState } from 'react';

interface UnirseClaseProps {
  onUnirse?: (codigoClase: string) => void;
  className?: string;
}

const UnirseClase: React.FC<UnirseClaseProps> = ({ onUnirse, className = '' }) => {
  const [codigo, setCodigo] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mensaje, setMensaje] = useState<string | null>(null);

  const handleUnirse = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!codigo.trim()) {
      setError('Por favor ingresa un código de clase');
      return;
    }

    if (codigo.length !== 8) {
      setError('El código debe tener exactamente 8 caracteres');
      return;
    }

    setLoading(true);
    setError(null);
    setMensaje(null);

    try {
      // Simular llamada a API (reemplazar con clasesAPI.unirse)
      const response = await new Promise<{success: boolean, message: string}>((resolve) => {
        setTimeout(() => {
          // Simular éxito o error
          const exito = Math.random() > 0.3;
          resolve({
            success: exito,
            message: exito ? 'Te has unido exitosamente a la clase' : 'Código inválido o expirado'
          });
        }, 1500);
      });

      if (response.success) {
        setMensaje(response.message);
        setCodigo('');
        if (onUnirse) {
          onUnirse(codigo);
        }
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError('Error al intentar unirse a la clase. Inténtalo de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  const formatearCodigo = (valor: string) => {
    // Convertir a mayúsculas y quitar caracteres no alfanuméricos
    const limpio = valor.toUpperCase().replace(/[^A-Z0-9]/g, '');
    // Limitar a 8 caracteres
    return limpio.slice(0, 8);
  };

  const handleCodigoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const valorFormateado = formatearCodigo(e.target.value);
    setCodigo(valorFormateado);
    
    // Limpiar mensajes al escribir
    if (error) setError(null);
    if (mensaje) setMensaje(null);
  };

  return (
    <div className={`bg-white rounded-lg border shadow-sm p-6 ${className}`}>
      <div className="text-center mb-6">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg 
            className="w-8 h-8 text-blue-600" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" 
            />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Unirse a Clase
        </h2>
        <p className="text-gray-600">
          Ingresa el código que te proporcionó tu docente
        </p>
      </div>

      <form onSubmit={handleUnirse} className="space-y-4">
        <div>
          <label htmlFor="codigo" className="block text-sm font-medium text-gray-700 mb-2">
            Código de Clase
          </label>
          <input
            type="text"
            id="codigo"
            value={codigo}
            onChange={handleCodigoChange}
            placeholder="MATH2025"
            className="w-full px-4 py-3 text-center text-lg font-mono tracking-widest border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            disabled={loading}
          />
          <p className="text-xs text-gray-500 mt-1 text-center">
            Formato: 4 letras + 4 números (ejemplo: MATH2025)
          </p>
        </div>

        {/* Mensajes de error o éxito */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          </div>
        )}

        {mensaje && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <p className="text-green-800 text-sm">{mensaje}</p>
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || codigo.length !== 8}
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Uniéndose...
            </div>
          ) : (
            'Unirse a Clase'
          )}
        </button>
      </form>

      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-sm font-medium text-gray-900 mb-2">¿Cómo funciona?</h3>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• Tu docente comparte un código único de 8 caracteres</li>
          <li>• Ingresa el código exactamente como se te proporcionó</li>
          <li>• Una vez dentro, tendrás acceso a todo el material de la clase</li>
          <li>• Si el código no funciona, contacta a tu docente</li>
        </ul>
      </div>

      {/* Códigos de ejemplo para desarrollo */}
  {import.meta.env.MODE === 'development' && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-xs text-yellow-800 mb-2">
            <strong>Códigos de prueba (solo desarrollo):</strong>
          </p>
          <div className="flex gap-2 flex-wrap">
            {['MATH2025', 'HIST3041', 'CHEM1505'].map((codigoEjemplo) => (
              <button
                key={codigoEjemplo}
                type="button"
                onClick={() => setCodigo(codigoEjemplo)}
                className="text-xs px-2 py-1 bg-yellow-200 text-yellow-800 rounded hover:bg-yellow-300 transition-colors"
              >
                {codigoEjemplo}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default UnirseClase;