import React from 'react';
import { View, Text, StyleSheet, ViewStyle, TextStyle } from 'react-native';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  dot?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'default', size = 'md', dot = false, style, textStyle }) => {
  if (dot) return <View style={[styles.dot, styles[`d_${variant}`], styles[`ds_${size}`], style]} />;
  return (<View style={[styles.base, styles[`v_${variant}`], styles[`s_${size}`], style]}><Text style={[styles.txt, styles[`tv_${variant}`], styles[`ts_${size}`], textStyle]}>{children}</Text></View>);
};

const styles = StyleSheet.create({
  base: { borderRadius: 12, alignSelf: 'flex-start', flexDirection: 'row', alignItems: 'center' },
  v_default: { backgroundColor: '#f3f4f6' },
  v_primary: { backgroundColor: '#7c3aed' },
  v_secondary: { backgroundColor: '#06b6d4' },
  v_success: { backgroundColor: '#10b981' },
  v_warning: { backgroundColor: '#f59e0b' },
  v_danger: { backgroundColor: '#dc2626' },
  v_outline: { backgroundColor: 'transparent', borderWidth: 1, borderColor: '#d1d5db' },
  s_sm: { paddingHorizontal: 6, paddingVertical: 2 },
  s_md: { paddingHorizontal: 8, paddingVertical: 4 },
  s_lg: { paddingHorizontal: 12, paddingVertical: 6 },
  txt: { fontWeight: '500' },
  tv_default: { color: '#374151' },
  tv_primary: { color: '#fff' },
  tv_secondary: { color: '#fff' },
  tv_success: { color: '#fff' },
  tv_warning: { color: '#fff' },
  tv_danger: { color: '#fff' },
  tv_outline: { color: '#374151' },
  ts_sm: { fontSize: 11 },
  ts_md: { fontSize: 12 },
  ts_lg: { fontSize: 14 },
  dot: { borderRadius: 999 },
  d_default: { backgroundColor: '#9ca3af' },
  d_primary: { backgroundColor: '#7c3aed' },
  d_secondary: { backgroundColor: '#06b6d4' },
  d_success: { backgroundColor: '#10b981' },
  d_warning: { backgroundColor: '#f59e0b' },
  d_danger: { backgroundColor: '#dc2626' },
  d_outline: { backgroundColor: '#d1d5db' },
  ds_sm: { width: 6, height: 6 },
  ds_md: { width: 8, height: 8 },
  ds_lg: { width: 10, height: 10 },
});

export default Badge;
