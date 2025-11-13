/**
 * Componente de Tracking de Rachas con Calendario
 * 
 * @module components/gamificacion/RachaTracker
 * @description Calendario mensual interactivo que muestra días activos con animaciones
 */

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Flame, 
  ChevronLeft, 
  ChevronRight, 
  Calendar as CalendarIcon,
  Award,
  TrendingUp
} from 'lucide-react';
import { useRacha } from '../../hooks/useGamificacion';

interface DiaCalendario {
  fecha: Date;
  dia: number;
  mes: number;
  año: number;
  esActivo: boolean;
  esMesActual: boolean;
  esHoy: boolean;
  diaSemana: number;
}

interface TooltipData {
  dia: number;
  fecha: string;
  activo: boolean;
  puntos?: number;
}

const DIAS_SEMANA = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
const MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
];

export default function RachaTracker() {
  const { data: racha, isLoading } = useRacha();
  const [mesActual, setMesActual] = useState(new Date());
  const [tooltipData, setTooltipData] = useState<TooltipData | null>(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

  // Generar calendario del mes
  const diasDelMes = useMemo(() => {
    const año = mesActual.getFullYear();
    const mes = mesActual.getMonth();
    
    // Primer día del mes
    const primerDia = new Date(año, mes, 1);
    const primerDiaSemana = primerDia.getDay();
    
    // Último día del mes
    const ultimoDia = new Date(año, mes + 1, 0);
    const ultimoDiaDelMes = ultimoDia.getDate();
    
    const dias: DiaCalendario[] = [];
    const hoy = new Date();
    
    // Días del mes anterior (para completar la primera semana)
    const ultimoDiaMesAnterior = new Date(año, mes, 0).getDate();
    for (let i = primerDiaSemana - 1; i >= 0; i--) {
      const dia = ultimoDiaMesAnterior - i;
      dias.push({
        fecha: new Date(año, mes - 1, dia),
        dia,
        mes: mes - 1,
        año,
        esActivo: false,
        esMesActual: false,
        esHoy: false,
        diaSemana: primerDiaSemana - i - 1
      });
    }
    
    // Días del mes actual
    for (let dia = 1; dia <= ultimoDiaDelMes; dia++) {
      const fecha = new Date(año, mes, dia);
      const esHoy = 
        fecha.getDate() === hoy.getDate() &&
        fecha.getMonth() === hoy.getMonth() &&
        fecha.getFullYear() === hoy.getFullYear();
      
      // Simular días activos (en producción vendría del backend)
      // Por ahora: días activos = días hasta hoy con racha activa
      const esActivo = racha?.activa && fecha <= hoy && 
        (hoy.getTime() - fecha.getTime()) / (1000 * 60 * 60 * 24) <= (racha?.dias_actuales || 0);
      
      dias.push({
        fecha,
        dia,
        mes,
        año,
        esActivo: esActivo || false,
        esMesActual: true,
        esHoy,
        diaSemana: fecha.getDay()
      });
    }
    
    // Días del mes siguiente (para completar la última semana)
    const diasRestantes = 42 - dias.length; // 6 semanas × 7 días
    for (let dia = 1; dia <= diasRestantes; dia++) {
      dias.push({
        fecha: new Date(año, mes + 1, dia),
        dia,
        mes: mes + 1,
        año,
        esActivo: false,
        esMesActual: false,
        esHoy: false,
        diaSemana: (ultimoDia.getDay() + dia) % 7
      });
    }
    
    return dias;
  }, [mesActual, racha]);

  // Navegación de meses
  const cambiarMes = (direccion: 'anterior' | 'siguiente') => {
    setMesActual(prev => {
      const nuevaFecha = new Date(prev);
      if (direccion === 'anterior') {
        nuevaFecha.setMonth(prev.getMonth() - 1);
      } else {
        nuevaFecha.setMonth(prev.getMonth() + 1);
      }
      return nuevaFecha;
    });
  };

  const irHoy = () => {
    setMesActual(new Date());
  };

  // Handlers de tooltip
  const mostrarTooltip = (dia: DiaCalendario, e: React.MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setTooltipPos({
      x: rect.left + rect.width / 2,
      y: rect.top - 10
    });
    
    setTooltipData({
      dia: dia.dia,
      fecha: dia.fecha.toLocaleDateString('es-ES', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      }),
      activo: dia.esActivo,
      puntos: dia.esActivo ? racha?.puntos_por_dia : undefined
    });
  };

  const ocultarTooltip = () => {
    setTooltipData(null);
  };

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-48 mb-4"></div>
          <div className="grid grid-cols-7 gap-2">
            {[...Array(35)].map((_, i) => (
              <div key={i} className="aspect-square bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-lg overflow-hidden">
      {/* Header del calendario */}
      <div className="bg-gradient-to-r from-orange-500 to-red-600 p-6 text-white">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
              <CalendarIcon className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Calendario de Rachas</h2>
              <p className="text-white/90 text-sm">
                Visualiza tu actividad diaria
              </p>
            </div>
          </div>
          
          {racha && (
            <div className="text-right">
              <div className="flex items-center gap-2 justify-end mb-1">
                <Flame className="w-5 h-5" />
                <span className="text-3xl font-bold">{racha.dias_actuales}</span>
              </div>
              <p className="text-sm text-white/90">días de racha</p>
            </div>
          )}
        </div>

        {/* Navegación de mes */}
        <div className="flex items-center justify-between">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => cambiarMes('anterior')}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
          >
            <ChevronLeft className="w-5 h-5" />
          </motion.button>

          <div className="text-center">
            <h3 className="text-xl font-bold">
              {MESES[mesActual.getMonth()]} {mesActual.getFullYear()}
            </h3>
            <button
              onClick={irHoy}
              className="text-sm text-white/80 hover:text-white transition-colors"
            >
              Ir a hoy
            </button>
          </div>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => cambiarMes('siguiente')}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
          >
            <ChevronRight className="w-5 h-5" />
          </motion.button>
        </div>
      </div>

      {/* Calendario */}
      <div className="p-6">
        {/* Headers de días de la semana */}
        <div className="grid grid-cols-7 gap-2 mb-2">
          {DIAS_SEMANA.map(dia => (
            <div
              key={dia}
              className="text-center text-xs font-semibold text-gray-600 dark:text-gray-400 py-2"
            >
              {dia}
            </div>
          ))}
        </div>

        {/* Grid de días */}
        <div className="grid grid-cols-7 gap-2">
          {diasDelMes.map((dia, idx) => (
            <motion.div
              key={`${dia.mes}-${dia.dia}`}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: idx * 0.01 }}
              onMouseEnter={(e) => mostrarTooltip(dia, e)}
              onMouseLeave={ocultarTooltip}
              className={`
                aspect-square rounded-lg flex items-center justify-center relative cursor-pointer
                transition-all duration-300
                ${!dia.esMesActual 
                  ? 'opacity-30' 
                  : 'opacity-100'
                }
                ${dia.esHoy
                  ? 'ring-2 ring-blue-500 dark:ring-blue-400'
                  : ''
                }
                ${dia.esActivo
                  ? 'bg-gradient-to-br from-orange-400 to-red-500 hover:from-orange-500 hover:to-red-600 shadow-lg'
                  : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600'
                }
              `}
            >
              {/* Número del día */}
              <span className={`
                text-sm font-semibold z-10
                ${dia.esActivo 
                  ? 'text-white' 
                  : 'text-gray-700 dark:text-gray-300'
                }
              `}>
                {dia.dia}
              </span>

              {/* Ícono de fuego para días activos */}
              {dia.esActivo && (
                <motion.div
                  animate={{
                    scale: [1, 1.2, 1],
                    rotate: [0, 10, -10, 0],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    repeatDelay: 1,
                  }}
                  className="absolute top-1 right-1"
                >
                  <Flame className="w-3 h-3 text-white drop-shadow-lg" />
                </motion.div>
              )}

              {/* Indicador de hoy */}
              {dia.esHoy && (
                <div className="absolute bottom-1 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-blue-500 rounded-full"></div>
              )}
            </motion.div>
          ))}
        </div>

        {/* Leyenda */}
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-gradient-to-br from-orange-400 to-red-500 rounded flex items-center justify-center">
                <Flame className="w-3 h-3 text-white" />
              </div>
              <span className="text-gray-600 dark:text-gray-400">Día activo</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-gray-200 dark:bg-gray-700 rounded"></div>
              <span className="text-gray-600 dark:text-gray-400">Día inactivo</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-gray-200 dark:bg-gray-700 rounded ring-2 ring-blue-500"></div>
              <span className="text-gray-600 dark:text-gray-400">Hoy</span>
            </div>
          </div>
        </div>

        {/* Stats adicionales */}
        {racha && (
          <div className="mt-6 grid grid-cols-3 gap-4">
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-xl text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Flame className="w-5 h-5 text-orange-500" />
              </div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {racha.dias_actuales}
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Racha actual
              </p>
            </div>

            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-xl text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <TrendingUp className="w-5 h-5 text-violet-500" />
              </div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {racha.mejor_racha}
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Récord personal
              </p>
            </div>

            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-xl text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Award className="w-5 h-5 text-yellow-500" />
              </div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {racha.puntos_por_dia}
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Puntos/día
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Tooltip */}
      <AnimatePresence>
        {tooltipData && (
          <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 5 }}
            style={{
              position: 'fixed',
              left: tooltipPos.x,
              top: tooltipPos.y,
              transform: 'translate(-50%, -100%)',
              zIndex: 9999,
            }}
            className="pointer-events-none"
          >
            <div className="bg-gray-900 dark:bg-gray-800 text-white px-4 py-3 rounded-lg shadow-xl border border-gray-700 max-w-xs">
              <p className="font-semibold mb-1 text-sm capitalize">
                {tooltipData.fecha}
              </p>
              <div className="flex items-center gap-2">
                {tooltipData.activo ? (
                  <>
                    <Flame className="w-4 h-4 text-orange-400" />
                    <span className="text-xs text-green-400">
                      ✓ Día activo
                    </span>
                    {tooltipData.puntos && (
                      <span className="text-xs text-yellow-400">
                        +{tooltipData.puntos} pts
                      </span>
                    )}
                  </>
                ) : (
                  <span className="text-xs text-gray-400">
                    Día inactivo
                  </span>
                )}
              </div>
              {/* Flecha del tooltip */}
              <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full">
                <div className="w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900 dark:border-t-gray-800"></div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
