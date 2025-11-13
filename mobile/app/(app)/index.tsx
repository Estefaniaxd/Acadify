/**
 * Dashboard Screen
 * Main home screen for authenticated users
 */

import React from 'react';
import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '@/context/AuthContext';
import { Card, Badge, Progress, Avatar, Button } from '@/components/ui';
import { getUserDisplayName, getUserInitials } from '@/utils/auth';

export default function DashboardScreen() {
  const { user, logout } = useAuth();
  const router = useRouter();

  const userDisplayName = getUserDisplayName(user);
  const userInitials = getUserInitials(user);

  // Mock data - replace with real data from API
  const stats = {
    cursosActivos: 4,
    tareasPendientes: 7,
    puntosTotales: 1250,
    nivel: 5,
  };

  const recentCourses = [
    {
      id: 1,
      title: 'Matemáticas Avanzadas',
      progress: 65,
      nextLesson: 'Cálculo Diferencial',
      dueDate: 'Hoy',
    },
    {
      id: 2,
      title: 'Historia Universal',
      progress: 45,
      nextLesson: 'Revolución Industrial',
      dueDate: 'Mañana',
    },
    {
      id: 3,
      title: 'Programación en Python',
      progress: 80,
      nextLesson: 'POO Avanzada',
      dueDate: '2 días',
    },
  ];

  const achievements = [
    { icon: '🏆', label: 'Top 10' },
    { icon: '⚡', label: '7 días' },
    { icon: '🎯', label: '100%' },
    { icon: '🔥', label: '20 racha' },
  ];

  return (
    <SafeAreaView className="flex-1 bg-gray-50 dark:bg-neutral-950">
      <ScrollView
        className="flex-1"
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View>
          <View className="flex-row items-center justify-between mb-4">
            <View>
              <Text className="text-sm text-gray-600 dark:text-gray-400">Hola de nuevo 👋</Text>
              <Text className="text-2xl font-black text-gray-900 dark:text-white">
                {userDisplayName}
              </Text>
            </View>
            <TouchableOpacity onPress={() => router.push('/(app)/profile')}>
              <Avatar alt={userDisplayName} size="lg" />
            </TouchableOpacity>
          </View>

          {/* Stats Cards */}
          <View className="flex-row gap-3">
            <Card variant="elevated" padding="md" className="flex-1">
              <View className="items-center">
                <Ionicons name="book-outline" size={24} color="#8b5cf6" />
                <Text className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                  {stats.cursosActivos}
                </Text>
                <Text className="text-xs text-gray-600 dark:text-gray-400">Cursos</Text>
              </View>
            </Card>
            <Card variant="elevated" padding="md" className="flex-1">
              <View className="items-center">
                <Ionicons name="checkmark-circle-outline" size={24} color="#10b981" />
                <Text className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                  {stats.tareasPendientes}
                </Text>
                <Text className="text-xs text-gray-600 dark:text-gray-400">Tareas</Text>
              </View>
            </Card>
            <Card variant="elevated" padding="md" className="flex-1">
              <View className="items-center">
                <Ionicons name="star-outline" size={24} color="#f59e0b" />
                <Text className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
                  {stats.puntosTotales}
                </Text>
                <Text className="text-xs text-gray-600 dark:text-gray-400">Puntos</Text>
              </View>
            </Card>
          </View>
        </View>

        {/* Level Progress */}
        <View>
          <Card variant="elevated" padding="lg" className="mb-6">
            <View className="flex-row items-center justify-between mb-3">
              <View className="flex-row items-center">
                <View className="w-10 h-10 rounded-full bg-violet-600 items-center justify-center mr-3">
                  <Text className="text-white font-bold">{stats.nivel}</Text>
                </View>
                <View>
                  <Text className="text-sm font-semibold text-gray-900 dark:text-white">
                    Nivel {stats.nivel}
                  </Text>
                  <Text className="text-xs text-gray-600 dark:text-gray-400">
                    250 pts para nivel {stats.nivel + 1}
                  </Text>
                </View>
              </View>
              <Badge variant="primary">En progreso</Badge>
            </View>
            <Progress value={70} variant="primary" size="md" />
          </Card>
        </View>

        {/* Achievements */}
        <View>
          <Text className="text-lg font-bold text-gray-900 dark:text-white mb-3">
            Logros Recientes
          </Text>
          <View className="flex-row gap-3">
            {achievements.map((achievement, index) => (
              <Card key={index} variant="elevated" padding="md" className="flex-1">
                <View className="items-center">
                  <Text className="text-3xl mb-2">{achievement.icon}</Text>
                  <Text className="text-xs text-gray-600 dark:text-gray-400 text-center">
                    {achievement.label}
                  </Text>
                </View>
              </Card>
            ))}
          </View>
        </View>

        {/* Recent Courses */}
        <View>
          <View className="flex-row items-center justify-between mb-3">
            <Text className="text-lg font-bold text-gray-900 dark:text-white">
              Continúa Aprendiendo
            </Text>
            <TouchableOpacity onPress={() => router.push('/(app)/courses')}>
              <Text className="text-sm font-semibold text-violet-600 dark:text-violet-400">
                Ver todos
              </Text>
            </TouchableOpacity>
          </View>

          <View className="gap-3">
            {recentCourses.map((course) => (
              <Card key={course.id} variant="elevated" padding="lg">
                <View className="flex-row items-center justify-between mb-3">
                  <Text className="text-base font-bold text-gray-900 dark:text-white flex-1">
                    {course.title}
                  </Text>
                  <Badge variant="warning" size="sm">
                    {course.dueDate}
                  </Badge>
                </View>

                <Text className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                  Próxima lección: {course.nextLesson}
                </Text>

                <View className="mb-3">
                  <View className="flex-row items-center justify-between mb-1">
                    <Text className="text-xs text-gray-600 dark:text-gray-400">Progreso</Text>
                    <Text className="text-xs font-semibold text-gray-900 dark:text-white">
                      {course.progress}%
                    </Text>
                  </View>
                  <Progress value={course.progress} variant="success" size="sm" />
                </View>

                <Button variant="primary" size="sm" fullWidth>
                  Continuar
                </Button>
              </Card>
            ))}
          </View>
        </View>

        {/* Quick Actions */}
        <View>
          <Text className="text-lg font-bold text-gray-900 dark:text-white mb-3">
            Acciones Rápidas
          </Text>
          <View className="flex-row gap-3">
            <TouchableOpacity className="flex-1">
              <Card variant="elevated" padding="lg">
                <View className="items-center">
                  <Ionicons name="calendar-outline" size={32} color="#8b5cf6" />
                  <Text className="text-sm font-semibold text-gray-900 dark:text-white mt-2">
                    Horario
                  </Text>
                </View>
              </Card>
            </TouchableOpacity>
            <TouchableOpacity className="flex-1">
              <Card variant="elevated" padding="lg">
                <View className="items-center">
                  <Ionicons name="trophy-outline" size={32} color="#f59e0b" />
                  <Text className="text-sm font-semibold text-gray-900 dark:text-white mt-2">
                    Ranking
                  </Text>
                </View>
              </Card>
            </TouchableOpacity>
            <TouchableOpacity className="flex-1">
              <Card variant="elevated" padding="lg">
                <View className="items-center">
                  <Ionicons name="ribbon-outline" size={32} color="#10b981" />
                  <Text className="text-sm font-semibold text-gray-900 dark:text-white mt-2">
                    Insignias
                  </Text>
                </View>
              </Card>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
