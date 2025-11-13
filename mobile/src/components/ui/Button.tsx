import React from 'react';
import { TouchableOpacity, Text, ActivityIndicator, TouchableOpacityProps, StyleSheet, ViewStyle, TextStyle } from 'react-native';

export interface ButtonProps extends Omit<TouchableOpacityProps, 'style'> {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  loading?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  disabled,
  style,
  textStyle,
  ...props
}) => (
  <TouchableOpacity
    style={[
      styles.base,
      variant && (styles as any)['v_' + variant],
      size && (styles as any)['s_' + size],
      fullWidth && styles.fullWidth,
      (disabled || loading) && styles.disabled,
      style
    ]}
    disabled={disabled || loading}
    activeOpacity={0.7}
    {...props}
  >
    {loading ? (
      <ActivityIndicator
        color={variant === 'outline' || variant === 'ghost' ? '#7c3aed' : '#fff'}
      />
    ) : (
      <Text
        style={[
          styles.text,
          variant && (styles as any)['tv_' + variant],
          size && (styles as any)['ts_' + size],
          textStyle
        ]}
      >
        {children}
      </Text>
    )}
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  base: { borderRadius: 12, alignItems: 'center', justifyContent: 'center', flexDirection: 'row' },
  fullWidth: { width: '100%' },
  disabled: { opacity: 0.5 },
  v_primary: { backgroundColor: '#7c3aed' },
  v_secondary: { backgroundColor: '#6b7280' },
  v_outline: { backgroundColor: 'transparent', borderWidth: 2, borderColor: '#7c3aed' },
  v_ghost: { backgroundColor: 'transparent' },
  v_danger: { backgroundColor: '#dc2626' },
  s_sm: { paddingHorizontal: 16, paddingVertical: 8 },
  s_md: { paddingHorizontal: 24, paddingVertical: 12 },
  s_lg: { paddingHorizontal: 32, paddingVertical: 16 },
  text: { fontWeight: '600' },
  tv_primary: { color: '#fff' },
  tv_secondary: { color: '#fff' },
  tv_outline: { color: '#7c3aed' },
  tv_ghost: { color: '#7c3aed' },
  tv_danger: { color: '#fff' },
  ts_sm: { fontSize: 14 },
  ts_md: { fontSize: 16 },
  ts_lg: { fontSize: 18 }
});

export default Button;
