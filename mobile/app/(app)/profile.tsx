/**
 * Profile Screen
 * User profile with settings and logout
 */

import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '@/context/AuthContext';
import { Card, Badge, Avatar, Button } from '@/components/ui';
import { getUserDisplayName, getUserInitials } from '@/utils/auth';

export default function ProfileScreen() {
  const { user, logout } = useAuth();
  const router = useRouter();

  const userDisplayName = getUserDisplayName(user);
  const userInitials = getUserInitials(user);

  const handleLogout = () => {
    Alert.alert(
      'Cerrar Sesión',
      '¿Estás seguro que deseas cerrar sesión?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Cerrar Sesión',
          style: 'destructive',
          onPress: async () => {
            await logout();
          },
        },
      ],
      { cancelable: true }
    );
  };

  interface MenuItem {
    icon: string;
    label: string;
    onPress: () => void;
    badge?: string;
    rightText?: string;
    hasSwitch?: boolean;
  }

  const menuSections: { title: string; items: MenuItem[] }[] = [
    {
      title: 'Mi Cuenta',
      items: [
        {
          icon: 'person-outline',
          label: 'Editar Perfil',
          onPress: () => console.log('Edit profile'),
        },
        {
          icon: 'card-outline',
          label: 'Información Personal',
          onPress: () => console.log('Personal info'),
        },
        {
          icon: 'shield-checkmark-outline',
          label: 'Seguridad',
          onPress: () => console.log('Security'),
        },
      ],
    },
    {
      title: 'Gamificación',
      items: [
        {
          icon: 'trophy-outline',
          label: 'Mis Logros',
          badge: '12',
          onPress: () => console.log('Achievements'),
        },
        {
          icon: 'ribbon-outline',
          label: 'Insignias',
          badge: '8',
          onPress: () => console.log('Badges'),
        },
        {
          icon: 'stats-chart-outline',
          label: 'Ranking',
          onPress: () => console.log('Ranking'),
        },
      ],
    },
    {
      title: 'Configuración',
      items: [
        {
          icon: 'notifications-outline',
          label: 'Notificaciones',
          onPress: () => console.log('Notifications'),
        },
        {
          icon: 'moon-outline',
          label: 'Tema Oscuro',
          onPress: () => console.log('Dark mode'),
          hasSwitch: true,
        },
        {
          icon: 'language-outline',
          label: 'Idioma',
          onPress: () => console.log('Language'),
          rightText: 'Español',
        },
      ],
    },
    {
      title: 'Soporte',
      items: [
        {
          icon: 'help-circle-outline',
          label: 'Centro de Ayuda',
          onPress: () => console.log('Help'),
        },
        {
          icon: 'document-text-outline',
          label: 'Términos y Condiciones',
          onPress: () => console.log('Terms'),
        },
        {
          icon: 'shield-outline',
          label: 'Política de Privacidad',
          onPress: () => console.log('Privacy'),
        },
      ],
    },
  ];

  return (
    <SafeAreaView className="flex-1 bg-gray-50 dark:bg-neutral-950">
      <ScrollView
        className="flex-1"
        showsVerticalScrollIndicator={false}
      >
        {/* Profile Header */}
        <View>
          <Card variant="elevated" padding="lg" className="mb-6">
            <View className="items-center">
              <Avatar alt={userDisplayName} size="2xl" />
              <Text className="text-2xl font-black text-gray-900 dark:text-white mt-4">
                {userDisplayName}
              </Text>
              <Text className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                {user?.email}
              </Text>
              <Badge variant="primary">{user?.role || 'Estudiante'}</Badge>

              {/* Stats */}
              <View className="flex-row items-center justify-around w-full mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                <View className="items-center">
                  <Text className="text-2xl font-bold text-gray-900 dark:text-white">4</Text>
                  <Text className="text-xs text-gray-600 dark:text-gray-400">Cursos</Text>
                </View>
                <View className="w-px h-10 bg-gray-200 dark:bg-gray-700" />
                <View className="items-center">
                  <Text className="text-2xl font-bold text-gray-900 dark:text-white">1250</Text>
                  <Text className="text-xs text-gray-600 dark:text-gray-400">Puntos</Text>
                </View>
                <View className="w-px h-10 bg-gray-200 dark:bg-gray-700" />
                <View className="items-center">
                  <Text className="text-2xl font-bold text-gray-900 dark:text-white">5</Text>
                  <Text className="text-xs text-gray-600 dark:text-gray-400">Nivel</Text>
                </View>
              </View>
            </View>
          </Card>
        </View>

        {/* Menu Sections */}
        {menuSections.map((section, sectionIndex) => (
          <View
            key={section.title}
            className="mb-6"
          >
            <Text className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase mb-2 px-1">
              {section.title}
            </Text>
            <Card variant="elevated" padding="none">
              {section.items.map((item, itemIndex) => (
                <TouchableOpacity
                  key={item.label}
                  onPress={item.onPress}
                  activeOpacity={0.7}
                  className={`flex-row items-center p-4 ${
                    itemIndex < section.items.length - 1
                      ? 'border-b border-gray-200 dark:border-gray-700'
                      : ''
                  }`}
                >
                  <View className="w-10 h-10 rounded-full bg-gray-100 dark:bg-gray-800 items-center justify-center mr-3">
                    <Ionicons name={item.icon as any} size={20} color="#8b5cf6" />
                  </View>
                  <Text className="flex-1 text-base text-gray-900 dark:text-white font-medium">
                    {item.label}
                  </Text>
                  {item.badge && (
                    <Badge variant="primary" size="sm">
                      {item.badge}
                    </Badge>
                  )}
                  {item.rightText && (
                    <Text className="text-sm text-gray-600 dark:text-gray-400 mr-2">
                      {item.rightText}
                    </Text>
                  )}
                  <Ionicons name="chevron-forward" size={20} color="#9ca3af" />
                </TouchableOpacity>
              ))}
            </Card>
          </View>
        ))}

        {/* Logout Button */}
        <View>
          <Button variant="danger" size="lg" fullWidth onPress={handleLogout}>
            <View className="flex-row items-center justify-center">
              <Ionicons name="log-out-outline" size={20} color="white" />
              <Text className="ml-2 text-white font-bold">Cerrar Sesión</Text>
            </View>
          </Button>
        </View>

        {/* App Version */}
        <Text className="text-center text-xs text-gray-400 dark:text-gray-600 mb-4">
          Acadify Mobile v1.0.0
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}
