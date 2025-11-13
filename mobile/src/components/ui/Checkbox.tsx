import React from 'react';
import { TouchableOpacity, View, Text, StyleSheet } from 'react-native';

export interface CheckboxProps {
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  label?: string;
  style?: any;
}

export const Checkbox: React.FC<CheckboxProps> = ({ checked, onCheckedChange, label, style }) => (
  <TouchableOpacity onPress={() => onCheckedChange(!checked)} style={[styles.container, style]}>
    <View style={[styles.box, checked && styles.boxChecked]}>
      {checked && <Text style={styles.check}>✓</Text>}
    </View>
    {label && <Text style={styles.label}>{label}</Text>}
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  container: { flexDirection: 'row', alignItems: 'center' },
  box: { width: 20, height: 20, borderRadius: 4, borderWidth: 2, borderColor: '#d1d5db', backgroundColor: 'transparent', alignItems: 'center', justifyContent: 'center', marginRight: 12 },
  boxChecked: { borderColor: '#7c3aed', backgroundColor: '#7c3aed' },
  check: { color: '#fff', fontSize: 14, fontWeight: 'bold' },
  label: { fontSize: 14, color: '#111827' },
});

export default Checkbox;
