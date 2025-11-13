import { View, Text, SafeAreaView, ScrollView, StyleSheet } from "react-native";
import { Button } from "@components/ui";
import { useRouter } from "expo-router";

export default function HomeScreen() {
  const router = useRouter();
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <Text style={styles.title}>🎓 Acadify</Text>
          <Text style={styles.subtitle}>Plataforma Educativa</Text>
        </View>
        <View style={styles.buttons}>
          <Button variant="primary" fullWidth onPress={() => router.push("/demo")}>Ver Demo</Button>
          <Button variant="outline" fullWidth onPress={() => router.push("/(auth)/login")}>Iniciar Sesión</Button>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#8b5cf6" },
  content: { flexGrow: 1, padding: 24, justifyContent: "center" },
  header: { alignItems: "center", marginBottom: 48 },
  title: { fontSize: 48, fontWeight: "bold", color: "#ffffff", textAlign: "center" },
  subtitle: { fontSize: 20, color: "#ffffff", opacity: 0.9, textAlign: "center" },
  buttons: { gap: 12 },
});
