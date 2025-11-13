import React from 'react';
import { Switch as RNSwitch, View, Text, StyleSheet, ViewStyle } from 'react-native';

export interface SwitchProps {
  checked: boolean;
  onCheckedChange: (v: boolean) => void;
  label?: string;
  description?: string;
  style?: ViewStyle;
}

export const Switch: React.FC<SwitchProps> = ({ checked, onCheckedChange, label, description, style }) => {
  return (
    <View style={[styles.cont, style]}>
      <View style={styles.txt}>
        {label && <Text style={styles.label}>{label}</Text>}
        {description && <Text style={styles.desc}>{description}</Text>}
      </View>
      <RNSwitch value={checked} onValueChange={onCheckedChange} trackColor={{ false: '#d1d5db', true: '#a78bfa' }} thumbColor={checked ? '#7c3aed' : '#f3f4f6'} />
    </View>
  );
};

const styles = StyleSheet.create({
  cont: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  txt: { flex: 1, marginRight: 12 },
  label: { fontSize: 14, fontWeight: '500', color: '#111827', marginBottom: 2 },
  desc: { fontSize: 12, color: '#6b7280' },
});

export default Switch;
