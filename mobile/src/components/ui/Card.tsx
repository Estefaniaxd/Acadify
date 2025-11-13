import React from 'react';
import { View, ViewProps, StyleSheet } from 'react-native';

export interface CardProps extends Omit<ViewProps, 'style'> {
  children: React.ReactNode;
  variant?: 'default' | 'elevated' | 'outlined';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  style?: any;
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'default',
  padding = 'md',
  style,
  ...props
}) => (
  <View
    style={[
      styles.base,
      variant && (styles as any)['v_' + variant],
      padding && (styles as any)['p_' + padding],
      style
    ]}
    {...props}
  >
    {children}
  </View>
);

const styles = StyleSheet.create({
  base: { borderRadius: 16, backgroundColor: '#ffffff' },
  v_default: {},
  v_elevated: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3
  },
  v_outlined: { borderWidth: 1, borderColor: '#e5e7eb' },
  p_none: { padding: 0 },
  p_sm: { padding: 12 },
  p_md: { padding: 16 },
  p_lg: { padding: 24 }
});

export default Card;
