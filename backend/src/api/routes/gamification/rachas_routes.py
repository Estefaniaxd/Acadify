"""Rutas para el sistema de rachas diarias."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_user, get_db
from src.models.users.usuario import Usuario
from src.services.gamification.racha_service import RachaService


router = APIRouter(tags=["Gamificación - Rachas"])


@router.post("/registrar", summary="Registrar acceso diario")
async def registrar_acceso_diario(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Registra el acceso diario del usuario y actualiza su racha.

    - **Incrementa racha**: Si accedió ayer
    - **Reinicia racha**: Si no accedió ayer (y no está congelada)
    - **Otorga recompensa**: Puntos según día del ciclo semanal
    - **Puede llamarse solo 1 vez por día**

    Retorna información sobre:
    - Racha actual y mejor racha
    - Puntos obtenidos
    - Día del ciclo (1-7)
    - Próxima recompensa
    - Si es nuevo récord personal
    """
    service = RachaService(db)
    return await service.registrar_acceso_diario(current_user.usuario_id)


@router.get("/mi-racha", summary="Obtener estado de mi racha")
async def obtener_mi_racha(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene el estado completo de la racha del usuario actual.

    Incluye:
    - **racha_actual**: Días consecutivos
    - **mejor_racha**: Récord personal
    - **ya_registro_hoy**: Si ya registró hoy
    - **en_riesgo**: Si la racha está en peligro
    - **dia_ciclo_actual**: Día en el ciclo semanal (1-7)
    - **proxima_recompensa**: Puntos y mensaje del próximo día
    - **recuperaciones_disponibles**: Recuperaciones para usar
    - **esta_congelada**: Si tiene protección activa
    """
    service = RachaService(db)
    return await service.get_estadisticas_racha(current_user.usuario_id)


@router.post("/usar-recuperacion", summary="Usar recuperación de racha")
async def usar_recuperacion(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Usa una recuperación para salvar la racha perdida.

    - **Requiere**: Tener al menos 1 recuperación disponible
    - **Efecto**: Simula que registraste ayer
    - **Uso**: Solo cuando la racha está en riesgo

    Las recuperaciones se ganan cada 7 días de racha consecutiva.
    """
    service = RachaService(db)
    return await service.usar_recuperacion(current_user.usuario_id)


@router.post("/congelar", summary="Congelar racha (requiere item)")
async def congelar_racha(
    dias: int = 1,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Congela la racha por X días usando un item funcional de la tienda.

    - **dias**: Número de días a congelar (1-7)
    - **Requiere**: Item "Congelador de Racha" en inventario
    - **Efecto**: La racha no se pierde aunque no accedas

    Los items de congelación se compran en la tienda con puntos.
    """
    if dias < 1 or dias > 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los días deben estar entre 1 y 7",
        )

    # TODO: Verificar que tenga el item en inventario y consumirlo

    service = RachaService(db)
    return await service.congelar_racha(current_user.usuario_id, dias)


@router.get("/historial", summary="Obtener historial de rachas")
async def obtener_historial(
    limite: int = 10,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene el historial de rachas del usuario.

    - **limite**: Número máximo de rachas a retornar (default: 10)

    Muestra rachas anteriores con:
    - Días alcanzados
    - Fechas de inicio y fin
    - Cómo terminó (perdida, recuperación, etc.)
    - Puntos ganados totales
    """
    service = RachaService(db)
    historial = await service.obtener_historial(current_user.usuario_id, limite)

    return {"historial": historial, "total": len(historial)}


@router.get("/recompensas", summary="Obtener recompensas recientes")
async def obtener_recompensas(
    limite: int = 7,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene las recompensas de racha recientes.

    - **limite**: Número máximo de recompensas (default: 7)

    Muestra:
    - Día de racha
    - Día del ciclo semanal
    - Puntos otorgados
    - Fecha de obtención
    """
    service = RachaService(db)
    recompensas = await service.obtener_recompensas_recientes(
        current_user.usuario_id, limite
    )

    return {"recompensas": recompensas, "total": len(recompensas)}


@router.get("/estadisticas-globales", summary="Estadísticas globales de rachas")
async def obtener_estadisticas_globales(db: Session = Depends(get_db)):
    """Obtiene estadísticas globales del sistema de rachas.

    **Endpoint público** que muestra:
    - Mayor racha actual en el sistema
    - Mejor racha histórica de todos los tiempos
    - Usuarios activos hoy
    - Total de rachas activas

    Útil para mostrar en un leaderboard o dashboard.
    """
    service = RachaService(db)
    return await service.obtener_estadisticas_globales()


@router.get(
    "/calendario-recompensas", summary="Ver calendario de recompensas semanales"
)
async def obtener_calendario_recompensas():
    """Obtiene el calendario de recompensas del ciclo semanal.

    Muestra qué puntos se obtienen cada día del ciclo (1-7).
    Útil para que los usuarios sepan qué esperar.
    """
    from src.services.gamification.racha_service import RachaService

    return {
        "ciclo": "semanal",
        "recompensas": RachaService.RECOMPENSAS_POR_DIA,
        "descripcion": "Las recompensas se repiten cada 7 días",
    }
