# 🚀 Guía de Uso - Acadify Mobile

## 📖 Tabla de Contenidos

1. [Comenzar a Desarrollar](#comenzar-a-desarrollar)
2. [Usar Servicios](#usar-servicios)
3. [Usar Hooks](#usar-hooks)
4. [Usar Stores](#usar-stores)
5. [Crear Pantallas](#crear-pantallas)
6. [Componentes UI](#componentes-ui)
7. [Ejemplos Prácticos](#ejemplos-prácticos)

---

## 🏁 Comenzar a Desarrollar

### **Instalación y Setup**

```bash
# Navegar al directorio
cd mobile

# Instalar dependencias (si no están instaladas)
npm install

# Iniciar servidor de desarrollo
npm start

# Ejecutar en Android
npm run android

# Ejecutar en iOS
npm run ios
```

### **Estructura de Imports**

```typescript
// Servicios
import { authService, userService, courseService, messageService } from '@/services';

// Hooks
import { useCourses, useMessages, useUserProfile } from '@/hooks';

// Stores
import { useThemeStore, useNotificationStore } from '@/store';

// Componentes UI
import { Button, Input, Card, Badge } from '@/components/ui';

// Utils
import { formatApiError } from '@/utils/api';
import { getUserDisplayName } from '@/utils/auth';
```

---

## 📡 Usar Servicios

Los servicios NO deben usarse directamente en componentes. Usa hooks en su lugar.

### **✅ Correcto: Usar desde hooks**

```typescript
// hooks/useCourses.ts
export function useCourses() {
  return useQuery({
    queryKey: ['courses'],
    queryFn: () => courseService.getCourses(), // ← Aquí se usa el servicio
  });
}

// En componente
function CoursesScreen() {
  const { data, isLoading } = useCourses(); // ← Usar el hook
}
```

### **❌ Incorrecto: Usar directamente**

```typescript
// ❌ NO HACER ESTO
function CoursesScreen() {
  const [courses, setCourses] = useState([]);
  
  useEffect(() => {
    courseService.getCourses().then(setCourses); // ← Mal
  }, []);
}
```

### **Uso en Servicios Personalizados**

Si necesitas llamar servicios fuera de componentes:

```typescript
// utils/myCustomLogic.ts
import { courseService } from '@/services';

export async function enrollMultipleCourses(courseIds: string[]) {
  const results = await Promise.all(
    courseIds.map(id => courseService.enrollCourse(id))
  );
  return results;
}
```

---

## 🪝 Usar Hooks

### **Queries (Lectura de datos)**

```typescript
import { useCourses, useCourseDetail, useUserProfile } from '@/hooks';

function MyScreen() {
  // Obtener lista de cursos
  const { data: courses, isLoading, error, refetch } = useCourses({
    categoria: 'Programación',
    nivel: 'intermedio',
  });

  // Obtener detalle de un curso
  const { data: course } = useCourseDetail('course-123');

  // Obtener perfil de usuario
  const { data: profile } = useUserProfile();

  if (isLoading) return <Spinner />;
  if (error) return <Text>Error: {error.message}</Text>;

  return (
    <View>
      {courses?.data.map(course => (
        <CourseCard key={course.id} course={course} />
      ))}
    </View>
  );
}
```

### **Mutations (Escritura de datos)**

```typescript
import { useEnrollCourse, useSendMessage, useUpdateProfile } from '@/hooks';
import { useToast } from '@/components/ui/Toast';

function MyScreen() {
  const { toast } = useToast();

  // Inscribirse a un curso
  const { mutate: enrollCourse, isLoading } = useEnrollCourse({
    onSuccess: () => {
      toast({
        title: 'Éxito',
        description: 'Te has inscrito al curso',
        variant: 'success',
      });
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'danger',
      });
    },
  });

  // Enviar mensaje
  const { mutate: sendMessage } = useSendMessage();

  // Actualizar perfil
  const { mutate: updateProfile } = useUpdateProfile();

  const handleEnroll = () => {
    enrollCourse('course-123');
  };

  const handleSendMessage = () => {
    sendMessage({
      conversacion_id: 'conv-456',
      contenido: 'Hola!',
      tipo: 'texto',
    });
  };

  return (
    <View>
      <Button onPress={handleEnroll} loading={isLoading}>
        Inscribirse
      </Button>
    </View>
  );
}
```

### **Invalidar Caché Manualmente**

```typescript
import { useQueryClient } from '@tanstack/react-query';
import { QUERY_KEYS } from '@/hooks';

function MyScreen() {
  const queryClient = useQueryClient();

  const handleRefresh = () => {
    // Invalidar cursos inscritos
    queryClient.invalidateQueries({ queryKey: QUERY_KEYS.enrolledCourses });
    
    // Invalidar detalle de curso específico
    queryClient.invalidateQueries({ queryKey: QUERY_KEYS.courseDetail('course-123') });
    
    // Invalidar todos los cursos
    queryClient.invalidateQueries({ queryKey: QUERY_KEYS.courses });
  };
}
```

---

## 🗄️ Usar Stores

### **Theme Store**

```typescript
import { useThemeStore } from '@/store';

function SettingsScreen() {
  const { mode, isDark, setTheme, toggleTheme } = useThemeStore();

  return (
    <View>
      <Text>Tema actual: {mode}</Text>
      <Text>¿Es oscuro?: {isDark ? 'Sí' : 'No'}</Text>

      <Button onPress={() => setTheme('dark')}>
        Modo Oscuro
      </Button>

      <Button onPress={() => setTheme('light')}>
        Modo Claro
      </Button>

      <Button onPress={() => setTheme('auto')}>
        Automático
      </Button>

      <Button onPress={toggleTheme}>
        Toggle Tema
      </Button>
    </View>
  );
}
```

### **Notification Store**

```typescript
import { useNotificationStore } from '@/store';

function NotificationsScreen() {
  const { 
    notifications, 
    unreadCount, 
    addNotification, 
    markAsRead,
    markAllAsRead,
    clearAll 
  } = useNotificationStore();

  const handleAddNotification = () => {
    addNotification({
      type: 'logro',
      titulo: 'Nuevo logro',
      descripcion: 'Has completado tu primer curso',
    });
  };

  return (
    <View>
      <Text>No leídas: {unreadCount}</Text>
      
      <Button onPress={handleAddNotification}>
        Agregar Notificación
      </Button>

      <Button onPress={markAllAsRead}>
        Marcar todas como leídas
      </Button>

      <Button onPress={clearAll}>
        Eliminar todas
      </Button>

      {notifications.map(notif => (
        <View key={notif.id}>
          <Text>{notif.titulo}</Text>
          <Button onPress={() => markAsRead(notif.id)}>
            Marcar como leída
          </Button>
        </View>
      ))}
    </View>
  );
}
```

### **Course Filter Store**

```typescript
import { useCourseFilterStore } from '@/store';
import { useCourses } from '@/hooks';

function CoursesScreen() {
  const { 
    filters, 
    searchQuery,
    setCategory, 
    setSearchQuery, 
    resetFilters,
    hasActiveFilters 
  } = useCourseFilterStore();

  // Los filtros se pasan automáticamente al hook
  const { data: courses } = useCourses(filters);

  return (
    <View>
      <Input
        value={searchQuery}
        onChangeText={setSearchQuery}
        placeholder="Buscar cursos..."
      />

      <View>
        {['Todos', 'Matemáticas', 'Programación', 'Historia'].map(cat => (
          <Button 
            key={cat}
            onPress={() => setCategory(cat === 'Todos' ? undefined : cat)}
            variant={filters.categoria === cat ? 'primary' : 'outline'}
          >
            {cat}
          </Button>
        ))}
      </View>

      {hasActiveFilters() && (
        <Button onPress={resetFilters}>
          Limpiar filtros
        </Button>
      )}

      {courses?.data.map(course => (
        <CourseCard key={course.id} course={course} />
      ))}
    </View>
  );
}
```

### **WebSocket Store**

```typescript
import { useWebSocketStore } from '@/store';
import { useAuth } from '@/hooks';
import { useEffect } from 'react';

function ChatScreen() {
  const { status, connect, disconnect, send, addMessageHandler } = useWebSocketStore();
  const { user } = useAuth();

  useEffect(() => {
    // Conectar al WebSocket
    const WS_URL = 'wss://api.acadify.com/ws';
    connect(WS_URL, user?.token);

    // Agregar handler para mensajes entrantes
    const unsubscribe = addMessageHandler((message) => {
      if (message.type === 'message') {
        console.log('Nuevo mensaje:', message.data);
        // Actualizar UI
      }
      
      if (message.type === 'typing') {
        console.log('Usuario está escribiendo...');
      }
    });

    // Cleanup
    return () => {
      unsubscribe();
      disconnect();
    };
  }, [user?.token]);

  const handleSendMessage = (content: string) => {
    send({
      type: 'message',
      data: {
        conversacion_id: 'conv-123',
        contenido: content,
      },
      timestamp: new Date().toISOString(),
    });
  };

  return (
    <View>
      <Text>Estado: {status}</Text>
      {status === 'connected' && <Text>✅ Conectado</Text>}
      {status === 'connecting' && <Text>⏳ Conectando...</Text>}
      {status === 'disconnected' && <Text>🔴 Desconectado</Text>}
    </View>
  );
}
```

---

## 🖥️ Crear Pantallas

### **Template Básico**

```typescript
/**
 * My Feature Screen
 * Descripción de la pantalla
 */

import React, { useState } from 'react';
import { View, Text, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Animated, { FadeInDown } from 'react-native-reanimated';
import { Button, Input, Card } from '@/components/ui';
import { useMyCoolHook } from '@/hooks';

export default function MyFeatureScreen() {
  // State
  const [value, setValue] = useState('');
  
  // Hooks
  const { data, isLoading, error } = useMyCoolHook();

  // Handlers
  const handleSubmit = () => {
    console.log('Submit:', value);
  };

  // Loading state
  if (isLoading) {
    return (
      <SafeAreaView className="flex-1 items-center justify-center">
        <Spinner />
      </SafeAreaView>
    );
  }

  // Error state
  if (error) {
    return (
      <SafeAreaView className="flex-1 items-center justify-center p-6">
        <Text className="text-red-600 text-center">{error.message}</Text>
      </SafeAreaView>
    );
  }

  // Main content
  return (
    <SafeAreaView className="flex-1 bg-gray-50 dark:bg-neutral-950">
      <ScrollView 
        className="flex-1"
        contentContainerClassName="p-6"
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <Animated.View entering={FadeInDown.duration(600).delay(100)}>
          <Text className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Mi Pantalla
          </Text>
        </Animated.View>

        {/* Content */}
        <Card variant="elevated" padding="lg">
          <Input
            label="Campo"
            value={value}
            onChangeText={setValue}
            placeholder="Ingresa algo..."
          />
          
          <Button 
            variant="primary" 
            fullWidth 
            onPress={handleSubmit}
            className="mt-4"
          >
            Enviar
          </Button>
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
}
```

### **Template con Tabs**

```typescript
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: '#8b5cf6',
        tabBarInactiveTintColor: '#9ca3af',
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Inicio',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="home" size={size} color={color} />
          ),
        }}
      />
      
      <Tabs.Screen
        name="courses"
        options={{
          title: 'Cursos',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="book" size={size} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}
```

---

## 🎨 Componentes UI

### **Button**

```typescript
<Button 
  variant="primary"      // primary | secondary | outline | ghost | danger
  size="lg"              // sm | md | lg
  fullWidth              // boolean
  loading={isLoading}    // boolean
  disabled={false}       // boolean
  onPress={() => {}}
>
  Texto del botón
</Button>
```

### **Input**

```typescript
<Input
  label="Email"
  value={email}
  onChangeText={setEmail}
  placeholder="tu@email.com"
  error={errors.email}
  description="Ingresa tu email institucional"
  leftIcon={<Ionicons name="mail-outline" size={20} />}
  rightIcon={<Ionicons name="checkmark" size={20} />}
  keyboardType="email-address"
  autoCapitalize="none"
  secureTextEntry={false}
/>
```

### **Card**

```typescript
<Card 
  variant="elevated"     // default | elevated | outlined
  padding="lg"           // none | sm | md | lg
>
  <Text>Contenido del card</Text>
</Card>
```

### **Badge**

```typescript
<Badge 
  variant="primary"      // primary | secondary | success | warning | danger
  size="md"              // sm | md | lg
>
  Nuevo
</Badge>
```

### **Avatar**

```typescript
<Avatar
  src="https://example.com/avatar.jpg"
  alt="Juan Pérez"
  size="lg"              // sm | md | lg | xl | 2xl
  fallback="JP"
/>
```

### **Progress**

```typescript
<Progress 
  value={75}             // 0-100
  variant="success"      // primary | secondary | success | warning | danger
  size="md"              // sm | md | lg
  showLabel              // boolean
/>
```

---

## 💡 Ejemplos Prácticos

### **Ejemplo 1: Inscribirse a un Curso**

```typescript
import { useEnrollCourse, useCourseDetail } from '@/hooks';
import { useToast } from '@/components/ui/Toast';

function CourseDetailScreen({ courseId }) {
  const { data: course, isLoading } = useCourseDetail(courseId);
  const { mutate: enrollCourse, isLoading: enrolling } = useEnrollCourse({
    onSuccess: () => {
      toast({
        title: '¡Inscrito!',
        description: 'Ya puedes comenzar el curso',
        variant: 'success',
      });
    },
  });
  const { toast } = useToast();

  const handleEnroll = () => {
    enrollCourse(courseId);
  };

  return (
    <View>
      <Text>{course?.titulo}</Text>
      <Button 
        onPress={handleEnroll} 
        loading={enrolling}
      >
        Inscribirse
      </Button>
    </View>
  );
}
```

### **Ejemplo 2: Enviar Mensaje con Imagen**

```typescript
import { useSendMessage, useSendFile } from '@/hooks';
import { useState } from 'react';

function ChatScreen({ conversationId }) {
  const [message, setMessage] = useState('');
  const { mutate: sendMessage } = useSendMessage();
  const { mutate: sendFile } = useSendFile();

  const handleSendText = () => {
    sendMessage({
      conversacion_id: conversationId,
      contenido: message,
      tipo: 'texto',
    });
    setMessage('');
  };

  const handleSendImage = async () => {
    // Seleccionar imagen (usar expo-image-picker)
    const image = await pickImage();
    
    sendFile({
      conversationId,
      file: image,
      tipo: 'imagen',
    });
  };

  return (
    <View>
      <Input
        value={message}
        onChangeText={setMessage}
        placeholder="Escribe un mensaje..."
      />
      <Button onPress={handleSendText}>Enviar</Button>
      <Button onPress={handleSendImage}>📷 Imagen</Button>
    </View>
  );
}
```

### **Ejemplo 3: Actualizar Perfil con Avatar**

```typescript
import { useUpdateProfile, useUploadAvatar, useUserProfile } from '@/hooks';
import { useState } from 'react';

function EditProfileScreen() {
  const { data: profile } = useUserProfile();
  const { mutate: updateProfile, isLoading } = useUpdateProfile();
  const { mutate: uploadAvatar, isLoading: uploading } = useUploadAvatar();
  
  const [bio, setBio] = useState(profile?.bio || '');

  const handleUpdateProfile = () => {
    updateProfile({
      bio,
      ciudad: 'Bogotá',
    });
  };

  const handleChangeAvatar = async () => {
    const image = await pickImage();
    uploadAvatar(image);
  };

  return (
    <View>
      <Avatar 
        src={profile?.avatar_url}
        alt={profile?.nombres}
        size="2xl"
      />
      <Button onPress={handleChangeAvatar} loading={uploading}>
        Cambiar foto
      </Button>

      <Input
        label="Biografía"
        value={bio}
        onChangeText={setBio}
        multiline
      />

      <Button 
        onPress={handleUpdateProfile} 
        loading={isLoading}
      >
        Guardar cambios
      </Button>
    </View>
  );
}
```

---

## 🐛 Debugging

### **React Query Devtools (Web)**

```typescript
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

export default function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {__DEV__ && <ReactQueryDevtools />}
    </QueryClientProvider>
  );
}
```

### **Console Logging**

```typescript
// En servicios
async getCourses() {
  console.log('📚 Fetching courses...');
  const response = await apiClient.get('/courses');
  console.log('✅ Courses fetched:', response.data);
  return response.data;
}

// En hooks
const { data } = useCourses();
console.log('Courses from hook:', data);

// En stores
setTheme: (mode) => {
  console.log('🎨 Changing theme to:', mode);
  set({ mode });
}
```

---

## 📚 Recursos Adicionales

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Arquitectura completa
- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - Resumen de implementación
- [README.md](./README.md) - Setup inicial

---

**¡Feliz desarrollo! 🚀**
