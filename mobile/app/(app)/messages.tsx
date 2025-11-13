/**
 * Messages Screen
 * Chat conversations list
 */

import React from 'react';
import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Card, Badge, Avatar } from '@/components/ui';

export default function MessagesScreen() {
  // Mock data - replace with real data from API
  const conversations = [
    {
      id: 1,
      user: 'Prof. Juan Pérez',
      lastMessage: 'Tu tarea está muy bien, felicitaciones!',
      timestamp: 'Hace 5 min',
      unread: 2,
      online: true,
    },
    {
      id: 2,
      user: 'María García',
      lastMessage: '¿Puedes ayudarme con el ejercicio 3?',
      timestamp: 'Hace 1h',
      unread: 1,
      online: true,
    },
    {
      id: 3,
      user: 'Carlos Ruiz',
      lastMessage: 'Gracias por la explicación!',
      timestamp: 'Ayer',
      unread: 0,
      online: false,
    },
    {
      id: 4,
      user: 'Grupo: Matemáticas Avanzadas',
      lastMessage: 'Pedro: Alguien tiene el PDF?',
      timestamp: 'Ayer',
      unread: 5,
      online: false,
      isGroup: true,
    },
    {
      id: 5,
      user: 'Ana López',
      lastMessage: 'Nos vemos en clase!',
      timestamp: '2 días',
      unread: 0,
      online: false,
    },
  ];

  return (
    <SafeAreaView className="flex-1 bg-gray-50 dark:bg-neutral-950">
      <View className="flex-1">
        {/* Header */}
        <View className="px-6 py-4 flex-row items-center justify-between">
          <Text className="text-3xl font-black text-gray-900 dark:text-white">Mensajes</Text>
          <TouchableOpacity className="w-10 h-10 rounded-full bg-violet-600 items-center justify-center">
            <Ionicons name="create-outline" size={20} color="white" />
          </TouchableOpacity>
        </View>

        {/* Conversations List */}
        <ScrollView
          className="flex-1 px-6"
          showsVerticalScrollIndicator={false}
          contentContainerStyle={{ paddingBottom: 20 }}
        >
          <View className="gap-2">
            {conversations.map((conversation, index) => (
              <View key={conversation.id}>
                <TouchableOpacity activeOpacity={0.7}>
                  <Card variant="default" padding="md" className="bg-white dark:bg-neutral-900">
                    <View className="flex-row items-center">
                      {/* Avatar */}
                      <View className="mr-3 relative">
                        <Avatar
                          alt={conversation.user}
                          size="lg"
                        />
                        {conversation.online && (
                          <View className="absolute bottom-0 right-0 w-3 h-3 bg-emerald-500 border-2 border-white dark:border-neutral-900 rounded-full" />
                        )}
                      </View>

                      {/* Content */}
                      <View className="flex-1 mr-3">
                        <View className="flex-row items-center justify-between mb-1">
                          <Text className="text-base font-bold text-gray-900 dark:text-white flex-1">
                            {conversation.user}
                          </Text>
                          <Text className="text-xs text-gray-500 dark:text-gray-400 ml-2">
                            {conversation.timestamp}
                          </Text>
                        </View>
                        <View className="flex-row items-center">
                          {conversation.isGroup && (
                            <Ionicons
                              name="people"
                              size={14}
                              color="#9ca3af"
                              style={{ marginRight: 4 }}
                            />
                          )}
                          <Text
                            className={`text-sm flex-1 ${
                              conversation.unread > 0
                                ? 'font-semibold text-gray-900 dark:text-white'
                                : 'text-gray-600 dark:text-gray-400'
                            }`}
                            numberOfLines={1}
                          >
                            {conversation.lastMessage}
                          </Text>
                        </View>
                      </View>

                      {/* Unread Badge */}
                      {conversation.unread > 0 && (
                        <View className="w-6 h-6 rounded-full bg-violet-600 items-center justify-center">
                          <Text className="text-xs font-bold text-white">
                            {conversation.unread}
                          </Text>
                        </View>
                      )}
                    </View>
                  </Card>
                </TouchableOpacity>
              </View>
            ))}
          </View>

          {/* Empty State */}
          {conversations.length === 0 && (
            <View className="flex-1 items-center justify-center py-20">
              <Ionicons name="chatbubbles-outline" size={64} color="#d1d5db" />
              <Text className="text-gray-500 dark:text-gray-400 mt-4 text-center">
                No tienes conversaciones aún
              </Text>
              <Text className="text-gray-400 dark:text-gray-500 text-sm text-center mt-2">
                Inicia una conversación con tus compañeros o profesores
              </Text>
            </View>
          )}
        </ScrollView>
      </View>
    </SafeAreaView>
  );
}
