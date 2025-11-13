/**
 * Register Screen
 * Multi-step registration form with validation
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
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { API, formatApiError } from '@/utils/api';
import { useToast } from '@/components/ui/Toast';
import { Button, Input, Card } from '@/components/ui';

interface FormData {
  rol: string;
  email: string;
  nombres: string;
  apellidos: string;
  tipoDocumento: string;
  numeroDocumento: string;
  username: string;
  password: string;
  confirm: string;
}

interface ValidationErrors {
  [key: string]: string;
}

const DOCUMENT_TYPES = [
  { value: 'cc', label: 'Cédula de ciudadanía (CC)' },
  { value: 'ti', label: 'Tarjeta de identidad (TI)' },
  { value: 'ce', label: 'Cédula de extranjería (CE)' },
];

export default function RegisterScreen() {
  const { toast } = useToast();
  const router = useRouter();

  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const [formData, setFormData] = useState<FormData>({
    rol: 'estudiante',
    email: '',
    nombres: '',
    apellidos: '',
    tipoDocumento: '',
    numeroDocumento: '',
    username: '',
    password: '',
    confirm: '',
  });

  const [errors, setErrors] = useState<ValidationErrors>({});
  const [globalError, setGlobalError] = useState('');

  const totalSteps = 3;

  /**
   * Validate individual field
   */
  const validateField = (field: string, value: string): string => {
    switch (field) {
      case 'nombres':
        return value.length < 2 ? 'El nombre debe tener al menos 2 caracteres' : '';
      case 'apellidos':
        return value.length < 2 ? 'Los apellidos deben tener al menos 2 caracteres' : '';
      case 'email':
        return !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? 'Email inválido' : '';
      case 'username':
        return value.length < 3 ? 'El usuario debe tener al menos 3 caracteres' : '';
      case 'numeroDocumento':
        return value.length < 6 ? 'Número de documento inválido' : '';
      case 'password':
        return value.length < 6 ? 'La contraseña debe tener al menos 6 caracteres' : '';
      case 'confirm':
        return value !== formData.password ? 'Las contraseñas no coinciden' : '';
      case 'tipoDocumento':
        return !value ? 'Selecciona un tipo de documento' : '';
      default:
        return '';
    }
  };

  /**
   * Update form field with validation
   */
  const updateField = (field: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));

    if (value.trim()) {
      const error = validateField(field, value);
      setErrors((prev) => ({ ...prev, [field]: error }));
    } else {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }

    // Validate confirm when password changes
    if (field === 'password' && formData.confirm) {
      const confirmError = validateField('confirm', formData.confirm);
      setErrors((prev) => ({ ...prev, confirm: confirmError }));
    }
  };

  /**
   * Validate current step
   */
  const validateStep = (stepNumber: number): boolean => {
    const stepErrors: ValidationErrors = {};

    switch (stepNumber) {
      case 1:
        if (!formData.nombres) stepErrors.nombres = 'Los nombres son obligatorios';
        else stepErrors.nombres = validateField('nombres', formData.nombres);

        if (!formData.apellidos) stepErrors.apellidos = 'Los apellidos son obligatorios';
        else stepErrors.apellidos = validateField('apellidos', formData.apellidos);

        if (!formData.tipoDocumento)
          stepErrors.tipoDocumento = 'Selecciona un tipo de documento';
        if (!formData.numeroDocumento)
          stepErrors.numeroDocumento = 'El número de documento es obligatorio';
        else
          stepErrors.numeroDocumento = validateField(
            'numeroDocumento',
            formData.numeroDocumento
          );
        break;

      case 2:
        if (!formData.username) stepErrors.username = 'El usuario es obligatorio';
        else stepErrors.username = validateField('username', formData.username);

        if (!formData.email) stepErrors.email = 'El email es obligatorio';
        else stepErrors.email = validateField('email', formData.email);
        break;

      case 3:
        if (!formData.password) stepErrors.password = 'La contraseña es obligatoria';
        else stepErrors.password = validateField('password', formData.password);

        if (!formData.confirm) stepErrors.confirm = 'Confirma tu contraseña';
        else stepErrors.confirm = validateField('confirm', formData.confirm);
        break;
    }

    setErrors(stepErrors);
    return Object.values(stepErrors).every((error) => !error);
  };

  /**
   * Go to next step
   */
  const nextStep = () => {
    if (validateStep(step) && step < totalSteps) {
      setStep(step + 1);
    }
  };

  /**
   * Go to previous step
   */
  const prevStep = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  /**
   * Submit registration
   */
  const handleSubmit = async () => {
    if (!validateStep(3)) return;

    setGlobalError('');
    setLoading(true);

    try {
      const payload = {
        username: formData.username,
        nombres: formData.nombres,
        apellidos: formData.apellidos,
        tipo_documento: formData.tipoDocumento,
        numero_documento: formData.numeroDocumento,
        password: formData.password,
        rol: formData.rol,
        correo_institucional: formData.email,
      };

      await API.auth.register(payload);

      setSuccess(true);

      toast({
        title: '¡Registro exitoso!',
        description: 'Tu cuenta ha sido creada correctamente',
        variant: 'success',
      });

      setTimeout(() => {
        router.replace('/(auth)/login');
      }, 3000);
    } catch (err: any) {
      const errorMessage = formatApiError(err);
      setGlobalError(errorMessage);

      toast({
        title: 'Error al registrar',
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
            <Ionicons name="checkmark-circle" size={60} color="white" />
          </View>
          <Text style={styles.successTitle}>
            ¡Registro exitoso!
          </Text>
          <Text style={styles.successText}>
            Tu cuenta ha sido creada correctamente. Te redirigiremos al login en unos segundos.
          </Text>
          <ActivityIndicator size="large" color="#10b981" style={styles.spinner} />
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
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* Header */}
          <View style={styles.header}>
            <View style={styles.logo}>
              <Ionicons name="school" size={40} color="white" />
            </View>
            <Text style={styles.title}>
              Únete a Acadify
            </Text>
            <Text style={styles.subtitle}>
              Crea tu cuenta y comienza tu aventura de aprendizaje
            </Text>
          </View>

          {/* Progress Indicator */}
          <View style={styles.progressContainer}>
            {[1, 2, 3].map((stepNumber) => (
              <View key={stepNumber} style={styles.progressRow}>
                <View
                  style={[
                    styles.progressStep,
                    stepNumber === step && styles.progressStepActive,
                    stepNumber < step && styles.progressStepCompleted,
                  ]}
                >
                  {stepNumber < step ? (
                    <Ionicons name="checkmark" size={20} color="white" />
                  ) : (
                    <Text style={styles.progressStepText}>{stepNumber}</Text>
                  )}
                </View>
                {stepNumber < totalSteps && (
                  <View
                    style={[
                      styles.progressLine,
                      stepNumber < step && styles.progressLineActive,
                    ]}
                  />
                )}
              </View>
            ))}
          </View>

          <Text style={styles.stepText}>
            Paso {step} de {totalSteps}
          </Text>

          {/* Form Card */}
          <View style={styles.card}>
            {/* Step 1: Personal Info */}
            {step === 1 && (
              <View>
                <View style={styles.stepHeader}>
                  <Ionicons name="person-outline" size={32} color="#10b981" />
                  <Text style={styles.stepTitle}>
                    Información Personal
                  </Text>
                  <Text style={styles.stepSubtitle}>
                    Cuéntanos un poco sobre ti
                  </Text>
                </View>

                <View style={styles.formGroup}>
                  <Input
                    label="Nombres"
                    value={formData.nombres}
                    onChangeText={(v: string) => updateField('nombres', v)}
                    placeholder="Ingresa tus nombres"
                    error={errors.nombres}
                  />
                  <Input
                    label="Apellidos"
                    value={formData.apellidos}
                    onChangeText={(v: string) => updateField('apellidos', v)}
                    placeholder="Ingresa tus apellidos"
                    error={errors.apellidos}
                  />

                  {/* Document Type Selector */}
                  <View>
                    <Text className="text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
                      Tipo de documento
                    </Text>
                    <View className="gap-2">
                      {DOCUMENT_TYPES.map((docType) => (
                        <TouchableOpacity
                          key={docType.value}
                          onPress={() => updateField('tipoDocumento', docType.value)}
                          className={`p-4 rounded-2xl border-2 ${
                            formData.tipoDocumento === docType.value
                              ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20'
                              : 'border-gray-200 dark:border-gray-600'
                          }`}
                        >
                          <Text
                            className={`font-semibold ${
                              formData.tipoDocumento === docType.value
                                ? 'text-emerald-700 dark:text-emerald-400'
                                : 'text-gray-700 dark:text-gray-300'
                            }`}
                          >
                            {docType.label}
                          </Text>
                        </TouchableOpacity>
                      ))}
                    </View>
                    {errors.tipoDocumento && (
                      <Text className="text-xs text-red-600 dark:text-red-400 mt-1">
                        {errors.tipoDocumento}
                      </Text>
                    )}
                  </View>

                  <Input
                    label="Número de documento"
                    value={formData.numeroDocumento}
                    onChangeText={(v: string) => updateField('numeroDocumento', v)}
                    placeholder="Número de identificación"
                    keyboardType="numeric"
                    error={errors.numeroDocumento}
                  />

                  {/* Role Selector */}
                  <View>
                    <Text className="text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
                      ¿Cuál es tu rol?
                    </Text>
                    <View className="flex-row gap-3">
                      {[
                        { value: 'estudiante', label: 'Estudiante', icon: 'school' },
                        { value: 'docente', label: 'Docente', icon: 'book' },
                      ].map((rol) => (
                        <TouchableOpacity
                          key={rol.value}
                          onPress={() => updateField('rol', rol.value)}
                          className={`flex-1 p-4 rounded-2xl border-2 items-center ${
                            formData.rol === rol.value
                              ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20'
                              : 'border-gray-200 dark:border-gray-600'
                          }`}
                        >
                          <View className="w-12 h-12 rounded-xl bg-emerald-600 items-center justify-center mb-2">
                            <Ionicons name={rol.icon as any} size={24} color="white" />
                          </View>
                          <Text
                            className={`font-semibold text-sm ${
                              formData.rol === rol.value
                                ? 'text-emerald-700 dark:text-emerald-400'
                                : 'text-gray-700 dark:text-gray-300'
                            }`}
                          >
                            {rol.label}
                          </Text>
                        </TouchableOpacity>
                      ))}
                    </View>
                  </View>
                </View>
              </View>
            )}

            {/* Step 2: Credentials */}
            {step === 2 && (
              <View>
                <View className="items-center mb-6">
                  <Ionicons name="mail-outline" size={32} color="#10b981" />
                  <Text className="text-xl font-bold text-gray-900 dark:text-white mt-2 mb-1">
                    Credenciales de Acceso
                  </Text>
                  <Text className="text-sm text-gray-600 dark:text-gray-300 text-center">
                    Define cómo accederás a tu cuenta
                  </Text>
                </View>

                <View className="gap-4">
                  <Input
                    label="Nombre de usuario"
                    value={formData.username}
                    onChangeText={(v: string) => updateField('username', v)}
                    placeholder="Elige un nombre de usuario único"
                    autoCapitalize="none"
                    error={errors.username}
                  />
                  <Input
                    label="Correo electrónico"
                    value={formData.email}
                    onChangeText={(v: string) => updateField('email', v)}
                    placeholder="tu.email@ejemplo.com"
                    keyboardType="email-address"
                    autoCapitalize="none"
                    error={errors.email}
                  />
                </View>
              </View>
            )}

            {/* Step 3: Password */}
            {step === 3 && (
              <View>
                <View className="items-center mb-6">
                  <Ionicons name="shield-checkmark-outline" size={32} color="#10b981" />
                  <Text className="text-xl font-bold text-gray-900 dark:text-white mt-2 mb-1">
                    Protege tu Cuenta
                  </Text>
                  <Text className="text-sm text-gray-600 dark:text-gray-300 text-center">
                    Crea una contraseña segura para tu cuenta
                  </Text>
                </View>

                <View className="gap-4">
                  <Input
                    label="Contraseña"
                    value={formData.password}
                    onChangeText={(v: string) => updateField('password', v)}
                    placeholder="Crea una contraseña segura"
                    secureTextEntry
                    error={errors.password}
                  />
                  <Input
                    label="Confirmar contraseña"
                    value={formData.confirm}
                    onChangeText={(v: string) => updateField('confirm', v)}
                    placeholder="Confirma tu contraseña"
                    secureTextEntry
                    error={errors.confirm}
                  />

                  <View className="p-4 rounded-2xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                    <Text className="text-xs text-gray-600 dark:text-gray-400">
                      Al crear una cuenta, aceptas nuestros Términos de Servicio y Política de
                      Privacidad
                    </Text>
                  </View>
                </View>
              </View>
            )}

            {/* Global Error */}
            {globalError && (
              <View
                className="mt-4 p-4 rounded-2xl bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800"
              >
                <View className="flex-row items-center">
                  <Ionicons name="alert-circle" size={20} color="#dc2626" />
                  <Text className="ml-2 text-sm text-red-600 dark:text-red-400 flex-1">
                    {globalError}
                  </Text>
                </View>
              </View>
            )}

            {/* Navigation Buttons */}
            <View className="flex-row items-center justify-between mt-6">
              {step > 1 ? (
                <Button variant="ghost" size="md" onPress={prevStep}>
                  <View className="flex-row items-center">
                    <Ionicons name="arrow-back" size={16} color="#6b7280" />
                    <Text className="ml-2 text-gray-700 dark:text-gray-300 font-semibold">
                      Anterior
                    </Text>
                  </View>
                </Button>
              ) : (
                <View />
              )}

              {step < totalSteps ? (
                <Button variant="primary" size="md" onPress={nextStep}>
                  <View className="flex-row items-center">
                    <Text className="mr-2 text-white font-semibold">Siguiente</Text>
                    <Ionicons name="arrow-forward" size={16} color="white" />
                  </View>
                </Button>
              ) : (
                <Button
                  variant="primary"
                  size="md"
                  onPress={handleSubmit}
                  loading={loading}
                  disabled={loading}
                >
                  Crear Cuenta
                </Button>
              )}
            </View>

            {/* Login Link */}
            <View style={styles.loginLink}>
              <Text style={styles.loginText}>
                ¿Ya tienes cuenta?{' '}
              </Text>
              <TouchableOpacity onPress={() => router.push('/(auth)/login')}>
                <Text style={styles.loginLinkText}>
                  Inicia sesión aquí
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  // Success screen styles
  successContainer: { flex: 1, backgroundColor: '#d1fae5', alignItems: 'center', justifyContent: 'center', padding: 24 },
  successIcon: { width: 96, height: 96, borderRadius: 48, backgroundColor: '#10b981', alignItems: 'center', justifyContent: 'center', marginBottom: 24 },
  successTitle: { fontSize: 30, fontWeight: '900', color: '#111827', marginBottom: 16, textAlign: 'center' },
  successText: { fontSize: 14, color: '#6b7280', textAlign: 'center', marginBottom: 32 },
  spinner: { marginTop: 16 },
  
  // Main screen styles
  safeArea: { flex: 1, backgroundColor: '#d1fae5' },
  flex: { flex: 1 },
  header: { alignItems: 'center', marginBottom: 24, marginTop: 16, paddingHorizontal: 16 },
  logo: { width: 80, height: 80, borderRadius: 24, backgroundColor: '#10b981', alignItems: 'center', justifyContent: 'center', marginBottom: 16, shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.2, shadowRadius: 8, elevation: 8 },
  title: { fontSize: 30, fontWeight: '900', color: '#111827', marginBottom: 8, textAlign: 'center' },
  subtitle: { fontSize: 14, color: '#6b7280', textAlign: 'center' },
  
  // Progress indicator
  progressContainer: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginBottom: 24 },
  progressRow: { flexDirection: 'row', alignItems: 'center' },
  progressStep: { width: 40, height: 40, borderRadius: 20, alignItems: 'center', justifyContent: 'center', backgroundColor: '#d1d5db' },
  progressStepActive: { backgroundColor: '#10b981' },
  progressStepCompleted: { backgroundColor: '#34d399' },
  progressStepText: { fontSize: 14, fontWeight: 'bold', color: '#fff' },
  progressLine: { width: 48, height: 4, marginHorizontal: 8, backgroundColor: '#d1d5db' },
  progressLineActive: { backgroundColor: '#10b981' },
  stepText: { textAlign: 'center', fontSize: 14, color: '#9ca3af', marginBottom: 24 },
  
  // Card and form
  card: { backgroundColor: '#ffffff', borderRadius: 24, padding: 24, marginHorizontal: 16, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 8, elevation: 5, borderWidth: 1, borderColor: '#a7f3d0', marginBottom: 16 },
  stepHeader: { alignItems: 'center', marginBottom: 24 },
  stepTitle: { fontSize: 20, fontWeight: 'bold', color: '#111827', marginTop: 8, marginBottom: 4 },
  stepSubtitle: { fontSize: 14, color: '#6b7280', textAlign: 'center' },
  formGroup: { gap: 16 },
  
  // Login link
  loginLink: { marginTop: 24, flexDirection: 'row', alignItems: 'center', justifyContent: 'center' },
  loginText: { fontSize: 14, color: '#6b7280' },
  loginLinkText: { fontSize: 14, fontWeight: '700', color: '#10b981' },
});
