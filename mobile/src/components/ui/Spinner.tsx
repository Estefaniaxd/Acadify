import React from 'react';
import { ActivityIndicator, View, StyleSheet, ViewStyle } from 'react-native';

export interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'secondary' | 'gray';
  style?: ViewStyle;
}

export const Spinner: React.FC<SpinnerProps> = ({ size = 'md', variant = 'primary', style }) => {
  const sizeMap = { sm: 'small' as const, md: 'large' as const, lg: 'large' as const };
  const colorMap = { primary: '#7c3aed', secondary: '#06b6d4', gray: '#6b7280' };
  return (<View style={[styles.cont, style]}><ActivityIndicator size={sizeMap[size]} color={colorMap[variant]} /></View>);
};

const styles = StyleSheet.create({
  cont: { justifyContent: 'center', alignItems: 'center' },
});

export default Spinner;
