/**
 * Auth Layout
 * Stack navigation for authentication screens (login, register, forgot-password)
 */

import { Stack } from 'expo-router';

export default function AuthLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        animation: 'slide_from_right',
        contentStyle: {
          backgroundColor: 'transparent',
        },
      }}
    >
      <Stack.Screen
        name="login"
        options={{
          title: 'Iniciar Sesión',
        }}
      />
      <Stack.Screen
        name="register"
        options={{
          title: 'Registro',
        }}
      />
      <Stack.Screen
        name="forgot-password"
        options={{
          title: 'Recuperar Contraseña',
          presentation: 'modal',
        }}
      />
    </Stack>
  );
}
