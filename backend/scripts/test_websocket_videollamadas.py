#!/usr/bin/env python3
"""
Test Script para WebSocket de Videollamadas
Verifica funcionamiento de eventos en tiempo real.
"""

import asyncio
import websockets
import json
from datetime import datetime
from typing import Optional
import sys

# Configuración
BASE_URL = "ws://127.0.0.1:8000/api/communication/videollamadas/ws"
TOKEN_FILE = "TEST/test_token.txt"


class VideollamadaWSClient:
    """Cliente WebSocket para testing."""
    
    def __init__(self, videollamada_id: str, token: str, nombre: str):
        self.videollamada_id = videollamada_id
        self.token = token
        self.nombre = nombre
        self.ws = None
        self.running = False
    
    async def connect(self):
        """Conectar al WebSocket."""
        url = f"{BASE_URL}/{self.videollamada_id}?token={self.token}"
        
        try:
            self.ws = await websockets.connect(url)
            self.running = True
            print(f"✅ [{self.nombre}] Conectado a videollamada {self.videollamada_id}")
            return True
        except Exception as e:
            print(f"❌ [{self.nombre}] Error conectando: {e}")
            return False
    
    async def disconnect(self):
        """Desconectar del WebSocket."""
        if self.ws:
            await self.ws.close()
            self.running = False
            print(f"🔌 [{self.nombre}] Desconectado")
    
    async def send_message(self, message_type: str, **kwargs):
        """Enviar mensaje al servidor."""
        if not self.ws:
            print(f"❌ [{self.nombre}] No conectado")
            return
        
        message = {
            "type": message_type,
            **kwargs
        }
        
        try:
            await self.ws.send(json.dumps(message))
            print(f"📤 [{self.nombre}] Enviado: {message_type}")
        except Exception as e:
            print(f"❌ [{self.nombre}] Error enviando mensaje: {e}")
    
    async def listen(self):
        """Escuchar mensajes del servidor."""
        while self.running:
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                self._handle_event(data)
            except websockets.exceptions.ConnectionClosed:
                print(f"🔌 [{self.nombre}] Conexión cerrada por el servidor")
                self.running = False
                break
            except Exception as e:
                print(f"❌ [{self.nombre}] Error recibiendo mensaje: {e}")
                break
    
    def _handle_event(self, data: dict):
        """Manejar evento recibido."""
        event_type = data.get("type")
        timestamp = data.get("timestamp", "")
        
        # Mapeo de eventos a emojis
        event_icons = {
            "connected": "🔗",
            "user_joined_call": "👋",
            "user_left_call": "👋",
            "participant_audio_toggled": "🎤",
            "participant_video_toggled": "📹",
            "participant_screenshare_toggled": "🖥️",
            "recording_started": "⏺️",
            "recording_stopped": "⏹️",
            "participant_muted": "🔇",
            "participant_removed": "🚫",
            "call_ended": "📞",
            "participants_state": "📊",
            "pong": "🏓",
            "error": "❌"
        }
        
        icon = event_icons.get(event_type, "📨")
        
        if event_type == "connected":
            print(f"{icon} [{self.nombre}] Conectado exitosamente")
            print(f"   • Connection ID: {data.get('connection_id')}")
            print(f"   • Es moderador: {data.get('es_moderador')}")
        
        elif event_type == "user_joined_call":
            usuario_id = data.get("participante", {}).get("usuario_id")
            count = data.get("participant_count", 0)
            print(f"{icon} [{self.nombre}] Usuario {usuario_id} se unió (Total: {count})")
        
        elif event_type == "user_left_call":
            usuario_id = data.get("usuario_id")
            count = data.get("participant_count", 0)
            print(f"{icon} [{self.nombre}] Usuario {usuario_id} salió (Total: {count})")
        
        elif event_type == "participant_audio_toggled":
            usuario_id = data.get("usuario_id")
            enabled = data.get("audio_enabled")
            estado = "activado" if enabled else "desactivado"
            print(f"{icon} [{self.nombre}] Audio {estado} por {usuario_id}")
        
        elif event_type == "participant_video_toggled":
            usuario_id = data.get("usuario_id")
            enabled = data.get("video_enabled")
            estado = "activado" if enabled else "desactivado"
            print(f"{icon} [{self.nombre}] Video {estado} por {usuario_id}")
        
        elif event_type == "participant_screenshare_toggled":
            usuario_id = data.get("usuario_id")
            enabled = data.get("screenshare_enabled")
            estado = "iniciado" if enabled else "detenido"
            print(f"{icon} [{self.nombre}] Compartir pantalla {estado} por {usuario_id}")
        
        elif event_type == "recording_started":
            iniciado_por = data.get("iniciado_por")
            print(f"{icon} [{self.nombre}] Grabación iniciada por {iniciado_por}")
        
        elif event_type == "recording_stopped":
            detenido_por = data.get("detenido_por")
            duracion = data.get("duracion_segundos", 0)
            print(f"{icon} [{self.nombre}] Grabación detenida por {detenido_por} ({duracion}s)")
        
        elif event_type == "participant_muted":
            usuario_id = data.get("usuario_id")
            muted_by = data.get("muted_by")
            print(f"{icon} [{self.nombre}] {usuario_id} silenciado por moderador {muted_by}")
        
        elif event_type == "participant_removed":
            usuario_id = data.get("usuario_id")
            removed_by = data.get("removed_by")
            razon = data.get("razon", "N/A")
            print(f"{icon} [{self.nombre}] {usuario_id} expulsado por {removed_by} (Razón: {razon})")
        
        elif event_type == "call_ended":
            finalizado_por = data.get("finalizado_por")
            print(f"{icon} [{self.nombre}] Llamada finalizada por {finalizado_por}")
        
        elif event_type == "participants_state":
            count = data.get("count", 0)
            print(f"{icon} [{self.nombre}] Estado de participantes (Total: {count})")
            for uid, state in data.get("participants", {}).items():
                audio = "🎤" if state.get("audio_enabled") else "🔇"
                video = "📹" if state.get("video_enabled") else "📷"
                print(f"   • {uid}: {audio} {video}")
        
        elif event_type == "pong":
            print(f"{icon} [{self.nombre}] Pong recibido")
        
        elif event_type == "error":
            message = data.get("message", "Unknown error")
            print(f"{icon} [{self.nombre}] ERROR: {message}")
        
        else:
            print(f"{icon} [{self.nombre}] Evento desconocido: {event_type}")
            print(f"   Datos: {json.dumps(data, indent=2)}")


