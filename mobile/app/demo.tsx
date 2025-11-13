import { View, Text, ScrollView, SafeAreaView } from 'react-native';
import {
  Button,
  Input,
  Card,
  Avatar,
  Badge,
  Spinner,
  Progress,
  Checkbox,
  Switch,
} from '@components/ui';
import { useToast } from '@components/ui/Toast';
import { useState } from 'react';

/**
 * Pantalla de demostración de todos los componentes UI
 */
export default function ComponentsDemo() {
  const { toast } = useToast();
  const [email, setEmail] = useState('');
  const [checked, setChecked] = useState(false);
  const [switchValue, setSwitchValue] = useState(false);
  // const [modalOpen, setModalOpen] = useState(false); // Deshabilitado - componente Modal no disponible
  // const [bottomSheetOpen, setBottomSheetOpen] = useState(false); // Deshabilitado - componente BottomSheet no disponible
  
  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <ScrollView>
        <View className="p-6">
          {/* Header */}
          <View className="mb-8">
            <Text className="text-4xl font-bold text-primary-600 mb-2">
              Acadify UI
            </Text>
            <Text className="text-lg text-gray-600">
              Sistema de componentes completo
            </Text>
          </View>
          
          {/* Avatars */}
          <View className="mb-8">
            <Text className="text-2xl font-bold text-gray-900 mb-4">
              Avatars
            </Text>
            <Card variant="elevated" padding="lg">
              <View className="flex-row items-center gap-4 flex-wrap">
                <Avatar size="xs" alt="Juan Pérez" />
                <Avatar size="sm" alt="María García" status="online" />
                <Avatar size="md" alt="Carlos López" status="away" />
                <Avatar size="lg" alt="Ana Martínez" status="busy" />
                <Avatar
                  size="xl"
                  source={{ uri: 'https://i.pravatar.cc/150?img=1' }}
                  status="online"
                />
                <Avatar
                  size="2xl"
                  source={{ uri: 'https://i.pravatar.cc/150?img=2' }}
                />
              </View>
            </Card>
          </View>
          
          {/* Badges */}
          <View className="mb-8">
            <Text className="text-2xl font-bold text-gray-900 mb-4">
              Badges
            </Text>
            <Card variant="elevated" padding="lg">
              <View className="flex-row items-center gap-2 flex-wrap">
                <Badge variant="default">Default</Badge>
                <Badge variant="primary">Primary</Badge>
                <Badge variant="secondary">Secondary</Badge>
                <Badge variant="success">Completado</Badge>
                <Badge variant="warning">Pendiente</Badge>
                <Badge variant="danger">Rechazado</Badge>
                <Badge variant="outline">Outline</Badge>
              </View>
              
              <View className="flex-row items-center gap-3 mt-4">
                <Badge dot variant="success" />
                <Badge dot variant="warning" size="md" />
                <Badge dot variant="danger" size="lg" />
              </View>
            </Card>
          </View>
          
          {/* Progress */}
          <View className="mb-8">
            <Text className="text-2xl font-bold text-gray-900 mb-4">
              Progress Bars
            </Text>
            <Card variant="elevated" padding="lg">
              <View className="gap-4">
                <View>
                  <Text className="text-sm text-gray-600 mb-2">25% - Primary</Text>
                  <Progress value={25} variant="primary" />
                </View>
                <View>
                  <Text className="text-sm text-gray-600 mb-2">50% - Success</Text>
                  <Progress value={50} variant="success" size="md" />
                </View>
                <View>
                  <Text className="text-sm text-gray-600 mb-2">75% - Warning</Text>
                  <Progress value={75} variant="warning" size="lg" />
                </View>
                <View>
                  <Text className="text-sm text-gray-600 mb-2">100% - Danger</Text>
                  <Progress value={100} variant="danger" />
                </View>
              </View>
            </Card>
          </View>
          
          {/* Spinners */}
          <View className="mb-8">
            <Text className="text-2xl font-bold text-gray-900 mb-4">
              Spinners
            </Text>
            <Card variant="elevated" padding="lg">
              <View className="flex-row items-center gap-6 justify-around">
                <Spinner size="sm" variant="primary" />
                <Spinner size="md" variant="secondary" />
                <Spinner size="lg" variant="gray" />
              </View>
            </Card>
          </View>
          
          {/* Skeletons - DESHABILITADO TEMPORALMENTE */}
          {/* <View className="mb-8">
            <Text className="text-2xl font-bold text-gray-900 mb-4">
              Skeleton Loaders
            </Text>
            <Card variant="elevated" padding="lg">
              <Skeleton width="100%" height={40} variant="rounded" className="mb-4" />
              <SkeletonText lines={3} className="mb-4" />
              <SkeletonCard />
            </Card>
          </View> */}
          
          {/* Form Inputs */}
          <View className="mb-8">
            <Text className="text-2xl font-bold text-gray-900 mb-4">
              Form Components
            </Text>
            <Card variant="elevated" padding="lg">
              <View className="gap-4">
                <Input
                  label="Email"
                  placeholder="tu@email.com"
                  value={email}
                  onChangeText={setEmail}
                  helperText="Ingresa tu correo electrónico"
                />
                
                <Input
                  label="Password"
                  placeholder="••••••••"
                  secureTextEntry
                  error="La contraseña es muy corta"
                />
                
                <Checkbox
                  checked={checked}
                  onCheckedChange={setChecked}
                  label="Acepto términos y condiciones"
                />
                
                <Switch
                  checked={switchValue}
                  onCheckedChange={setSwitchValue}
                  label="Notificaciones push"
                  description="Recibe alertas en tiempo real"
                />
              </View>
            </Card>
          </View>
          
          {/* Buttons & Toasts */}
          <View className="mb-8">
            <Text className="text-2xl font-bold text-gray-900 mb-4">
              Buttons & Toasts
            </Text>
            <Card variant="elevated" padding="lg">
              <View className="gap-3">
                <Button
                  variant="primary"
                  fullWidth
                  onPress={() =>
                    toast({
                      title: 'Éxito',
                      description: 'Operación completada correctamente',
                      variant: 'success',
                    })
                  }
                >
                  Toast Success
                </Button>
                
                <Button
                  variant="secondary"
                  fullWidth
                  onPress={() =>
                    toast({
                      title: 'Advertencia',
                      description: 'Revisa la información',
                      variant: 'warning',
                    })
                  }
                >
                  Toast Warning
                </Button>
                
                <Button
                  variant="outline"
                  fullWidth
                  onPress={() =>
                    toast({
                      title: 'Error',
                      description: 'Algo salió mal',
                      variant: 'danger',
                    })
                  }
                >
                  Toast Error
                </Button>
                
                <Button
                  variant="ghost"
                  fullWidth
                  onPress={() =>
                    toast({
                      title: 'Información',
                      description: 'Mensaje informativo',
                      variant: 'info',
                    })
                  }
                >
                  Toast Info
                </Button>
              </View>
            </Card>
          </View>
          
          {/* Modals - DESHABILITADO TEMPORALMENTE */}
          {/* <View className="mb-8">
            <Text className="text-2xl font-bold text-gray-900 mb-4">
              Modals
            </Text>
            <Card variant="elevated" padding="lg">
              <View className="gap-3">
                <Button
                  variant="primary"
                  fullWidth
                  onPress={() => setModalOpen(true)}
                >
                  Abrir Modal Centro
                </Button>
                
                <Button
                  variant="secondary"
                  fullWidth
                  onPress={() => setBottomSheetOpen(true)}
                >
                  Abrir Bottom Sheet
                </Button>
              </View>
            </Card>
          </View> */}
        </View>
      </ScrollView>
      
      {/* Modal - DESHABILITADO TEMPORALMENTE */}
      {/* <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Modal de Ejemplo"
        description="Este es un modal centrado"
        size="md"
      >
        <View className="gap-4">
          <Text className="text-gray-700">
            Este modal se muestra en el centro de la pantalla con animación.
          </Text>
          
          <View className="flex-row gap-3">
            <Button
              variant="outline"
              className="flex-1"
              onPress={() => setModalOpen(false)}
            >
              Cancelar
            </Button>
            <Button
              variant="primary"
              className="flex-1"
              onPress={() => {
                setModalOpen(false);
                toast({ title: 'Confirmado', variant: 'success' });
              }}
            >
              Confirmar
            </Button>
          </View>
        </View>
      </Modal> */}
      
      {/* Bottom Sheet - DESHABILITADO TEMPORALMENTE */}
      {/* <BottomSheet
        open={bottomSheetOpen}
        onClose={() => setBottomSheetOpen(false)}
        title="Bottom Sheet"
        description="Desliza hacia abajo para cerrar"
      >
        <View className="gap-4">
          <Text className="text-gray-700">
            Este Bottom Sheet aparece desde abajo y es ideal para menús y acciones rápidas.
          </Text>
          
          <View className="gap-2">
            <Button variant="primary" fullWidth onPress={() => setBottomSheetOpen(false)}>
              Opción 1
            </Button>
            <Button variant="outline" fullWidth onPress={() => setBottomSheetOpen(false)}>
              Opción 2
            </Button>
            <Button variant="ghost" fullWidth onPress={() => setBottomSheetOpen(false)}>
              Cancelar
            </Button>
          </View>
        </View>
      </BottomSheet> */}
    </SafeAreaView>
  );
}
