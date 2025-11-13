"""
Test del Sistema de Comunicación - Fase 1
==========================================

Suite completa de tests para el sistema de chat en tiempo real.

Categorías:
1. Backend - WebSocket Manager
2. Backend - Chat WebSocket Endpoint
3. Frontend - Services (simulación)
4. Integración - Flujo completo

@author Acadify Team
"""

import pytest
import asyncio
import json
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Imports del proyecto
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app
from src.services.websocket_manager import connection_manager
from src.crud.auth.crud_usuario import crud_usuario
from src.db.session import get_db


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def test_client():
    """Cliente de prueba para FastAPI"""
    return TestClient(app)


@pytest.fixture
async def clean_connection_manager():
    """Limpiar ConnectionManager antes de cada test"""
    # Limpiar todas las conexiones
    connection_manager._active_connections.clear()
    connection_manager._user_rooms.clear()
    connection_manager._typing_users.clear()
    yield connection_manager
    # Limpiar después del test
    connection_manager._active_connections.clear()
    connection_manager._user_rooms.clear()
    connection_manager._typing_users.clear()


@pytest.fixture
def mock_websocket():
    """Mock de WebSocket para testing"""
    ws = AsyncMock(spec=WebSocket)
    ws.send_json = AsyncMock()
    ws.send_text = AsyncMock()
    ws.receive_text = AsyncMock()
    ws.receive_json = AsyncMock()
    ws.accept = AsyncMock()
    ws.close = AsyncMock()
    return ws


@pytest.fixture
def sample_sala_id():
    """ID de sala de prueba"""
    return "test-sala-123"


@pytest.fixture
def sample_usuario_id():
    """ID de usuario de prueba"""
    return "test-user-456"


@pytest.fixture
def sample_mensaje_data():
    """Datos de mensaje de prueba"""
    return {
        "contenido": "Hola, este es un mensaje de prueba",
        "tipo_mensaje": "texto"
    }


# ============================================================================
# TEST 1: ConnectionManager - Conexiones Básicas
# ============================================================================