async def test_scenario_1():
    """
    Test Scenario 1: Conexión básica y eventos de audio/video.
    """
    print("\n" + "=" * 70)
    print("🧪 TEST SCENARIO 1: Conexión y Audio/Video Toggle")
    print("=" * 70 + "\n")
    
    # Cargar token
    try:
        with open(TOKEN_FILE, 'r') as f:
            token = f.read().strip()
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo de token: {TOKEN_FILE}")
        return
    
    # ID de videollamada (deberás crear una primero)
    videollamada_id = input("Ingresa el ID de la videollamada (o presiona Enter para test local): ").strip()
    if not videollamada_id:
        videollamada_id = "test-videollamada-123"
    
    # Crear cliente
    client = VideollamadaWSClient(videollamada_id, token, "Cliente Test")
    
    # Conectar
    connected = await client.connect()
    if not connected:
        return
    
    # Iniciar listener en background
    listener_task = asyncio.create_task(client.listen())
    
    # Esperar a recibir mensaje de bienvenida
    await asyncio.sleep(2)
    
    # Test 1: Toggle audio
    print("\n🎤 Test 1: Activar/Desactivar Audio")
    await client.send_message("audio_toggle", enabled=True)
    await asyncio.sleep(1)
    await client.send_message("audio_toggle", enabled=False)
    await asyncio.sleep(1)
    
    # Test 2: Toggle video
    print("\n📹 Test 2: Activar/Desactivar Video")
    await client.send_message("video_toggle", enabled=True)
    await asyncio.sleep(1)
    await client.send_message("video_toggle", enabled=False)
    await asyncio.sleep(1)
    
    # Test 3: Compartir pantalla
    print("\n🖥️  Test 3: Compartir Pantalla")
    await client.send_message("screenshare_toggle", enabled=True)
    await asyncio.sleep(1)
    await client.send_message("screenshare_toggle", enabled=False)
    await asyncio.sleep(1)
    
    # Test 4: Ping/Pong
    print("\n🏓 Test 4: Ping/Pong")
    await client.send_message("ping")
    await asyncio.sleep(1)
    
    # Test 5: Obtener estado de participantes
    print("\n📊 Test 5: Estado de Participantes")
    await client.send_message("get_participants_state")
    await asyncio.sleep(2)
    
    # Desconectar
    await client.disconnect()
    listener_task.cancel()
    
    print("\n✅ Test Scenario 1 completado\n")


