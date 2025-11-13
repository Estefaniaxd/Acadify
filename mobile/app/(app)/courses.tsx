/**
 * Courses Screen
 * List of all available courses
 */

import React, { useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, TextInput } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Card, Badge, Progress } from '@/components/ui';

export default function CoursesScreen() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');

  // Mock data - replace with real data from API
  const courses = [
    {
      id: 1,
      title: 'Matemáticas Avanzadas',
      instructor: 'Prof. Juan Pérez',
      progress: 65,
      students: 245,
      rating: 4.8,
      category: 'Matemáticas',
      status: 'active',
    },
    {
      id: 2,
      title: 'Historia Universal',
      instructor: 'Prof. María García',
      progress: 45,
      students: 180,
      rating: 4.6,
      category: 'Historia',
      status: 'active',
    },
    {
      id: 3,
      title: 'Programación en Python',
      instructor: 'Prof. Carlos Ruiz',
      progress: 80,
      students: 320,
      rating: 4.9,
      category: 'Programación',
      status: 'active',
    },
    {
      id: 4,
      title: 'Física Cuántica',
      instructor: 'Prof. Ana López',
      progress: 0,
      students: 150,
      rating: 4.7,
      category: 'Física',
      status: 'new',
    },
    {
      id: 5,
      title: 'Literatura Clásica',
      instructor: 'Prof. Luis Torres',
      progress: 100,
      students: 200,
      rating: 4.5,
      category: 'Literatura',
      status: 'completed',
    },
  ];

  const categories = ['Todos', 'Matemáticas', 'Historia', 'Programación', 'Física', 'Literatura'];
  const [selectedCategory, setSelectedCategory] = useState('Todos');

  const filteredCourses = courses.filter((course) => {
    const matchesSearch = course.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory =
      selectedCategory === 'Todos' || course.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <SafeAreaView className="flex-1 bg-gray-50 dark:bg-neutral-950">
      <View className="flex-1">
        {/* Header */}
        <View className="p-6 pb-4">
          <Text className="text-3xl font-black text-gray-900 dark:text-white mb-4">
            Mis Cursos
          </Text>

          {/* Search Bar */}
          <View className="flex-row items-center bg-white dark:bg-neutral-900 rounded-2xl px-4 py-3 border border-gray-200 dark:border-gray-700 mb-4">
            <Ionicons name="search" size={20} color="#9ca3af" />
            <TextInput
              className="flex-1 ml-2 text-gray-900 dark:text-white"
              placeholder="Buscar cursos..."
              placeholderTextColor="#9ca3af"
              value={searchQuery}
              onChangeText={setSearchQuery}
            />
          </View>

          {/* Categories */}
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            className="flex-row -mx-6 px-6"
            contentContainerStyle={{ gap: 8 }}
          >
            {categories.map((category) => (
              <TouchableOpacity
                key={category}
                onPress={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-full ${
                  selectedCategory === category
                    ? 'bg-violet-600'
                    : 'bg-gray-200 dark:bg-neutral-800'
                }`}
              >
                <Text
                  className={`text-sm font-semibold ${
                    selectedCategory === category
                      ? 'text-white'
                      : 'text-gray-700 dark:text-gray-300'
                  }`}
                >
                  {category}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {/* Courses List */}
        <ScrollView
          className="flex-1 px-6"
          showsVerticalScrollIndicator={false}
          contentContainerStyle={{ paddingBottom: 20 }}
        >
          {filteredCourses.length === 0 ? (
            <View className="flex-1 items-center justify-center py-20">
              <Ionicons name="search-outline" size={64} color="#d1d5db" />
              <Text className="text-gray-500 dark:text-gray-400 mt-4">
                No se encontraron cursos
              </Text>
            </View>
          ) : (
            <View className="gap-4">
              {filteredCourses.map((course, index) => (
                <View key={course.id}>
                  <TouchableOpacity
                    activeOpacity={0.8}
                    onPress={() => console.log('Course:', course.id)}
                  >
                    <Card variant="elevated" padding="lg">
                      {/* Course Header */}
                      <View className="flex-row items-start justify-between mb-3">
                        <View className="flex-1 mr-3">
                          <Text className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                            {course.title}
                          </Text>
                          <Text className="text-sm text-gray-600 dark:text-gray-400">
                            {course.instructor}
                          </Text>
                        </View>
                        {course.status === 'new' && (
                          <Badge variant="success" size="sm">
                            Nuevo
                          </Badge>
                        )}
                        {course.status === 'completed' && (
                          <Badge variant="primary" size="sm">
                            Completado
                          </Badge>
                        )}
                        {course.status === 'active' && course.progress > 0 && (
                          <Badge variant="warning" size="sm">
                            En curso
                          </Badge>
                        )}
                      </View>

                      {/* Course Stats */}
                      <View className="flex-row items-center gap-4 mb-3">
                        <View className="flex-row items-center">
                          <Ionicons name="people-outline" size={16} color="#9ca3af" />
                          <Text className="text-xs text-gray-600 dark:text-gray-400 ml-1">
                            {course.students}
                          </Text>
                        </View>
                        <View className="flex-row items-center">
                          <Ionicons name="star" size={16} color="#f59e0b" />
                          <Text className="text-xs text-gray-600 dark:text-gray-400 ml-1">
                            {course.rating}
                          </Text>
                        </View>
                        <View className="flex-row items-center">
                          <Ionicons name="bookmark-outline" size={16} color="#9ca3af" />
                          <Text className="text-xs text-gray-600 dark:text-gray-400 ml-1">
                            {course.category}
                          </Text>
                        </View>
                      </View>

                      {/* Progress */}
                      {course.progress > 0 && (
                        <View>
                          <View className="flex-row items-center justify-between mb-1">
                            <Text className="text-xs text-gray-600 dark:text-gray-400">
                              Progreso
                            </Text>
                            <Text className="text-xs font-semibold text-gray-900 dark:text-white">
                              {course.progress}%
                            </Text>
                          </View>
                          <Progress
                            value={course.progress}
                            variant={
                              course.progress === 100
                                ? 'success'
                                : course.progress >= 50
                                ? 'primary'
                                : 'warning'
                            }
                            size="sm"
                          />
                        </View>
                      )}
                    </Card>
                  </TouchableOpacity>
                </View>
              ))}
            </View>
          )}
        </ScrollView>
      </View>
    </SafeAreaView>
  );
}
