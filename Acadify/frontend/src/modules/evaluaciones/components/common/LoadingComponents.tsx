import React from 'react';
import { motion } from 'framer-motion';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'white';
  message?: string;
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6', 
  lg: 'w-8 h-8',
  xl: 'w-12 h-12'
};

const colorClasses = {
  primary: 'border-blue-600 dark:border-blue-400',
  secondary: 'border-gray-600 dark:border-gray-400',
  white: 'border-white'
};

export function LoadingSpinner({ size = 'md', color = 'primary', message }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center space-y-3">
      <motion.div
        className={`
          ${sizeClasses[size]}
          border-2 border-t-transparent rounded-full
          ${colorClasses[color]}
        `}
        animate={{ rotate: 360 }}
        transition={{
          duration: 1,
          repeat: Infinity,
          ease: "linear"
        }}
      />
      {message && (
        <p className="text-sm text-gray-600 dark:text-gray-400 animate-pulse">
          {message}
        </p>
      )}
    </div>
  );
}

interface LoadingOverlayProps {
  message?: string;
  show: boolean;
}

export function LoadingOverlay({ message = 'Cargando...', show }: LoadingOverlayProps) {
  if (!show) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
    >
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-2xl border border-gray-200 dark:border-gray-700"
      >
        <LoadingSpinner size="lg" message={message} />
      </motion.div>
    </motion.div>
  );
}

interface SkeletonProps {
  className?: string;
  count?: number;
}

export function Skeleton({ className = 'h-4 w-full', count = 1 }: SkeletonProps) {
  return (
    <div className="animate-pulse space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={`bg-gray-200 dark:bg-gray-700 rounded-lg ${className}`}
        />
      ))}
    </div>
  );
}

interface CardSkeletonProps {
  showImage?: boolean;
  lines?: number;
}

export function CardSkeleton({ showImage = false, lines = 3 }: CardSkeletonProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 animate-pulse">
      {showImage && (
        <div className="h-48 bg-gray-200 dark:bg-gray-700 rounded-lg mb-4" />
      )}
      <div className="space-y-3">
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded-lg w-3/4" />
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className="h-4 bg-gray-200 dark:bg-gray-700 rounded-lg"
            style={{ width: `${Math.random() * 40 + 60}%` }}
          />
        ))}
      </div>
      <div className="flex justify-between items-center mt-6">
        <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded-lg w-20" />
        <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded-lg w-24" />
      </div>
    </div>
  );
}

interface LoadingDotsProps {
  color?: string;
}

export function LoadingDots({ color = 'bg-blue-600 dark:bg-blue-400' }: LoadingDotsProps) {
  return (
    <div className="flex space-x-1 justify-center items-center">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className={`w-2 h-2 rounded-full ${color}`}
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.7, 1, 0.7]
          }}
          transition={{
            duration: 0.8,
            repeat: Infinity,
            delay: i * 0.2
          }}
        />
      ))}
    </div>
  );
}

interface ProgressBarProps {
  progress: number;
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
  size?: 'sm' | 'md' | 'lg';
  showPercentage?: boolean;
  animated?: boolean;
}

export function ProgressBar({ 
  progress, 
  color = 'blue', 
  size = 'md',
  showPercentage = false,
  animated = true 
}: ProgressBarProps) {
  const colorClasses = {
    blue: 'bg-blue-600 dark:bg-blue-400',
    green: 'bg-green-600 dark:bg-green-400',
    yellow: 'bg-yellow-600 dark:bg-yellow-400',
    red: 'bg-red-600 dark:bg-red-400',
    purple: 'bg-purple-600 dark:bg-purple-400'
  };

  const sizeClasses = {
    sm: 'h-2',
    md: 'h-3',
    lg: 'h-4'
  };

  const clampedProgress = Math.min(Math.max(progress, 0), 100);

  return (
    <div className="w-full">
      <div className={`
        w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden
        ${sizeClasses[size]}
      `}>
        <motion.div
          className={`h-full rounded-full ${colorClasses[color]} ${animated ? 'transition-all duration-300 ease-out' : ''}`}
          initial={animated ? { width: '0%' } : { width: `${clampedProgress}%` }}
          animate={{ width: `${clampedProgress}%` }}
          transition={animated ? { duration: 0.5, ease: 'easeOut' } : { duration: 0 }}
        />
      </div>
      {showPercentage && (
        <div className="flex justify-between mt-1 text-xs text-gray-600 dark:text-gray-400">
          <span>{Math.round(clampedProgress)}%</span>
          <span>100%</span>
        </div>
      )}
    </div>
  );
}