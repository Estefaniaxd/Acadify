/**
 * Login Screen
 * User authentication with email/username and password
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  TouchableOpacity,
  ActivityIndicator,
  StyleSheet,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '@/context/AuthContext';
import { API, formatApiError } from '@/utils/api';
import { useToast } from '@/components/ui/Toast';
import { Button, Input, Checkbox } from '@/components/ui';

export default function LoginScreen() {
  const { login } = useAuth();
  const { toast } = useToast();
  const router = useRouter();

  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(false);
  const [accepted, setAccepted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // OTP State
  const [otpRequired, setOtpRequired] = useState(false);
  const [otp, setOtp] = useState('');
  const [otpMessage, setOtpMessage] = useState('');

  const validate = (): string => {
    if (!identifier || !password) {
      return 'Todos los campos son obligatorios';
    }
    if (!accepted) {
      return 'Debes aceptar el tratamiento de datos';
    }
    if (otpRequired && !otp) {
      return 'Ingresa el código OTP';
    }
    return '';
  };

  const handleSubmit = async () => {
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setError('');
    setLoading(true);

    try {
      const payload: any = {
        identifier,
        password,
        remember,
      };

      if (otpRequired && otp) {
        payload.otp_code = otp;
      }

      const response = await API.auth.login(payload);

      // Success - save tokens and navigate
      if (response.data.access_token && response.data.refresh_token) {
        await login(response.data.access_token, response.data.refresh_token);

        toast({
          title: '¡Bienvenido de vuelta!',
          description: 'Sesión iniciada correctamente',
          variant: 'success',
        });

        // Navigate to app
        router.replace('/(app)');
      } else if (response.data.status === 'otp_required') {
        // OTP required
        setOtpRequired(true);
        setOtpMessage(response.data.message || 'Se requiere código OTP');
      }
    } catch (err: any) {
      const errorMessage = formatApiError(err);
      setError(errorMessage);
      
      toast({
        title: 'Error al iniciar sesión',
        description: errorMessage,
        variant: 'danger',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.flex}
      >
        <ScrollView
          style={styles.flex}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* Header */}
          <View style={styles.header}>
            <View style={styles.logo}>
              <Ionicons name="sparkles" size={40} color="white" />
            </View>
            <Text style={styles.title}>
              ¡Bienvenido de vuelta!
            </Text>
            <Text style={styles.subtitle}>
              Inicia sesión para continuar tu aventura de aprendizaje
            </Text>
          </View>

          {/* Form Card */}
          <View style={styles.card}>
            {/* Identifier Input */}
            <View style={styles.inputGroup}>
              <Input
                label="Usuario o Email"
                value={identifier}
                onChangeText={setIdentifier}
                placeholder="Ingresa tu usuario o email"
                autoCapitalize="none"
                keyboardType="email-address"
                error={error && !identifier ? 'Campo requerido' : undefined}
              />
            </View>

            {/* Password Input */}
            <View style={styles.inputGroup}>
              <Input
                label="Contraseña"
                value={password}
                onChangeText={setPassword}
                placeholder="Ingresa tu contraseña"
                secureTextEntry={!showPassword}
                error={error && !password ? 'Campo requerido' : undefined}
              />
            </View>

            {/* OTP Input (if required) */}
            {otpRequired && (
              <View style={styles.inputGroup}>
                <Input
                  label="Código OTP"
                  value={otp}
                  onChangeText={setOtp}
                  placeholder="Código de 6 dígitos"
                  keyboardType="number-pad"
                  maxLength={6}
                  helperText={otpMessage}
                />
              </View>
            )}

            {/* Options */}
            <View style={styles.options}>
              <Checkbox
                checked={remember}
                onCheckedChange={setRemember}
                label="Recordarme"
              />
              <TouchableOpacity onPress={() => router.push('/(auth)/forgot-password')}>
                <Text style={styles.linkText}>
                  ¿Olvidaste tu contraseña?
                </Text>
              </TouchableOpacity>
            </View>

            {/* Acceptance Checkbox */}
            <View style={styles.inputGroup}>
              <Checkbox
                checked={accepted}
                onCheckedChange={setAccepted}
                label="Acepto el tratamiento de datos"
              />
            </View>

            {/* Error Message */}
            {error && (
              <View style={styles.errorBox}>
                <View style={styles.errorContent}>
                  <Ionicons name="alert-circle" size={20} color="#dc2626" />
                  <Text style={styles.errorText}>
                    {error}
                  </Text>
                </View>
              </View>
            )}

            {/* Submit Button */}
            <Button
              onPress={handleSubmit}
              loading={loading}
              disabled={loading}
              style={styles.button}
            >
              {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
            </Button>

            {/* Register Link */}
            <View style={styles.registerContainer}>
              <Text style={styles.registerText}>
                ¿No tienes cuenta?{' '}
              </Text>
              <TouchableOpacity onPress={() => router.push('/(auth)/register')}>
                <Text style={styles.registerLink}>
                  Regístrate gratis
                </Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Footer */}
          <View style={styles.footer}>
            <Text style={styles.footerText}>
              Al iniciar sesión, aceptas nuestros Términos de Servicio y Política de Privacidad
            </Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#f5f3ff' },
  flex: { flex: 1 },
  header: { alignItems: 'center', marginBottom: 32, marginTop: 32, paddingHorizontal: 16 },
  logo: { width: 80, height: 80, borderRadius: 24, backgroundColor: '#7c3aed', alignItems: 'center', justifyContent: 'center', marginBottom: 16, shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.2, shadowRadius: 8, elevation: 8 },
  title: { fontSize: 30, fontWeight: '900', color: '#111827', marginBottom: 8, textAlign: 'center' },
  subtitle: { fontSize: 14, color: '#6b7280', textAlign: 'center' },
  card: { backgroundColor: '#ffffff', borderRadius: 24, padding: 24, marginHorizontal: 16, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 8, elevation: 5, borderWidth: 1, borderColor: '#e9d5ff' },
  inputGroup: { marginBottom: 16 },
  options: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 },
  linkText: { fontSize: 14, fontWeight: '600', color: '#7c3aed' },
  errorBox: { marginBottom: 16, padding: 16, borderRadius: 16, backgroundColor: '#fef2f2', borderWidth: 1, borderColor: '#fecaca' },
  errorContent: { flexDirection: 'row', alignItems: 'center' },
  errorText: { marginLeft: 8, fontSize: 14, color: '#dc2626', flex: 1 },
  button: { marginTop: 8 },
  registerContainer: { marginTop: 24, flexDirection: 'row', alignItems: 'center', justifyContent: 'center' },
  registerText: { fontSize: 14, color: '#6b7280' },
  registerLink: { fontSize: 14, fontWeight: '700', color: '#7c3aed' },
  footer: { marginTop: 32, alignItems: 'center', paddingHorizontal: 32, marginBottom: 16 },
  footerText: { fontSize: 12, color: '#9ca3af', textAlign: 'center' },
});
