import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';

export interface ProgressProps {
  value: number;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  style?: ViewStyle;
}

export const Progress: React.FC<ProgressProps> = ({ value, variant = 'primary', size = 'md', style }) => {
  const clampedValue = Math.min(Math.max(value, 0), 100);
  return (
    <View style={[styles.cont, styles[`s_${size}`], style]}>
      <View style={[styles.fill, styles[`v_${variant}`], { width: `${clampedValue}%` }]} />
    </View>
  );
};

const styles = StyleSheet.create({
  cont: { width: '100%', backgroundColor: '#e5e7eb', borderRadius: 999, overflow: 'hidden' },
  s_sm: { height: 4 },
  s_md: { height: 8 },
  s_lg: { height: 12 },
  fill: { height: '100%', borderRadius: 999 },
  v_primary: { backgroundColor: '#7c3aed' },
  v_secondary: { backgroundColor: '#06b6d4' },
  v_success: { backgroundColor: '#10b981' },
  v_warning: { backgroundColor: '#f59e0b' },
  v_danger: { backgroundColor: '#dc2626' },
});

export default Progress;