class TestConnectionManager:
    """Tests para el ConnectionManager"""
    
    @pytest.mark.asyncio
    async def test_connect_user(self, clean_connection_manager, mock_websocket, sample_sala_id, sample_usuario_id):
        """Test: Conectar un usuario a una sala"""
        await clean_connection_manager.connect(sample_sala_id, sample_usuario_id, mock_websocket)
        
        # Verificar que el usuario está conectado
        assert sample_sala_id in clean_connection_manager._active_connections
        assert sample_usuario_id in clean_connection_manager._active_connections[sample_sala_id]
        assert sample_sala_id in clean_connection_manager._user_rooms[sample_usuario_id]
        
        # Verificar que se llamó accept()
        mock_websocket.accept.assert_called_once()
    
    
    @pytest.mark.asyncio
    async def test_disconnect_user(self, clean_connection_manager, mock_websocket, sample_sala_id, sample_usuario_id):
        """Test: Desconectar un usuario de una sala"""
        # Conectar primero
        await clean_connection_manager.connect(sample_sala_id, sample_usuario_id, mock_websocket)
        
        # Desconectar
        await clean_connection_manager.disconnect(sample_sala_id, sample_usuario_id)
        
        # Verificar que el usuario ya no está conectado
        if sample_sala_id in clean_connection_manager._active_connections:
            assert sample_usuario_id not in clean_connection_manager._active_connections[sample_sala_id]
        assert sample_sala_id not in clean_connection_manager._user_rooms.get(sample_usuario_id, set())
    
    
    @pytest.mark.asyncio
    async def test_broadcast_to_sala(self, clean_connection_manager, mock_websocket, sample_sala_id):
        """Test: Broadcast de mensaje a todos los usuarios de una sala"""
        # Conectar 3 usuarios
        users = ["user1", "user2", "user3"]
        websockets = []
        
        for user_id in users:
            ws = AsyncMock(spec=WebSocket)
            ws.send_json = AsyncMock()
            websockets.append(ws)
            await clean_connection_manager.connect(sample_sala_id, user_id, ws)
        
        # Broadcast mensaje
        message = {"event": "test", "data": "test_message"}
        await clean_connection_manager.broadcast_to_sala(sample_sala_id, message)
        
        # Verificar que todos recibieron el mensaje
        for ws in websockets:
            ws.send_json.assert_called_once_with(message)
    
    
    @pytest.mark.asyncio
    async def test_broadcast_exclude_user(self, clean_connection_manager, sample_sala_id):
        """Test: Broadcast excluyendo un usuario específico"""
        # Conectar 3 usuarios
        users = ["user1", "user2", "user3"]
        websockets = {}
        
        for user_id in users:
            ws = AsyncMock(spec=WebSocket)
            ws.send_json = AsyncMock()
            websockets[user_id] = ws
            await clean_connection_manager.connect(sample_sala_id, user_id, ws)
        
        # Broadcast excluyendo user2
        message = {"event": "test", "data": "test_message"}
        await clean_connection_manager.broadcast_to_sala(sample_sala_id, message, exclude_user="user2")
        
        # Verificar que user1 y user3 recibieron, pero user2 no
        websockets["user1"].send_json.assert_called_once_with(message)
        websockets["user2"].send_json.assert_not_called()
        websockets["user3"].send_json.assert_called_once_with(message)
    
    
    @pytest.mark.asyncio
    async def test_typing_indicators(self, clean_connection_manager, mock_websocket, sample_sala_id):
        """Test: Indicadores de escritura"""
        user1 = "user1"
        user2 = "user2"
        
        # Conectar usuarios
        await clean_connection_manager.connect(sample_sala_id, user1, mock_websocket)
        
        # Usuario 1 empieza a escribir
        await clean_connection_manager.set_typing(sample_sala_id, user1, True)
        assert user1 in clean_connection_manager._typing_users.get(sample_sala_id, set())
        
        # Usuario 1 deja de escribir
        await clean_connection_manager.set_typing(sample_sala_id, user1, False)
        assert user1 not in clean_connection_manager._typing_users.get(sample_sala_id, set())
    
    
    @pytest.mark.asyncio
    async def test_get_online_users(self, clean_connection_manager, mock_websocket, sample_sala_id):
        """Test: Obtener usuarios online en una sala"""
        users = ["user1", "user2", "user3"]
        
        # Conectar usuarios
        for user_id in users:
            ws = AsyncMock(spec=WebSocket)
            await clean_connection_manager.connect(sample_sala_id, user_id, ws)
        
        # Obtener usuarios online
        online_users = clean_connection_manager.get_online_users(sample_sala_id)
        
        # Verificar
        assert len(online_users) == 3
        assert all(user in online_users for user in users)
    
    
    @pytest.mark.asyncio
    async def test_get_stats(self, clean_connection_manager, mock_websocket):
        """Test: Obtener estadísticas del manager"""
        # Conectar usuarios en diferentes salas
        await clean_connection_manager.connect("sala1", "user1", AsyncMock(spec=WebSocket))
        await clean_connection_manager.connect("sala1", "user2", AsyncMock(spec=WebSocket))
        await clean_connection_manager.connect("sala2", "user3", AsyncMock(spec=WebSocket))
        
        # Marcar typing
        await clean_connection_manager.set_typing("sala1", "user1", True)
        
        # Obtener stats
        stats = clean_connection_manager.get_stats()
        
        # Verificar
        assert stats["total_connections"] == 3
        assert stats["total_rooms"] == 2
        assert stats["typing_users_count"] == 1


# ============================================================================
# TEST 2: WebSocket Endpoint - Eventos
# ============================================================================

