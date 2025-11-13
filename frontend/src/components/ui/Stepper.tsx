/**
 * Stepper Component
 * Componente de pasos para formularios y procesos
 * Sigue principios SOLID y mejores prácticas de accesibilidad
 */

import React, { memo, useCallback } from 'react';
import { motion } from 'framer-motion';
;
import type { IconType } from 'react-icons';
import { AlertCircle, Check, X } from 'lucide-react';

/* ============================================
   TYPES & INTERFACES
   ============================================ */

export type StepStatus = 'complete' | 'active' | 'error' | 'incomplete';
export type StepperOrientation = 'horizontal' | 'vertical';

export interface Step {
  id: string;
  label: string;
  description?: string;
  icon?: IconType;
  status?: StepStatus;
}

export interface StepperProps {
  steps: Step[];
  currentStep: number; // Index del paso actual (0-based)
  orientation?: StepperOrientation;
  onStepClick?: (stepIndex: number) => void;
  clickable?: boolean; // Permitir navegar haciendo click
  showDescription?: boolean;
  className?: string;
}

/* ============================================
   CONFIGURATION
   ============================================ */

const STATUS_COLORS = {
  complete: {
    bg: 'bg-emerald-500 dark:bg-emerald-600',
    text: 'text-emerald-600 dark:text-emerald-400',
    border: 'border-emerald-500 dark:border-emerald-600',
    icon: 'text-white'
  },
  active: {
    bg: 'bg-violet-600 dark:bg-violet-500',
    text: 'text-violet-600 dark:text-violet-400',
    border: 'border-violet-600 dark:border-violet-500',
    icon: 'text-white'
  },
  error: {
    bg: 'bg-red-500 dark:bg-red-600',
    text: 'text-red-600 dark:text-red-400',
    border: 'border-red-500 dark:border-red-600',
    icon: 'text-white'
  },
  incomplete: {
    bg: 'bg-neutral-200 dark:bg-neutral-700',
    text: 'text-neutral-500 dark:text-neutral-400',
    border: 'border-neutral-300 dark:border-neutral-600',
    icon: 'text-neutral-500 dark:text-neutral-400'
  }
};

const STATUS_ICONS: Record<StepStatus, IconType> = {
  complete: Check,
  active: () => null,
  error: X,
  incomplete: () => null
};

/* ============================================
   HELPER FUNCTION
   ============================================ */

const getStepStatus = (index: number, currentStep: number, step: Step): StepStatus => {
  if (step.status) return step.status;
  if (index < currentStep) return 'complete';
  if (index === currentStep) return 'active';
  return 'incomplete';
};

/* ============================================
   SUB-COMPONENTS
   ============================================ */

interface StepIconProps {
  step: Step;
  status: StepStatus;
  index: number;
}

const StepIcon = memo<StepIconProps>(({ step, status, index }) => {
  const colors = STATUS_COLORS[status];
  const StatusIcon = STATUS_ICONS[status];
  const CustomIcon = step.icon;
  const showStatusIcon = status !== 'active' && status !== 'incomplete';

  return (
    <motion.div
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      className={`
        relative w-10 h-10 rounded-full flex items-center justify-center
        ${colors.bg}
        ${status === 'active' ? 'ring-4 ring-violet-200 dark:ring-violet-900/50' : ''}
        transition-all duration-300
      `}
    >
      {showStatusIcon ? (
        <StatusIcon className={`w-5 h-5 ${colors.icon}`} />
      ) : CustomIcon ? (
        <CustomIcon className={`w-5 h-5 ${colors.icon}`} />
      ) : (
        <span className={`font-bold text-sm ${colors.icon}`}>
          {index + 1}
        </span>
      )}

      {/* Pulse animation for active step */}
      {status === 'active' && (
        <motion.div
          className="absolute inset-0 rounded-full bg-violet-400"
          animate={{ scale: [1, 1.3], opacity: [0.5, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        />
      )}
    </motion.div>
  );
});

StepIcon.displayName = 'StepIcon';

interface StepConnectorProps {
  status: StepStatus;
  orientation: StepperOrientation;
}

const StepConnector = memo<StepConnectorProps>(({ status, orientation }) => {
  const colors = STATUS_COLORS[status];
  const isHorizontal = orientation === 'horizontal';

  return (
    <div
      className={`
        ${isHorizontal ? 'flex-1 h-0.5 mx-4' : 'w-0.5 h-12 ml-5 my-2'}
        bg-neutral-200 dark:bg-neutral-700 relative overflow-hidden
      `}
    >
      <motion.div
        initial={{ [isHorizontal ? 'width' : 'height']: status === 'complete' ? '100%' : '0%' }}
        animate={{ [isHorizontal ? 'width' : 'height']: status === 'complete' ? '100%' : '0%' }}
        transition={{ duration: 0.5, ease: 'easeInOut' }}
        className={`absolute ${isHorizontal ? 'h-full' : 'w-full'} ${colors.bg}`}
      />
    </div>
  );
});

StepConnector.displayName = 'StepConnector';

/* ============================================
   MAIN COMPONENT
   ============================================ */

export const Stepper = memo<StepperProps>(({
  steps,
  currentStep,
  orientation = 'horizontal',
  onStepClick,
  clickable = false,
  showDescription = true,
  className = ''
}) => {
  const isHorizontal = orientation === 'horizontal';

  const handleStepClick = useCallback((index: number, status: StepStatus) => {
    if (!clickable || !onStepClick) return;
    if (status === 'incomplete') return; // No permitir navegar a pasos incompletos
    onStepClick(index);
  }, [clickable, onStepClick]);

  return (
    <div className={className}>
      <div
        className={`
          flex ${isHorizontal ? 'flex-row items-center' : 'flex-col'}
        `}
        role="list"
        aria-label="Pasos del proceso"
      >
        {steps.map((step, index) => {
          const status = getStepStatus(index, currentStep, step);
          const colors = STATUS_COLORS[status];
          const isLast = index === steps.length - 1;
          const isClickable = clickable && status !== 'incomplete';

          return (
            <React.Fragment key={step.id}>
              {/* Step Item */}
              <div
                className={`
                  flex ${isHorizontal ? 'flex-col items-center' : 'flex-row items-start'}
                  ${isClickable ? 'cursor-pointer' : ''}
                  ${isHorizontal ? 'flex-1' : 'w-full'}
                `}
                role="listitem"
                onClick={() => handleStepClick(index, status)}
              >
                <div className={`flex ${isHorizontal ? 'flex-col' : 'flex-row'} items-center gap-3`}>
                  {/* Icon */}
                  <motion.div
                    whileHover={isClickable ? { scale: 1.05 } : {}}
                    whileTap={isClickable ? { scale: 0.95 } : {}}
                  >
                    <StepIcon step={step} status={status} index={index} />
                  </motion.div>

                  {/* Label & Description */}
                  <div className={`${isHorizontal ? 'text-center mt-2' : 'text-left'} min-w-0`}>
                    <div className={`font-semibold text-sm ${colors.text}`}>
                      {step.label}
                    </div>
                    {showDescription && step.description && (
                      <div className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">
                        {step.description}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Connector */}
              {!isLast && (
                <StepConnector 
                  status={getStepStatus(index, currentStep, steps[index])}
                  orientation={orientation}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
});

Stepper.displayName = 'Stepper';

export default Stepper;