async def test_scenario_2():
    """
    Test Scenario 2: Múltiples participantes simultáneos.
    """
    print("\n" + "=" * 70)
    print("🧪 TEST SCENARIO 2: Múltiples Participantes")
    print("=" * 70 + "\n")
    
    # Cargar token
    try:
        with open(TOKEN_FILE, 'r') as f:
            token = f.read().strip()
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo de token: {TOKEN_FILE}")
        return
    
    videollamada_id = input("Ingresa el ID de la videollamada: ").strip()
    if not videollamada_id:
        print("❌ ID de videollamada requerido")
        return
    
    # Crear múltiples clientes
    clients = [
        VideollamadaWSClient(videollamada_id, token, f"Participante {i+1}")
        for i in range(3)
    ]
    
    # Conectar todos
    print("Conectando participantes...")
    for client in clients:
        await client.connect()
        await asyncio.sleep(0.5)
    
    # Iniciar listeners
    listener_tasks = [
        asyncio.create_task(client.listen())
        for client in clients
    ]
    
    await asyncio.sleep(2)
    
    # Simulación de actividades
    print("\n🎬 Simulando actividades...")
    
    # Participante 1 desactiva audio
    await clients[0].send_message("audio_toggle", enabled=False)
    await asyncio.sleep(1)
    
    # Participante 2 desactiva video
    await clients[1].send_message("video_toggle", enabled=False)
    await asyncio.sleep(1)
    
    # Participante 3 comparte pantalla
    await clients[2].send_message("screenshare_toggle", enabled=True)
    await asyncio.sleep(2)
    
    # Todos obtienen estado
    for client in clients:
        await client.send_message("get_participants_state")
    
    await asyncio.sleep(3)
    
    # Desconectar todos
    print("\nDesconectando participantes...")
    for client in clients:
        await client.disconnect()
    
    for task in listener_tasks:
        task.cancel()
    
    print("\n✅ Test Scenario 2 completado\n")


def print_menu():
    """Imprimir menú de opciones."""
    print("\n" + "=" * 70)
    print("🧪 TESTS WEBSOCKET - VIDEOLLAMADAS")
    print("=" * 70)
    print()
    print("1. Test Scenario 1: Conexión y Audio/Video Toggle")
    print("2. Test Scenario 2: Múltiples Participantes")
    print("3. Salir")
    print()


async def main():
    """Función principal."""
    print("✨ Test Suite para WebSocket de Videollamadas")
    
    while True:
        print_menu()
        choice = input("Selecciona una opción: ").strip()
        
        if choice == "1":
            await test_scenario_1()
        elif choice == "2":
            await test_scenario_2()
        elif choice == "3":
            print("👋 Hasta luego!")
            break
        else:
            print("❌ Opción inválida")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
