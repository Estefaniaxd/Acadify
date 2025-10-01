import React from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  hover?: boolean;
  clickable?: boolean;
  onClick?: () => void;
  loading?: boolean;
  disabled?: boolean;
}

const paddingClasses = {
  none: '',
  sm: 'p-3',
  md: 'p-4',
  lg: 'p-6',
  xl: 'p-8'
};

export function Card({
  children,
  className = '',
  padding = 'md',
  hover = false,
  clickable = false,
  onClick,
  loading = false,
  disabled = false
}: CardProps) {
  const isInteractive = clickable || onClick;
  
  return (
    <motion.div
      className={`
        bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700
        shadow-sm transition-all duration-200
        ${paddingClasses[padding]}
        ${hover || isInteractive ? 'hover:shadow-md hover:border-gray-300 dark:hover:border-gray-600' : ''}
        ${isInteractive ? 'cursor-pointer' : ''}
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        ${className}
      `}
      onClick={!disabled ? onClick : undefined}
      whileHover={hover || isInteractive ? { y: -2 } : {}}
      whileTap={isInteractive ? { scale: 0.98 } : {}}
      layout
    >
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        children
      )}
    </motion.div>
  );
}

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
  className?: string;
}

export function CardHeader({ title, subtitle, actions, className = '' }: CardHeaderProps) {
  return (
    <div className={`flex items-start justify-between mb-4 ${className}`}>
      <div className="flex-1">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          {title}
        </h3>
        {subtitle && (
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            {subtitle}
          </p>
        )}
      </div>
      {actions && (
        <div className="flex-shrink-0 ml-4">
          {actions}
        </div>
      )}
    </div>
  );
}

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

export function CardContent({ children, className = '' }: CardContentProps) {
  return (
    <div className={`${className}`}>
      {children}
    </div>
  );
}

interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
  divider?: boolean;
}

export function CardFooter({ children, className = '', divider = true }: CardFooterProps) {
  return (
    <div className={`
      ${divider ? 'border-t border-gray-200 dark:border-gray-700 pt-4' : ''}
      mt-4 ${className}
    `}>
      {children}
    </div>
  );
}

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export function EmptyState({ icon, title, description, action, className = '' }: EmptyStateProps) {
  return (
    <div className={`text-center py-12 ${className}`}>
      {icon && (
        <div className="flex justify-center mb-4">
          <div className="w-12 h-12 text-gray-400 dark:text-gray-500">
            {icon}
          </div>
        </div>
      )}
      
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
        {title}
      </h3>
      
      {description && (
        <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
          {description}
        </p>
      )}
      
      {action && action}
    </div>
  );
}

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    label: string;
    direction: 'up' | 'down' | 'neutral';
  };
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'gray';
  className?: string;
}

const colorClasses = {
  blue: {
    bg: 'bg-blue-50 dark:bg-blue-900/20',
    icon: 'text-blue-600 dark:text-blue-400',
    value: 'text-blue-900 dark:text-blue-100'
  },
  green: {
    bg: 'bg-green-50 dark:bg-green-900/20',
    icon: 'text-green-600 dark:text-green-400',
    value: 'text-green-900 dark:text-green-100'
  },
  yellow: {
    bg: 'bg-yellow-50 dark:bg-yellow-900/20',
    icon: 'text-yellow-600 dark:text-yellow-400',
    value: 'text-yellow-900 dark:text-yellow-100'
  },
  red: {
    bg: 'bg-red-50 dark:bg-red-900/20',
    icon: 'text-red-600 dark:text-red-400',
    value: 'text-red-900 dark:text-red-100'
  },
  purple: {
    bg: 'bg-purple-50 dark:bg-purple-900/20',
    icon: 'text-purple-600 dark:text-purple-400',
    value: 'text-purple-900 dark:text-purple-100'
  },
  gray: {
    bg: 'bg-gray-50 dark:bg-gray-900/20',
    icon: 'text-gray-600 dark:text-gray-400',
    value: 'text-gray-900 dark:text-gray-100'
  }
};

export function StatCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  color = 'blue',
  className = ''
}: StatCardProps) {
  const colors = colorClasses[color];
  
  return (
    <Card className={className} hover>
      <div className="flex items-center">
        {icon && (
          <div className={`
            flex-shrink-0 p-3 rounded-lg mr-4
            ${colors.bg}
          `}>
            <div className={`w-6 h-6 ${colors.icon}`}>
              {icon}
            </div>
          </div>
        )}
        
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {title}
          </p>
          <p className={`text-2xl font-bold ${colors.value}`}>
            {value}
          </p>
          {subtitle && (
            <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
              {subtitle}
            </p>
          )}
        </div>
        
        {trend && (
          <div className="flex-shrink-0 text-right">
            <div className={`
              flex items-center text-sm font-medium
              ${trend.direction === 'up' ? 'text-green-600 dark:text-green-400' : ''}
              ${trend.direction === 'down' ? 'text-red-600 dark:text-red-400' : ''}
              ${trend.direction === 'neutral' ? 'text-gray-600 dark:text-gray-400' : ''}
            `}>
              <span className="mr-1">
                {trend.direction === 'up' && '↗'}
                {trend.direction === 'down' && '↘'}
                {trend.direction === 'neutral' && '→'}
              </span>
              {trend.value}%
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
              {trend.label}
            </p>
          </div>
        )}
      </div>
    </Card>
  );
}

interface GridProps {
  children: React.ReactNode;
  cols?: 1 | 2 | 3 | 4 | 5 | 6;
  gap?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const colsClasses = {
  1: 'grid-cols-1',
  2: 'grid-cols-1 md:grid-cols-2',
  3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
  4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
  5: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5',
  6: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6'
};

const gapClasses = {
  sm: 'gap-3',
  md: 'gap-4',
  lg: 'gap-6',
  xl: 'gap-8'
};

export function Grid({ children, cols = 3, gap = 'md', className = '' }: GridProps) {
  return (
    <div className={`
      grid ${colsClasses[cols]} ${gapClasses[gap]}
      ${className}
    `}>
      {children}
    </div>
  );
}

interface ListProps {
  children: React.ReactNode;
  divided?: boolean;
  className?: string;
}

export function List({ children, divided = true, className = '' }: ListProps) {
  return (
    <div className={`
      space-y-0
      ${divided ? 'divide-y divide-gray-200 dark:divide-gray-700' : ''}
      ${className}
    `}>
      {children}
    </div>
  );
}

interface ListItemProps {
  children: React.ReactNode;
  clickable?: boolean;
  onClick?: () => void;
  className?: string;
  padding?: 'sm' | 'md' | 'lg';
}

const listPaddingClasses = {
  sm: 'px-3 py-2',
  md: 'px-4 py-3',
  lg: 'px-6 py-4'
};

export function ListItem({ 
  children, 
  clickable = false, 
  onClick, 
  className = '',
  padding = 'md'
}: ListItemProps) {
  return (
    <div
      className={`
        ${listPaddingClasses[padding]}
        ${clickable || onClick ? 'hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors' : ''}
        ${className}
      `}
      onClick={onClick}
    >
      {children}
    </div>
  );
}