import React from 'react';
import { View, TextInput, Text, TextInputProps, StyleSheet, ViewStyle, TextStyle } from 'react-native';

export interface InputProps extends Omit<TextInputProps, 'style'> {
  label?: string;
  error?: string;
  helperText?: string;
  containerStyle?: ViewStyle;
  inputStyle?: TextStyle;
}

export const Input: React.FC<InputProps> = ({ label, error, helperText, containerStyle, inputStyle, ...props }) => {
  return (
    <View style={[styles.container, containerStyle]}>
      {label && <Text style={styles.label}>{label}</Text>}
      <TextInput style={[styles.input, error && styles.inputError, inputStyle]} placeholderTextColor="#9ca3af" {...props} />
      {error && <Text style={styles.error}>{error}</Text>}
      {helperText && !error && <Text style={styles.helper}>{helperText}</Text>}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { marginBottom: 16 },
  label: { fontSize: 14, fontWeight: '500', color: '#374151', marginBottom: 6 },
  input: { height: 44, borderWidth: 1, borderColor: '#d1d5db', borderRadius: 8, paddingHorizontal: 12, fontSize: 16, backgroundColor: '#fff', color: '#111827' },
  inputError: { borderColor: '#dc2626' },
  error: { fontSize: 12, color: '#dc2626', marginTop: 4 },
  helper: { fontSize: 12, color: '#6b7280', marginTop: 4 },
});

export default Input;
