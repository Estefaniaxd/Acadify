/**
 * Provider para el sistema de rachas
 * Maneja la lógica de mostrar el modal automáticamente al iniciar sesión
 */
import React, { createContext, useContext, useEffect, useState } from 'react';
import StreakWelcomeModal from '../components/gamification/StreakWelcomeModal';
import { useRacha } from '../hooks/useRacha';

interface RachaContextValue {
  rachaActual: number;
  mejorRacha: number;
  yaRegistroHoy: boolean;
  enRiesgo: boolean;
  recuperacionesDisponibles: number;
  recargar: () => Promise<void>;
}

const RachaContext = createContext<RachaContextValue | undefined>(undefined);

interface RachaProviderProps {
  children: React.ReactNode;
}

export const RachaProvider: React.FC<RachaProviderProps> = ({ children }) => {
  const {
    rachaState,
    registrarAccesoDiario,
    recargarEstado
  } = useRacha();

  const [showModal, setShowModal] = useState(false);
  const [rachaData, setRachaData] = useState<any>(null);
  const [hasCheckedToday, setHasCheckedToday] = useState(false);

  // Verificar si hay usuario autenticado
  const isAuthenticated = !!localStorage.getItem('access_token');

  /**
   * Verifica si debe mostrar el modal al cargar
   */
  useEffect(() => {
    const checkAndRegisterStreak = async () => {
      // Solo ejecutar si hay usuario autenticado
      if (!isAuthenticated) return;

      // Solo ejecutar una vez por sesión
      if (hasCheckedToday) return;

      // Esperar a que el estado de racha esté disponible
      if (!rachaState) return;

      try {
        // Registrar acceso diario
        const resultado = await registrarAccesoDiario();
        
        if (resultado) {
          // SIEMPRE mostrar modal con los datos de la racha
          setRachaData(resultado);
          setShowModal(true);
        }

        setHasCheckedToday(true);
      } catch (error) {
        console.error('Error registrando racha:', error);
        setHasCheckedToday(true);
      }
    };

    checkAndRegisterStreak();
  }, [rachaState, hasCheckedToday, registrarAccesoDiario, isAuthenticated]);

  /**
   * Cierra el modal
   */
  const handleCloseModal = () => {
    setShowModal(false);
  };

  const contextValue: RachaContextValue = {
    rachaActual: rachaState?.racha_actual || 0,
    mejorRacha: rachaState?.mejor_racha || 0,
    yaRegistroHoy: rachaState?.ya_registro_hoy || false,
    enRiesgo: rachaState?.en_riesgo || false,
    recuperacionesDisponibles: rachaState?.recuperaciones_disponibles || 0,
    recargar: recargarEstado
  };

  return (
    <RachaContext.Provider value={contextValue}>
      {children}
      <StreakWelcomeModal
        isOpen={showModal}
        onClose={handleCloseModal}
        rachaData={rachaData}
      />
    </RachaContext.Provider>
  );
};

/**
 * Hook para usar el contexto de racha
 */
export const useRachaContext = (): RachaContextValue => {
  const context = useContext(RachaContext);
  if (!context) {
    throw new Error('useRachaContext debe usarse dentro de un RachaProvider');
  }
  return context;
};

export default RachaProvider;