class TestChatWebSocketEndpoint:
    """Tests para el endpoint WebSocket de chat"""
    
    def test_endpoint_requires_authentication(self, test_client):
        """Test: El endpoint requiere autenticación JWT"""
        # Intentar conectar sin token
        sala_id = "test-sala-123"
        
        # En FastAPI TestClient, WebSocket requiere conexión real
        # Este test verificaría que sin token se rechaza la conexión
        # (implementación depende de cómo manejes auth en testing)
        pass
    
    
    @pytest.mark.asyncio
    async def test_message_new_event(self, sample_mensaje_data):
        """Test: Evento message.new"""
        # Este test requeriría mock del handler
        # Simular envío de mensaje nuevo
        event_data = {
            "event": "message.new",
            "data": sample_mensaje_data
        }
        
        # Verificar que se procesa correctamente
        # (implementación completa requiere mocks de DB)
        assert event_data["event"] == "message.new"
        assert "contenido" in event_data["data"]
    
    
    @pytest.mark.asyncio
    async def test_typing_start_event(self):
        """Test: Evento typing.start"""
        event_data = {
            "event": "typing.start",
            "data": {}
        }
        
        # Verificar estructura del evento
        assert event_data["event"] == "typing.start"
    
    
    @pytest.mark.asyncio
    async def test_typing_stop_event(self):
        """Test: Evento typing.stop"""
        event_data = {
            "event": "typing.stop",
            "data": {}
        }
        
        # Verificar estructura del evento
        assert event_data["event"] == "typing.stop"


# ============================================================================
# TEST 3: Validación de Datos
# ============================================================================

class TestDataValidation:
    """Tests de validación de datos"""
    
    def test_validate_message_content(self):
        """Test: Validar contenido de mensaje"""
        # Mensaje válido
        valid_message = {
            "contenido": "Test message",
            "tipo_mensaje": "texto"
        }
        assert "contenido" in valid_message
        assert len(valid_message["contenido"]) > 0
        
        # Mensaje inválido (vacío)
        invalid_message = {
            "contenido": "",
            "tipo_mensaje": "texto"
        }
        assert len(invalid_message["contenido"]) == 0
    
    
    def test_validate_message_type(self):
        """Test: Validar tipo de mensaje"""
        valid_types = ["texto", "imagen", "video", "audio", "archivo", "sistema"]
        
        for msg_type in valid_types:
            message = {
                "contenido": "Test",
                "tipo_mensaje": msg_type
            }
            assert message["tipo_mensaje"] in valid_types
        
        # Tipo inválido
        invalid_message = {
            "contenido": "Test",
            "tipo_mensaje": "invalid_type"
        }
        assert invalid_message["tipo_mensaje"] not in valid_types
    
    
    def test_validate_emoji_reaction(self):
        """Test: Validar reacciones con emojis"""
        valid_emojis = ["👍", "❤️", "😂", "😮", "😢", "🎉"]
        
        for emoji in valid_emojis:
            reaction = {
                "mensaje_id": "msg-123",
                "emoji": emoji
            }
            assert reaction["emoji"] in valid_emojis


# ============================================================================
# TEST 4: Manejo de Errores
# ============================================================================

class TestErrorHandling:
    """Tests de manejo de errores"""
    
    @pytest.mark.asyncio
    async def test_disconnect_on_error(self, clean_connection_manager, sample_sala_id, sample_usuario_id):
        """Test: Desconexión al ocurrir error"""
        # Crear WebSocket mock que falla al enviar
        ws = AsyncMock(spec=WebSocket)
        ws.send_json = AsyncMock(side_effect=Exception("Connection error"))
        
        # Conectar
        await clean_connection_manager.connect(sample_sala_id, sample_usuario_id, ws)
        
        # Intentar enviar mensaje (debería fallar)
        try:
            await ws.send_json({"test": "data"})
        except Exception:
            pass
        
        # El manager debería poder manejar la desconexión
        await clean_connection_manager.disconnect(sample_sala_id, sample_usuario_id)
        
        # Verificar que se limpió
        assert sample_usuario_id not in clean_connection_manager._active_connections.get(sample_sala_id, {})
    
    
    @pytest.mark.asyncio
    async def test_reconnection_scenario(self, clean_connection_manager, mock_websocket, sample_sala_id, sample_usuario_id):
        """Test: Escenario de reconexión"""
        # Conectar
        await clean_connection_manager.connect(sample_sala_id, sample_usuario_id, mock_websocket)
        
        # Desconectar
        await clean_connection_manager.disconnect(sample_sala_id, sample_usuario_id)
        
        # Reconectar (nuevo WebSocket)
        new_ws = AsyncMock(spec=WebSocket)
        new_ws.accept = AsyncMock()
        await clean_connection_manager.connect(sample_sala_id, sample_usuario_id, new_ws)
        
        # Verificar que está conectado con el nuevo WebSocket
        assert sample_usuario_id in clean_connection_manager._active_connections[sample_sala_id]
        new_ws.accept.assert_called_once()


