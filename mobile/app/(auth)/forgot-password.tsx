/**
 * Forgot Password Screen
 * Password recovery with email
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { API, formatApiError } from '@/utils/api';
import { useToast } from '@/components/ui/Toast';
import { Button, Input } from '@/components/ui';

export default function ForgotPasswordScreen() {
  const { toast } = useToast();
  const router = useRouter();

  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const validate = (): string => {
    if (!email) {
      return 'El email es obligatorio';
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return 'Email inválido';
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
      await API.auth.recoverPassword(email);

      setSuccess(true);

      toast({
        title: 'Email enviado',
        description: 'Revisa tu correo para restablecer tu contraseña',
        variant: 'success',
      });
    } catch (err: any) {
      const errorMessage = formatApiError(err);
      setError(errorMessage);

      toast({
        title: 'Error al enviar email',
        description: errorMessage,
        variant: 'danger',
      });
    } finally {
      setLoading(false);
    }
  };

  // Success screen
  if (success) {
    return (
      <SafeAreaView style={styles.successContainer}>
        <View>
          <View style={styles.successIcon}>
            <Ionicons name="mail" size={60} color="white" />
          </View>
          <Text style={styles.successTitle}>
            ¡Revisa tu email!
          </Text>
          <Text style={styles.successText}>
            Hemos enviado un enlace de recuperación a:
          </Text>
          <Text style={styles.emailText}>
            {email}
          </Text>
          <Text style={styles.successHint}>
            Si no recibes el email en unos minutos, revisa tu carpeta de spam
          </Text>
          <Button onPress={() => router.replace('/(auth)/login')}>
            Volver al Login
          </Button>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.flex}
      >
        <ScrollView
          style={styles.flex}
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* Back Button */}
          <TouchableOpacity
            onPress={() => router.back()}
            style={styles.backButton}
          >
            <Ionicons name="arrow-back" size={24} color="#6b7280" />
            <Text style={styles.backText}>Volver</Text>
          </TouchableOpacity>

          {/* Header */}
          <View style={styles.header}>
            <View style={styles.logo}>
              <Ionicons name="key" size={40} color="white" />
            </View>
            <Text style={styles.title}>
              ¿Olvidaste tu contraseña?
            </Text>
            <Text style={styles.subtitle}>
              No te preocupes, te enviaremos un enlace para que puedas restablecerla
            </Text>
          </View>

          {/* Form Card */}
          <View style={styles.card}>
            <View style={styles.inputGroup}>
              <Input
                label="Correo electrónico"
                value={email}
                onChangeText={setEmail}
                placeholder="tu.email@ejemplo.com"
                keyboardType="email-address"
                autoCapitalize="none"
                error={error}
                helperText="Ingresa el email asociado a tu cuenta"
              />
            </View>

            {/* Info Box */}
            <View style={styles.infoBox}>
              <View style={styles.infoContent}>
                <Ionicons name="information-circle" size={20} color="#3b82f6" />
                <Text style={styles.infoText}>
                  Recibirás un enlace en tu correo para restablecer tu contraseña. El enlace será
                  válido por 1 hora.
                </Text>
              </View>
            </View>

            {/* Submit Button */}
            <Button
              onPress={handleSubmit}
              loading={loading}
              disabled={loading}
              style={styles.button}
            >
              {loading ? 'Enviando...' : 'Enviar enlace de recuperación'}
            </Button>

            {/* Login Link */}
            <View style={styles.loginLink}>
              <Text style={styles.loginText}>
                ¿Recordaste tu contraseña?{' '}
              </Text>
              <TouchableOpacity onPress={() => router.push('/(auth)/login')}>
                <Text style={styles.loginLinkText}>
                  Inicia sesión
                </Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Footer Help */}
          <View style={styles.helpBox}>
            <Text style={styles.helpTitle}>
              ¿Necesitas ayuda?
            </Text>
            <Text style={styles.helpText}>
              Si tienes problemas para recuperar tu cuenta, contacta con soporte:
            </Text>
            <Text style={styles.helpEmail}>
              soporte@acadify.com
            </Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  // Success screen
  successContainer: { flex: 1, backgroundColor: '#dbeafe', alignItems: 'center', justifyContent: 'center', padding: 24 },
  successIcon: { width: 96, height: 96, borderRadius: 48, backgroundColor: '#3b82f6', alignItems: 'center', justifyContent: 'center', marginBottom: 24 },
  successTitle: { fontSize: 30, fontWeight: '900', color: '#111827', marginBottom: 16, textAlign: 'center' },
  successText: { fontSize: 14, color: '#6b7280', textAlign: 'center', marginBottom: 8 },
  emailText: { fontSize: 18, fontWeight: 'bold', color: '#3b82f6', marginBottom: 32, textAlign: 'center' },
  successHint: { fontSize: 12, color: '#9ca3af', textAlign: 'center', marginBottom: 32 },
  
  // Main screen
  safeArea: { flex: 1, backgroundColor: '#dbeafe' },
  flex: { flex: 1 },
  scrollContent: { padding: 16 },
  backButton: { flexDirection: 'row', alignItems: 'center', marginBottom: 16 },
  backText: { marginLeft: 8, fontSize: 16, color: '#374151', fontWeight: '600' },
  header: { alignItems: 'center', marginBottom: 32, marginTop: 32 },
  logo: { width: 80, height: 80, borderRadius: 24, backgroundColor: '#3b82f6', alignItems: 'center', justifyContent: 'center', marginBottom: 16, shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.2, shadowRadius: 8, elevation: 8 },
  title: { fontSize: 30, fontWeight: '900', color: '#111827', marginBottom: 8, textAlign: 'center' },
  subtitle: { fontSize: 14, color: '#6b7280', textAlign: 'center', paddingHorizontal: 16 },
  card: { backgroundColor: '#ffffff', borderRadius: 24, padding: 24, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 8, elevation: 5, borderWidth: 1, borderColor: '#bfdbfe' },
  inputGroup: { marginBottom: 24 },
  infoBox: { padding: 16, borderRadius: 16, backgroundColor: '#eff6ff', borderWidth: 1, borderColor: '#bfdbfe', marginBottom: 24 },
  infoContent: { flexDirection: 'row', alignItems: 'flex-start' },
  infoText: { marginLeft: 8, fontSize: 14, color: '#1e40af', flex: 1 },
  button: { marginBottom: 24 },
  loginLink: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center' },
  loginText: { fontSize: 14, color: '#6b7280' },
  loginLinkText: { fontSize: 14, fontWeight: '700', color: '#3b82f6' },
  helpBox: { marginTop: 32, padding: 16, borderRadius: 16, backgroundColor: 'rgba(255,255,255,0.5)', borderWidth: 1, borderColor: '#e5e7eb' },
  helpTitle: { fontSize: 14, fontWeight: '600', color: '#111827', marginBottom: 8 },
  helpText: { fontSize: 12, color: '#6b7280', marginBottom: 8 },
  helpEmail: { fontSize: 12, color: '#3b82f6', fontWeight: '600' },
});
