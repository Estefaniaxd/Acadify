import React from 'react';
import {
  Modal as RNModal,
  View,
  Text,
  TouchableOpacity,
  Pressable,
  ModalProps as RNModalProps,
} from 'react-native';
import { cn } from '@utils/cn';

export interface ModalProps extends Omit<RNModalProps, 'visible' | 'onRequestClose'> {
  /**
   * Si el modal está abierto
   */
  open: boolean;
  
  /**
   * Callback al cerrar
   */
  onClose: () => void;
  
  /**
   * Título del modal
   */
  title?: string;
  
  /**
   * Descripción/subtitle
   */
  description?: string;
  
  /**
   * Contenido del modal
   */
  children: React.ReactNode;
  
  /**
   * Variante del modal
   * @default 'center'
   */
  variant?: 'center' | 'bottom';
  
  /**
   * Tamaño del modal
   * @default 'md'
   */
  size?: 'sm' | 'md' | 'lg' | 'full';
  
  /**
   * Si muestra botón de cerrar (X)
   * @default true
   */
  showClose?: boolean;
  
  /**
   * Si permite cerrar tocando el overlay
   * @default true
   */
  dismissible?: boolean;
  
  /**
   * Clase adicional para el contenido
   */
  className?: string;
}

/**
 * Componente Modal - Diálogo modal con animaciones
 * 
 * @example
 * ```tsx
 * <Modal
 *   open={isOpen}
 *   onClose={() => setIsOpen(false)}
 *   title="Confirmar acción"
 * >
 *   <Text>¿Estás seguro?</Text>
 * </Modal>
 * ```
 */
export const Modal: React.FC<ModalProps> = ({
  open,
  onClose,
  title,
  description,
  children,
  variant = 'center',
  size = 'md',
  showClose = true,
  dismissible = true,
  className,
  ...props
}) => {
  // Estilos por tamaño
  const sizeStyles = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    full: 'w-full h-full',
  };
  
  // Estilos por variante
  const variantStyles = {
    center: 'rounded-2xl mx-4',
    bottom: 'rounded-t-3xl w-full',
  };
  
  const containerStyles = {
    center: 'items-center justify-center',
    bottom: 'items-end justify-end',
  };
  
  const handleBackdropPress = () => {
    if (dismissible) {
      onClose();
    }
  };
  
  return (
    <RNModal
      visible={open}
      transparent
      animationType="none"
      statusBarTranslucent
      onRequestClose={onClose}
      {...props}
    >
      <View className="flex-1">
        {/* Backdrop */}
        <Animated.View
          entering={FadeIn.duration(200)}
          exiting={FadeOut.duration(200)}
          className="absolute inset-0 bg-black/50"
        >
          <Pressable
            className="flex-1"
            onPress={handleBackdropPress}
          />
        </Animated.View>
        
        {/* Modal Content */}
        <View className={cn('flex-1', containerStyles[variant])}>
          <Animated.View
            entering={variant === 'bottom' ? SlideInDown.duration(300) : FadeIn.duration(300)}
            exiting={variant === 'bottom' ? SlideOutDown.duration(300) : FadeOut.duration(300)}
            className={cn(
              'bg-white',
              sizeStyles[size],
              variantStyles[variant],
              size !== 'full' && 'max-h-[90%]',
              className
            )}
          >
            {/* Header */}
            {(title || showClose) && (
              <View className="flex-row items-center justify-between p-6 pb-4">
                <View className="flex-1 pr-4">
                  {title && (
                    <Text className="text-xl font-bold text-gray-900">
                      {title}
                    </Text>
                  )}
                  {description && (
                    <Text className="text-sm text-gray-600 mt-1">
                      {description}
                    </Text>
                  )}
                </View>
                
                {showClose && (
                  <TouchableOpacity
                    onPress={onClose}
                    className="w-8 h-8 items-center justify-center rounded-full bg-gray-100"
                    activeOpacity={0.7}
                  >
                    <Text className="text-gray-600 font-bold text-lg">×</Text>
                  </TouchableOpacity>
                )}
              </View>
            )}
            
            {/* Content */}
            <View className={cn('px-6', (title || showClose) ? 'pb-6' : 'py-6')}>
              {children}
            </View>
          </Animated.View>
        </View>
      </View>
    </RNModal>
  );
};

/**
 * BottomSheet - Alias de Modal con variant='bottom'
 */
export const BottomSheet: React.FC<Omit<ModalProps, 'variant'>> = (props) => {
  return <Modal {...props} variant="bottom" />;
};

export default Modal;