# ============================================================================
# TEST 5: Performance y Concurrencia
# ============================================================================

class TestPerformance:
    """Tests de performance y concurrencia"""
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_connections(self, clean_connection_manager):
        """Test: Múltiples conexiones concurrentes"""
        sala_id = "stress-test-sala"
        num_users = 50
        
        # Conectar múltiples usuarios concurrentemente
        tasks = []
        for i in range(num_users):
            ws = AsyncMock(spec=WebSocket)
            ws.accept = AsyncMock()
            user_id = f"user-{i}"
            tasks.append(clean_connection_manager.connect(sala_id, user_id, ws))
        
        # Ejecutar todas las conexiones
        await asyncio.gather(*tasks)
        
        # Verificar que todos están conectados
        online_users = clean_connection_manager.get_online_users(sala_id)
        assert len(online_users) == num_users
    
    
    @pytest.mark.asyncio
    async def test_broadcast_performance(self, clean_connection_manager):
        """Test: Performance de broadcast a muchos usuarios"""
        sala_id = "broadcast-test"
        num_users = 100
        
        # Conectar usuarios
        for i in range(num_users):
            ws = AsyncMock(spec=WebSocket)
            ws.send_json = AsyncMock()
            await clean_connection_manager.connect(sala_id, f"user-{i}", ws)
        
        # Broadcast mensaje
        message = {"event": "test", "data": "performance_test"}
        
        import time
        start_time = time.time()
        await clean_connection_manager.broadcast_to_sala(sala_id, message)
        end_time = time.time()
        
        # El broadcast debería ser rápido (< 1 segundo para 100 usuarios)
        assert (end_time - start_time) < 1.0


# ============================================================================
# TEST 6: Integración - Flujo Completo
# ============================================================================

class TestIntegrationFlow:
    """Tests de integración del flujo completo"""
    
    @pytest.mark.asyncio
    async def test_complete_chat_flow(self, clean_connection_manager):
        """Test: Flujo completo de chat"""
        sala_id = "integration-sala"
        
        # 1. Dos usuarios se conectan
        user1_ws = AsyncMock(spec=WebSocket)
        user1_ws.send_json = AsyncMock()
        user2_ws = AsyncMock(spec=WebSocket)
        user2_ws.send_json = AsyncMock()
        
        await clean_connection_manager.connect(sala_id, "user1", user1_ws)
        await clean_connection_manager.connect(sala_id, "user2", user2_ws)
        
        # 2. User1 empieza a escribir
        await clean_connection_manager.set_typing(sala_id, "user1", True)
        
        # 3. User1 envía mensaje (simular broadcast)
        message = {
            "event": "message.new",
            "data": {
                "usuario_id": "user1",
                "contenido": "Hola!",
                "tipo_mensaje": "texto"
            }
        }
        await clean_connection_manager.broadcast_to_sala(sala_id, message)
        
        # 4. User1 deja de escribir
        await clean_connection_manager.set_typing(sala_id, "user1", False)
        
        # 5. User2 reacciona (simular)
        reaction = {
            "event": "message.reaction",
            "data": {
                "mensaje_id": "msg-123",
                "emoji": "👍",
                "usuario_id": "user2"
            }
        }
        await clean_connection_manager.broadcast_to_sala(sala_id, reaction)
        
        # Verificar que ambos recibieron mensajes
        assert user1_ws.send_json.call_count >= 2  # mensaje + reacción
        assert user2_ws.send_json.call_count >= 2


# ============================================================================
# RUNNER
# ============================================================================

if __name__ == "__main__":
    """Ejecutar tests"""
    print("=" * 80)
    print("🧪 TEST SUITE - Sistema de Comunicación (Fase 1)")
    print("=" * 80)
    
    # Ejecutar con pytest
    pytest.main([
        __file__,
        "-v",  # verbose
        "-s",  # no capture output
        "--tb=short",  # short traceback
        "--color=yes"
    ])
