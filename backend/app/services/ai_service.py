# backend/app/services/ai_service.py
"""
Servicio de IA avanzado para Acadify
- Chat educativo
- Retroalimentación de tareas
- Sugerencia de recursos
- Caching, control de tokens y multi-contexto
"""

import asyncio
from typing import Dict, Optional, Any
from collections import deque

import openai
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import log_error
from app.models.chatbot import MessageContext

# Importa las instancias reales del CRUD y crea aliases para compatibilidad
from app.crud.chat import chat_bot, faq_bot, bot_message

# Aliases (permiten seguir usando los nombres antiguos en el resto del código)
chatbot_crud = chat_bot
faq_crud = faq_bot
bot_message_crud = bot_message


class AIServiceAdvanced:
    """Servicio avanzado de IA para producción"""

    def __init__(self, max_history: int = 10):
        self.openai_client = None
        self.max_history = max_history
        self.user_history: Dict[str, deque] = {}  # historial de mensajes por usuario
        self.response_cache: Dict[str, str] = {}  # cache simple por mensaje
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_client = openai

    # -------------------------------
    # Chat principal con historial y caching
    # -------------------------------
    async def generate_chat_response(
        self,
        user_message: str,
        context: MessageContext,
        user_id: str,
        db: Session,
        course_id: Optional[str] = None,
        material_id: Optional[str] = None
    ) -> str:
        """Genera respuesta usando IA avanzada"""
        try:
            # 1. Revisar cache
            cache_key = f"{user_id}:{user_message}"
            if cache_key in self.response_cache:
                return self.response_cache[cache_key]

            # 2. Buscar en FAQ
            faq_response = await self._search_faq(user_message, db)
            if faq_response:
                return faq_response

            # 3. Construir contexto y prompt con historial
            context_data = await self._build_context(user_message, context, user_id, db, course_id, material_id)
            prompt = self._build_prompt_with_history(user_id, user_message, context_data)

            # 4. Llamar OpenAI
            response = await self._call_openai(prompt)

            # 5. Guardar en historial y cache
            self._add_to_history(user_id, user_message, response)
            self.response_cache[cache_key] = response

            # 6. Guardar interacción en DB
            await self._save_bot_interaction(user_id, user_message, response, context, db, course_id, material_id)

            return response

        except Exception as e:
            log_error(e, "AI_SERVICE_ADVANCED_CHAT")
            return await self._generate_fallback_response(user_message, getattr(context, "value", "general"))

    # -------------------------------
    # Historial y caching
    # -------------------------------
    def _add_to_history(self, user_id: str, user_message: str, bot_response: str):
        """Agrega mensaje y respuesta al historial"""
        if user_id not in self.user_history:
            self.user_history[user_id] = deque(maxlen=self.max_history)
        self.user_history[user_id].append({"user": user_message, "bot": bot_response})

    def _build_prompt_with_history(self, user_id: str, user_message: str, context_data: Dict[str, Any]) -> str:
        """Construye prompt incluyendo historial de conversación"""
        base_prompt = self._build_educational_prompt(context_data)
        history = self.user_history.get(user_id, [])
        for h in history:
            base_prompt += f"\nUsuario: {h['user']}\nBot: {h['bot']}"
        base_prompt += f"\nUsuario: {user_message}\nBot:"
        return base_prompt

    # -------------------------------
    # Funciones internas
    # -------------------------------
    async def _call_openai(self, prompt: str) -> str:
        try:
            if not self.openai_client:
                return "IA no disponible temporalmente."

            # ChatCompletion es una llamada bloqueante -> correr en executor
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.openai_client.ChatCompletion.create(
                    model=settings.AI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.7
                )
            )
            # Extraer contenido
            # Nota: la estructura puede variar según la versión de la librería
            choice = response.choices[0]
            # Compatibilidad: choice.message.content o choice['message']['content']
            if hasattr(choice, "message") and hasattr(choice.message, "content"):
                return choice.message.content.strip()
            # fallback:
            return str(choice).strip()
        except Exception as e:
            log_error(e, "AI_SERVICE_ADVANCED_OPENAI")
            return "No pude procesar tu mensaje. Por favor intenta más tarde."

    async def _search_faq(self, user_message: str, db: Session) -> Optional[str]:
        """
        Busca en las FAQs. Usa el método `search` que sí existe en CRUDFAQBot.
        Antes se intentó usar `search_by_keywords` (no existe).
        """
        try:
            # usa el método `search(db, query=...)` implementado en CRUDFAQBot
            faqs = faq_crud.search(db, query=user_message.lower())
            if faqs:
                return faqs[0].answer
            return None
        except Exception as e:
            log_error(e, "AI_SERVICE_ADVANCED_SEARCH_FAQ")
            return None

    async def _save_bot_interaction(
        self, user_id: str, user_message: str, bot_response: str,
        context: MessageContext, db: Session,
        course_id: Optional[str] = None, material_id: Optional[str] = None
    ):
        try:
            # obtener bot por defecto usando el método disponible en CRUDChatBot
            default_bot = chatbot_crud.get_default(db)
            if not default_bot:
                default_bot = await self._create_default_bot(db)

            # Crear mensaje del bot (obj_in puede ser dict o schema; CRUDBase normalmente acepta schema)
            bot_message_crud.create(db, obj_in={
                "user_id": user_id,
                "chatbot_id": str(default_bot.id),
                "content": user_message,
                "response": bot_response,
                "context": getattr(context, "value", str(context)),
                "referenced_material_id": material_id
            })
        except Exception as e:
            log_error(e, "AI_SERVICE_ADVANCED_SAVE")

    async def _create_default_bot(self, db: Session):
        from app.schemas.chat import ChatBotCreate
        bot_data = ChatBotCreate(
            name="AcadifyBot",
            description="Asistente educativo inteligente de Acadify",
            profile_image_url="/static/images/acadify_bot.png",
            is_active=True
        )
        return chatbot_crud.create(db, obj_in=bot_data)

    def _build_educational_prompt(self, context_data: Dict[str, Any]) -> str:
        base_prompt = (
            "Eres un asistente educativo especializado. Mantén un tono profesional y motivador.\n"
            "Contexto de la conversación:"
        )
        context_type = context_data.get("context_type", "general")
        if context_type == "course":
            course_info = context_data.get("course_info", {})
            base_prompt += f"\nCurso: {course_info.get('name','N/A')} - Descripción: {course_info.get('description','N/A')}"
        elif context_type == "material":
            material_info = context_data.get("material_info", {})
            base_prompt += f"\nMaterial: {material_info.get('title','N/A')} - Tipo: {material_info.get('type','N/A')}"
        base_prompt += "\nResponde en español, sé conciso y motivador.\n"
        return base_prompt

    async def _generate_fallback_response(self, user_message: str, context_type: str) -> str:
        fallback_responses = {
            "general": "Un docente podrá ayudarte pronto.",
            "course": "Revisa el material o contacta al docente.",
            "material": "Consulta el material o pide ayuda a tu docente."
        }
        return fallback_responses.get(context_type, fallback_responses["general"])


# Instancia global del servicio de IA avanzado
ai_service = AIServiceAdvanced()
