"""Tracker de costos y uso de tokens para servicios de IA.

Registra y analiza el uso de tokens para control de costos y
optimización del servicio.

Author: Gemini AI Assistant
Date: 31 octubre 2025
"""

from collections import defaultdict
from datetime import datetime, timedelta
import json
import logging
from typing import Any

from src.services.ai.config import GEMINI_PRICING


logger = logging.getLogger(__name__)


class CostTracker:
    """Rastreador de costos y uso de tokens.

    Mantiene estadísticas detalladas de:
    - Tokens consumidos por tipo (input/output)
    - Costos estimados (plan gratuito vs pagado)
    - Requests por minuto/día
    - Alertas de límites
    """

    def __init__(self, modelo: str = "gemini-1.5-flash") -> None:
        """Inicializa el tracker.

        Args:
            modelo: Modelo de Gemini utilizado
        """
        self.modelo = modelo
        self.registros: list[dict[str, Any]] = []
        self._tokens_por_periodo: dict[str, int] = defaultdict(int)
        self._requests_por_periodo: dict[str, int] = defaultdict(int)

    def registrar_uso(
        self,
        tokens_input: int,
        tokens_output: int,
        duracion_segundos: float,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Registra el uso de una llamada a la API.

        Args:
            tokens_input: Tokens del prompt
            tokens_output: Tokens de la respuesta
            duracion_segundos: Tiempo de la llamada
            metadata: Información adicional (usuario_id, tarea_id, etc.)
        """
        timestamp = datetime.utcnow()

        registro = {
            "timestamp": timestamp.isoformat(),
            "modelo": self.modelo,
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
            "tokens_total": tokens_input + tokens_output,
            "duracion_segundos": round(duracion_segundos, 2),
            "metadata": metadata or {},
        }

        self.registros.append(registro)

        # Actualizar contadores por período
        minuto_actual = timestamp.strftime("%Y-%m-%d %H:%M")
        dia_actual = timestamp.strftime("%Y-%m-%d")

        self._tokens_por_periodo[minuto_actual] += registro["tokens_total"]
        self._requests_por_periodo[minuto_actual] += 1
        self._requests_por_periodo[dia_actual] += 1

        logger.debug(
            f"Uso registrado: {tokens_input}+{tokens_output}={registro['tokens_total']} tokens "
            f"en {duracion_segundos:.2f}s"
        )

    def calcular_costo_estimado(self, plan: str = "free") -> dict[str, float]:
        """Calcula el costo estimado del uso acumulado.

        Args:
            plan: "free" o "paid"

        Returns:
            Dict con costos desglosados (USD)
        """
        if not self.registros:
            return {
                "costo_input": 0.0,
                "costo_output": 0.0,
                "costo_total": 0.0,
                "en_plan_gratuito": True,
            }

        pricing = GEMINI_PRICING.get(self.modelo, GEMINI_PRICING["gemini-1.5-flash"])

        total_tokens_input = sum(r["tokens_input"] for r in self.registros)
        total_tokens_output = sum(r["tokens_output"] for r in self.registros)

        if plan == "free":
            # Plan gratuito no tiene costo pero tiene límites
            return {
                "costo_input": 0.0,
                "costo_output": 0.0,
                "costo_total": 0.0,
                "en_plan_gratuito": True,
                "tokens_input": total_tokens_input,
                "tokens_output": total_tokens_output,
                "limite_gratis_excedido": self.verificar_limites_plan_gratuito(),
            }

        # Plan pagado
        # Calcular costo por millón de tokens
        costo_input = (total_tokens_input / 1_000_000) * pricing["paid_tier"][
            "input_per_1m_tokens"
        ]
        costo_output = (total_tokens_output / 1_000_000) * pricing["paid_tier"][
            "output_per_1m_tokens"
        ]

        return {
            "costo_input": round(costo_input, 4),
            "costo_output": round(costo_output, 4),
            "costo_total": round(costo_input + costo_output, 4),
            "en_plan_gratuito": False,
            "tokens_input": total_tokens_input,
            "tokens_output": total_tokens_output,
        }

    def verificar_limites_plan_gratuito(self) -> dict[str, Any]:
        """Verifica si se están excediendo los límites del plan gratuito.

        Returns:
            Dict con estado de límites:
            {
                "excede_rpm": bool,
                "excede_tpm": bool,
                "excede_rpd": bool,
                "requests_este_minuto": int,
                "tokens_este_minuto": int,
                "requests_hoy": int
            }
        """
        pricing = GEMINI_PRICING.get(self.modelo, GEMINI_PRICING["gemini-1.5-flash"])
        limites = pricing["free_tier"]

        now = datetime.utcnow()
        minuto_actual = now.strftime("%Y-%m-%d %H:%M")
        dia_actual = now.strftime("%Y-%m-%d")

        requests_este_minuto = self._requests_por_periodo.get(minuto_actual, 0)
        tokens_este_minuto = self._tokens_por_periodo.get(minuto_actual, 0)
        requests_hoy = self._requests_por_periodo.get(dia_actual, 0)

        return {
            "excede_rpm": requests_este_minuto >= limites["requests_per_minute"],
            "excede_tpm": tokens_este_minuto >= limites["tokens_per_minute"],
            "excede_rpd": requests_hoy >= limites["requests_per_day"],
            "requests_este_minuto": requests_este_minuto,
            "limite_rpm": limites["requests_per_minute"],
            "tokens_este_minuto": tokens_este_minuto,
            "limite_tpm": limites["tokens_per_minute"],
            "requests_hoy": requests_hoy,
            "limite_rpd": limites["requests_per_day"],
        }

    def obtener_estadisticas(self, periodo_dias: int = 7) -> dict[str, Any]:
        """Obtiene estadísticas de uso para un período.

        Args:
            periodo_dias: Días hacia atrás a incluir

        Returns:
            Dict con estadísticas detalladas
        """
        if not self.registros:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "promedio_tokens_por_request": 0,
                "promedio_duracion_segundos": 0,
            }

        fecha_limite = datetime.utcnow() - timedelta(days=periodo_dias)

        registros_periodo = [
            r
            for r in self.registros
            if datetime.fromisoformat(r["timestamp"]) >= fecha_limite
        ]

        if not registros_periodo:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "promedio_tokens_por_request": 0,
                "promedio_duracion_segundos": 0,
            }

        total_tokens = sum(r["tokens_total"] for r in registros_periodo)
        total_duracion = sum(r["duracion_segundos"] for r in registros_periodo)

        return {
            "periodo_dias": periodo_dias,
            "total_requests": len(registros_periodo),
            "total_tokens": total_tokens,
            "total_tokens_input": sum(r["tokens_input"] for r in registros_periodo),
            "total_tokens_output": sum(r["tokens_output"] for r in registros_periodo),
            "promedio_tokens_por_request": round(
                total_tokens / len(registros_periodo), 1
            ),
            "promedio_duracion_segundos": round(
                total_duracion / len(registros_periodo), 2
            ),
            "duracion_total_minutos": round(total_duracion / 60, 2),
            "costo_estimado": self.calcular_costo_estimado(plan="paid"),
        }

    def obtener_uso_por_dia(self, ultimos_dias: int = 7) -> dict[str, dict[str, int]]:
        """Obtiene uso desglosado por día.

        Args:
            ultimos_dias: Número de días a incluir

        Returns:
            Dict con datos por día: {"2025-10-31": {"requests": 10, "tokens": 50000}}
        """
        fecha_limite = datetime.utcnow() - timedelta(days=ultimos_dias)

        uso_por_dia = defaultdict(lambda: {"requests": 0, "tokens": 0})

        for registro in self.registros:
            timestamp = datetime.fromisoformat(registro["timestamp"])
            if timestamp >= fecha_limite:
                dia = timestamp.strftime("%Y-%m-%d")
                uso_por_dia[dia]["requests"] += 1
                uso_por_dia[dia]["tokens"] += registro["tokens_total"]

        return dict(uso_por_dia)

    def limpiar_registros_antiguos(self, dias_conservar: int = 30) -> None:
        """Elimina registros más antiguos que X días.

        Args:
            dias_conservar: Días de historial a mantener
        """
        fecha_limite = datetime.utcnow() - timedelta(days=dias_conservar)

        registros_antiguos = len(self.registros)
        self.registros = [
            r
            for r in self.registros
            if datetime.fromisoformat(r["timestamp"]) >= fecha_limite
        ]

        eliminados = registros_antiguos - len(self.registros)

        if eliminados > 0:
            logger.info(
                f"Limpiados {eliminados} registros antiguos (>{dias_conservar} días)"
            )

    def exportar_registros(self, archivo_salida: str, formato: str = "json") -> None:
        """Exporta registros a un archivo.

        Args:
            archivo_salida: Path del archivo de salida
            formato: "json" o "csv"
        """
        if formato == "json":
            with open(archivo_salida, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "modelo": self.modelo,
                        "exportado_en": datetime.utcnow().isoformat(),
                        "total_registros": len(self.registros),
                        "registros": self.registros,
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

        elif formato == "csv":
            import csv

            with open(archivo_salida, "w", newline="", encoding="utf-8") as f:
                if not self.registros:
                    return

                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "timestamp",
                        "modelo",
                        "tokens_input",
                        "tokens_output",
                        "tokens_total",
                        "duracion_segundos",
                    ],
                )
                writer.writeheader()

                for r in self.registros:
                    writer.writerow(
                        {
                            "timestamp": r["timestamp"],
                            "modelo": r["modelo"],
                            "tokens_input": r["tokens_input"],
                            "tokens_output": r["tokens_output"],
                            "tokens_total": r["tokens_total"],
                            "duracion_segundos": r["duracion_segundos"],
                        }
                    )

        logger.info(f"Registros exportados a {archivo_salida}")

    def generar_alerta_limites(self) -> str | None:
        """Genera mensaje de alerta si se están acercando a límites.

        Returns:
            str: Mensaje de alerta o None si todo está bien
        """
        limites = self.verificar_limites_plan_gratuito()
        alertas = []

        # Alertar si se está cerca (80%) de los límites
        if limites["requests_este_minuto"] >= limites["limite_rpm"] * 0.8:
            alertas.append(
                f"⚠️ Cerca del límite RPM: "
                f"{limites['requests_este_minuto']}/{limites['limite_rpm']}"
            )

        if limites["tokens_este_minuto"] >= limites["limite_tpm"] * 0.8:
            alertas.append(
                f"⚠️ Cerca del límite TPM: "
                f"{limites['tokens_este_minuto']:,}/{limites['limite_tpm']:,}"
            )

        if limites["requests_hoy"] >= limites["limite_rpd"] * 0.8:
            alertas.append(
                f"⚠️ Cerca del límite RPD: "
                f"{limites['requests_hoy']}/{limites['limite_rpd']}"
            )

        if limites["excede_rpm"] or limites["excede_tpm"] or limites["excede_rpd"]:
            alertas.append(
                "🚫 ¡LÍMITE EXCEDIDO! Considera usar rate limiting o plan pagado"
            )

        return "\n".join(alertas) if alertas else None

    def __repr__(self) -> str:
        stats = self.obtener_estadisticas(periodo_dias=1)
        return (
            f"CostTracker(modelo={self.modelo}, "
            f"requests={stats['total_requests']}, "
            f"tokens={stats['total_tokens']:,})"
        )
