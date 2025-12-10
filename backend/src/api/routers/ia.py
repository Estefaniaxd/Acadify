"""""""""

⚡ IA Feedback - Router INTEGRADO CON GEMINI

⚡ IA Feedback - Router INTEGRADO CON GEMINI⚡ IA Feedback - Router INTEGRADO CON GEMINI

Endpoints para retroalimentación automática con IA usando Google Gemini:

- Retroalimentación individual de tareas

- Retroalimentación masiva (bulk)

- Información de modelos disponiblesEndpoints para retroalimentación automática con IA usando Google Gemini:Endpoints para retroalimentación automática con IA usando Google Gemini:



IMPORTANTE: Este router usa GeminiService de backend/src/services/ai/- Retroalimentación individual de tareas- Retroalimentación individual de tareas

Escribe en la columna retroalimentacion_ia (JSONB) de entregas_tareas

"""- Retroalimentación masiva (bulk)- Retroalimentación masiva (bulk)



from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks- Calificación automática- Calificación automática

from pydantic import BaseModel, Field

from typing import Optional- Gestión de modelos IA- Gestión de modelos IA

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, update

from uuid import uuid4

from datetime import datetimeIMPORTANTE: Este router usa GeminiService de backend/src/services/ai/IMPORTANTE: Este router usa GeminiService de backend/src/services/ai/

import logging

Escribe en la columna retroalimentacion_ia (JSONB) de entregas_tareasNo es un mock - es INTEGRACIÓN REAL con Google Generative AI API

from src.db.database import get_db

from src.core.security import get_current_user"""

from src.models.usuario import Usuario

from src.models.academic.tarea import Tarea, EntregaTareaBase de datos:

from src.models.retroalimentacion_ia import (

    RetroalimentacionIASchema,- entregas_tareas.retroalimentacion_ia (JSONB) - almacena retroalimentación generadafrom fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

    crear_retroalimentacion_dict,

    parsear_retroalimentacion- entregas_tareas.retroalimentacion_docente (TEXT) - retroalimentación manual del docentefrom pydantic import BaseModel, Field

)

from src.services.ai import GeminiService, AIConfig"""from typing import Optional

from src.services.ai.helpers import FileProcessor

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasksfrom sqlalchemy import select

router = APIRouter(prefix="/ia", tags=["IA Feedback"])

from pydantic import BaseModel, Fieldfrom uuid import uuid4



# ============================================================================from typing import Optionalfrom datetime import datetime

# SCHEMAS

# ============================================================================from sqlalchemy.ext.asyncio import AsyncSessionimport logging



class RetroalimentacionRequest(BaseModel):from sqlalchemy import select, update

    """Request para generar retroalimentación de una entrega."""

    entrega_id: str = Field(..., description="ID de la entrega del estudiante")from uuid import uuid4from src.db.database import get_db

    modelo: str = Field(

        "gemini-2.5-flash",from datetime import datetimefrom src.core.security import get_current_user

        description="Modelo IA a usar"

    )import loggingfrom src.models.usuario import Usuario

    nivel_detalle: str = Field(

        "completo",from src.models.tarea import Tarea, Entrega

        description="Nivel: 'basico', 'medio' o 'completo'"

    )from src.db.database import get_dbfrom src.models.retroalimentacion_ia import RetroalimentacionIA

    incluir_calificacion: bool = Field(True, description="Incluir calificación sugerida")

from src.core.security import get_current_userfrom src.services.ai import GeminiService, AIConfig



class RetroalimentacionResponse(BaseModel):from src.models.usuario import Usuariofrom src.services.ai.helpers import FileProcessor

    """Response con retroalimentación generada."""

    entrega_id: strfrom src.models.tarea import Tarea, EntregaTarea

    tarea_id: str

    retroalimentacion: Optional[RetroalimentacionIASchema] = Nonefrom src.models.retroalimentacion_ia import (logger = logging.getLogger(__name__)

    fecha_generacion: Optional[datetime] = None

    RetroalimentacionIASchema,

    class Config:

        from_attributes = True    crear_retroalimentacion_dict,router = APIRouter(prefix="/ia", tags=["IA Feedback"])



    parsear_retroalimentacion

class BulkRetroalimentacionRequest(BaseModel):

    """Request para generación masiva.""")

    entrega_ids: list[str] = Field(..., description="IDs de entregas a procesar")

    modelo: str = Field("gemini-2.5-flash", description="Modelo IA")from src.services.ai import GeminiService, AIConfig# ============================================================================

    nivel_detalle: str = Field("completo", description="Nivel de detalle")

    incluir_calificacion: bool = Field(True, description="Incluir calificación")from src.services.ai.helpers import FileProcessor# SCHEMAS - Requests/Responses



# ============================================================================

class BulkRetroalimentacionResponse(BaseModel):

    """Response para operación bulk."""logger = logging.getLogger(__name__)

    job_id: str

    total_entregas: intclass RetroalimentacionRequest(BaseModel):

    estado: str = "procesando"

router = APIRouter(prefix="/ia", tags=["IA Feedback"])    """Request para generar retroalimentación de una tarea."""



class ModeloIAInfo(BaseModel):    entrega_id: int = Field(..., description="ID de la entrega del estudiante")

    """Información sobre modelo IA."""

    nombre: str    modelo: str = Field(

    descripcion: str

    costo_entrada: float# ============================================================================        "gemini-2.5-flash",

    costo_salida: float

    velocidad: str# SCHEMAS - Requests/Responses        description="Modelo IA a usar (gemini-2.5-flash, gemini-2.5-pro, gemini-2.0-flash)"

    capaz_multimedia: bool

# ============================================================================    )



# ============================================================================    nivel_detalle: str = Field(

# ENDPOINTS

# ============================================================================class RetroalimentacionRequest(BaseModel):        "completo",



@router.post(    """Request para generar retroalimentación de una tarea."""        description="Nivel: 'basico', 'medio' o 'completo'"

    "/retroalimentacion-tareas",

    response_model=RetroalimentacionResponse,    entrega_id: str = Field(..., description="ID de la entrega del estudiante")    )

    summary="Generar retroalimentación con IA"

)    modelo: str = Field(    incluir_calificacion: bool = Field(

async def generar_retroalimentacion_tarea(

    request: RetroalimentacionRequest,        "gemini-2.5-flash",        True,

    db: AsyncSession = Depends(get_db),

    current_user: Usuario = Depends(get_current_user)        description="Modelo IA a usar (gemini-2.5-flash, gemini-2.5-pro, gemini-2.0-flash)"        description="Si incluir sugerencia de calificación"

):

    """    )    )

    🚀 Genera retroalimentación con Google Gemini

        nivel_detalle: str = Field(

    Flujo:

    1. Obtiene entrega del estudiante        "completo",

    2. Verifica permisos (profesor del curso)

    3. Llama a GeminiService        description="Nivel: 'basico', 'medio' o 'completo'"class RetroalimentacionResponse(BaseModel):

    4. Almacena resultado en entregas_tareas.retroalimentacion_ia

    5. Retorna retroalimentación al profesor    )    """Response con retroalimentación generada."""

    """

    try:    incluir_calificacion: bool = Field(    retroalimentacion_id: int

        # 1. Obtener entrega

        result = await db.execute(        True,    entrega_id: int

            select(EntregaTarea).where(EntregaTarea.entrega_id == request.entrega_id)

        )        description="Si incluir sugerencia de calificación"    tarea_id: int

        entrega = result.scalars().first()

            )    fortalezas: list[str]

        if not entrega:

            raise HTTPException(status_code=404, detail="Entrega no encontrada")    areas_mejora: list[str]

        

        # 2. Obtener tarea y verificar permisos    retroalimentacion_texto: str

        result_tarea = await db.execute(

            select(Tarea).where(Tarea.tarea_id == entrega.tarea_id)class RetroalimentacionResponse(BaseModel):    calificacion_sugerida: Optional[float] = None

        )

        tarea = result_tarea.scalars().first()    """Response con retroalimentación generada."""    modelo_usado: str

        

        if not tarea:    entrega_id: str    tokens_usados: int

            raise HTTPException(status_code=404, detail="Tarea no encontrada")

            tarea_id: str    tiempo_procesamiento: float

        # Verificar permisos

        if str(tarea.docente_id) != str(current_user.usuario_id):    retroalimentacion: Optional[RetroalimentacionIASchema] = None    creado_en: datetime

            raise HTTPException(

                status_code=403,    fecha_generacion: Optional[datetime] = None

                detail="No tienes permisos para generar retroalimentación"

            )    class Config:

        

        # 3. Procesar archivos    class Config:        from_attributes = True

        archivos_contenido = {}

        if entrega.archivos_adicionales:        from_attributes = True

            try:

                archivos_list = entrega.archivos_adicionales if isinstance(entrega.archivos_adicionales, list) else [entrega.archivos_adicionales]

                for archivo in archivos_list:

                    try:class BulkRetroalimentacionRequest(BaseModel):

                        archivo_path = archivo.get("path") if isinstance(archivo, dict) else str(archivo)

                        if archivo_path:class BulkRetroalimentacionRequest(BaseModel):    """Request para generar retroalimentación masiva."""

                            contenido = await FileProcessor.procesar_archivo(archivo_path)

                            archivos_contenido[archivo_path] = contenido    """Request para generar retroalimentación masiva."""    entrega_ids: list[int] = Field(..., description="IDs de entregas a procesar")

                    except Exception as e:

                        logger.warning(f"No se pudo procesar archivo: {e}")    entrega_ids: list[str] = Field(..., description="IDs de entregas a procesar")    modelo: str = Field("gemini-2.5-flash", description="Modelo IA")

            except Exception as e:

                logger.warning(f"Error procesando archivos: {e}")    modelo: str = Field("gemini-2.5-flash", description="Modelo IA")    nivel_detalle: str = Field("completo", description="Nivel de detalle")

        

        # 4. Generar retroalimentación    nivel_detalle: str = Field("completo", description="Nivel de detalle")    incluir_calificacion: bool = Field(True, description="Incluir calificación sugerida")

        config = AIConfig(

            modelo=request.modelo,    incluir_calificacion: bool = Field(True, description="Incluir calificación sugerida")    notificar_estudiantes: bool = Field(

            temperatura=0.7,

            max_tokens=2000    notificar_estudiantes: bool = Field(        True,

        )

        gemini_service = GeminiService(config)        True,        description="Enviar notificación a estudiantes cuando esté lista"

        

        inicio = datetime.now()        description="Enviar notificación a estudiantes cuando esté lista"    )

        resultado = await gemini_service.generar_retroalimentacion(

            entrega=entrega,    )

            tarea=tarea,

            archivos_contenido=archivos_contenido,

            incluir_calificacion=request.incluir_calificacion,

            nivel_detalle=request.nivel_detalleclass BulkRetroalimentacionResponse(BaseModel):

        )

        tiempo_procesamiento = (datetime.now() - inicio).total_seconds()class BulkRetroalimentacionResponse(BaseModel):    """Response para operación bulk."""

        

        # 5. Preparar datos    """Response para operación bulk."""    job_id: str

        retroalimentacion_data = crear_retroalimentacion_dict(

            retroalimentacion_texto=resultado.get("retroalimentacion_texto", ""),    job_id: str    total_entregas: int

            fortalezas=resultado.get("fortalezas", []),

            areas_mejora=resultado.get("areas_mejora", []),    total_entregas: int    estado: str = "procesando"

            recursos_recomendados=resultado.get("recursos_recomendados", []),

            calificacion_sugerida=resultado.get("calificacion_sugerida"),    estado: str = "procesando"    progreso: int = 0

            modelo_usado=request.modelo,

            nivel_profundidad=request.nivel_detalle,    progreso: int = 0

            tokens_usados=resultado.get("tokens_usados", 0)

        )

        

        # 6. Guardar en BDclass ModeloIAInfo(BaseModel):

        stmt = update(EntregaTarea).where(

            EntregaTarea.entrega_id == request.entrega_idclass ModeloIAInfo(BaseModel):    """Información sobre modelo IA disponible."""

        ).values(

            retroalimentacion_ia=retroalimentacion_data,    """Información sobre modelo IA disponible."""    nombre: str

            calificacion_preliminar_ia=resultado.get("calificacion_sugerida")

        )    nombre: str    descripcion: str

        await db.execute(stmt)

        await db.commit()    descripcion: str    costo_entrada: float

        

        # 7. Obtener actualizado    costo_entrada: float    costo_salida: float

        result_updated = await db.execute(

            select(EntregaTarea).where(EntregaTarea.entrega_id == request.entrega_id)    costo_salida: float    velocidad: str  # "rapido", "normal", "lento"

        )

        entrega_updated = result_updated.scalars().first()    velocidad: str  # "rapido", "normal", "lento"    capaz_multimedia: bool

        

        # 8. Retornar    capaz_multimedia: bool

        retroalimentacion_parsed = parsear_retroalimentacion(entrega_updated.retroalimentacion_ia)

        

        return RetroalimentacionResponse(

            entrega_id=entrega_updated.entrega_id,# ============================================================================

            tarea_id=entrega_updated.tarea_id,

            retroalimentacion=retroalimentacion_parsed,# ============================================================================# ENDPOINTS - RETROALIMENTACIÓN INDIVIDUAL (REAL)

            fecha_generacion=datetime.now()

        )# ENDPOINTS - RETROALIMENTACIÓN INDIVIDUAL (REAL)# ============================================================================

    

    except HTTPException:# ============================================================================

        raise

    except Exception as e:@router.post(

        logger.error(f"Error: {e}", exc_info=True)

        raise HTTPException(status_code=500, detail=str(e))@router.post(    "/retroalimentacion-tareas",



    "/retroalimentacion-tareas",    response_model=RetroalimentacionResponse,

@router.post(

    "/retroalimentacion-masiva",    response_model=RetroalimentacionResponse,    summary="Generar retroalimentación con IA para una tarea",

    response_model=BulkRetroalimentacionResponse,

    summary="Generar retroalimentación para múltiples entregas"    summary="Generar retroalimentación con IA para una tarea",    description="Analiza la entrega de un estudiante con Google Gemini y genera retroalimentación estructurada."

)

async def generar_retroalimentacion_masiva(    description="Analiza la entrega de un estudiante con Google Gemini y genera retroalimentación estructurada.")

    request: BulkRetroalimentacionRequest,

    background_tasks: BackgroundTasks,)async def generar_retroalimentacion_tarea(

    db: AsyncSession = Depends(get_db),

    current_user: Usuario = Depends(get_current_user)async def generar_retroalimentacion_tarea(    request: RetroalimentacionRequest,

):

    """    request: RetroalimentacionRequest,    db: AsyncSession = Depends(get_db),

    🚀 Procesa retroalimentación de múltiples entregas en background

    """    db: AsyncSession = Depends(get_db),    current_user: Usuario = Depends(get_current_user)

    job_id = str(uuid4())

        current_user: Usuario = Depends(get_current_user)):

    # Validar entregas

    entregas = []):    """

    for entrega_id in request.entrega_ids:

        result = await db.execute(    """    🚀 ENDPOINT REAL - Usa GeminiService para generar retroalimentación

            select(EntregaTarea).where(EntregaTarea.entrega_id == entrega_id)

        )    🚀 ENDPOINT REAL - Usa GeminiService para generar retroalimentación    

        entrega = result.scalars().first()

                Flujo:

        if not entrega:

            continue    Flujo:    1. Obtiene entrega del estudiante

        

        result_tarea = await db.execute(    1. Obtiene entrega del estudiante    2. Verifica permisos (profesor del curso)

            select(Tarea).where(Tarea.tarea_id == entrega.tarea_id)

        )    2. Verifica permisos (profesor del curso)    3. Descarga archivos adjuntos

        tarea = result_tarea.scalars().first()

            3. Descarga archivos adjuntos    4. Llama a GeminiService.generar_retroalimentacion()

        if tarea and str(tarea.docente_id) == str(current_user.usuario_id):

            entregas.append((entrega, tarea))    4. Llama a GeminiService.generar_retroalimentacion()    5. Almacena resultado en BD

    

    if not entregas:    5. Almacena resultado en BD (entregas_tareas.retroalimentacion_ia)    6. Retorna retroalimentación al profesor

        raise HTTPException(

            status_code=400,    6. Retorna retroalimentación al profesor    """

            detail="No se encontraron entregas válidas"

        )    """    try:

    

    # Agregar tarea en background    try:        # ✅ 1. Obtener entrega

    background_tasks.add_task(

        procesar_retroalimentacion_masiva,        # ✅ 1. Obtener entrega        result = await db.execute(

        job_id=job_id,

        entregas=entregas,        result = await db.execute(            select(Entrega).where(Entrega.id == request.entrega_id)

        request=request

    )            select(EntregaTarea).where(EntregaTarea.entrega_id == request.entrega_id)        )

    

    return BulkRetroalimentacionResponse(        )        entrega = result.scalars().first()

        job_id=job_id,

        total_entregas=len(entregas),        entrega = result.scalars().first()        

        estado="procesando"

    )                if not entrega:



        if not entrega:            raise HTTPException(status_code=404, detail="Entrega no encontrada")

async def procesar_retroalimentacion_masiva(

    job_id: str,            raise HTTPException(status_code=404, detail="Entrega no encontrada")        

    entregas: list[tuple],

    request: BulkRetroalimentacionRequest                # ✅ 2. Obtener tarea y verificar permisos

):

    """Procesa entregas secuencialmente en background."""        # ✅ 2. Obtener tarea y verificar permisos        tarea = await db.get(Tarea, entrega.tarea_id)

    config = AIConfig(

        modelo=request.modelo,        result_tarea = await db.execute(        if not tarea:

        temperatura=0.7,

        max_tokens=2000            select(Tarea).where(Tarea.tarea_id == entrega.tarea_id)            raise HTTPException(status_code=404, detail="Tarea no encontrada")

    )

    gemini_service = GeminiService(config)        )        

    

    for idx, (entrega, tarea) in enumerate(entregas):        tarea = result_tarea.scalars().first()        # Verificar que current_user es profesor del curso

        try:

            # Procesar archivos                if tarea.docente_id != current_user.id:

            archivos_contenido = {}

            if entrega.archivos_adicionales:        if not tarea:            raise HTTPException(

                try:

                    archivos_list = entrega.archivos_adicionales if isinstance(entrega.archivos_adicionales, list) else [entrega.archivos_adicionales]            raise HTTPException(status_code=404, detail="Tarea no encontrada")                status_code=403,

                    for archivo in archivos_list:

                        try:                        detail="No tienes permisos para generar retroalimentación en esta tarea"

                            archivo_path = archivo.get("path") if isinstance(archivo, dict) else str(archivo)

                            if archivo_path:        # Verificar que current_user es profesor del curso            )

                                contenido = await FileProcessor.procesar_archivo(archivo_path)

                                archivos_contenido[archivo_path] = contenido        if str(tarea.docente_id) != str(current_user.usuario_id):        

                        except Exception as e:

                            logger.warning(f"Error procesando: {e}")            raise HTTPException(        # ✅ 3. Procesar archivos adjuntos

                except Exception as e:

                    logger.warning(f"Error: {e}")                status_code=403,        archivos_contenido = {}

            

            # Generar                detail="No tienes permisos para generar retroalimentación en esta tarea"        if entrega.archivos_adjuntos:

            resultado = await gemini_service.generar_retroalimentacion(

                entrega=entrega,            )            for archivo_path in entrega.archivos_adjuntos:

                tarea=tarea,

                archivos_contenido=archivos_contenido,                        try:

                incluir_calificacion=request.incluir_calificacion,

                nivel_detalle=request.nivel_detalle        # ✅ 3. Procesar archivos adjuntos                    contenido = await FileProcessor.procesar_archivo(archivo_path)

            )

                    archivos_contenido = {}                    archivos_contenido[archivo_path] = contenido

            # Preparar datos

            retroalimentacion_data = crear_retroalimentacion_dict(        if entrega.archivos_adicionales:                except Exception as e:

                retroalimentacion_texto=resultado.get("retroalimentacion_texto", ""),

                fortalezas=resultado.get("fortalezas", []),            try:                    logger.warning(f"No se pudo procesar archivo {archivo_path}: {e}")

                areas_mejora=resultado.get("areas_mejora", []),

                recursos_recomendados=resultado.get("recursos_recomendados", []),                archivos_list = entrega.archivos_adicionales if isinstance(entrega.archivos_adicionales, list) else [entrega.archivos_adicionales]        

                calificacion_sugerida=resultado.get("calificacion_sugerida"),

                modelo_usado=request.modelo,                for archivo in archivos_list:        # ✅ 4. Inicializar GeminiService y generar retroalimentación

                nivel_profundidad=request.nivel_detalle,

                tokens_usados=resultado.get("tokens_usados", 0),                    try:        config = AIConfig(

                job_id=job_id

            )                        if isinstance(archivo, dict):            modelo=request.modelo,

            

            logger.info(f"✅ Retroalimentación lista: {entrega.entrega_id} ({idx+1}/{len(entregas)})")                            archivo_path = archivo.get("path") or archivo.get("url")            temperatura=0.7,

        

        except Exception as e:                        else:            max_tokens=2000

            logger.error(f"❌ Error procesando {entrega.entrega_id}: {e}")

            continue                            archivo_path = str(archivo)        )



                                gemini_service = GeminiService(config)

@router.get(

    "/retroalimentacion/{entrega_id}",                        if archivo_path:        

    response_model=RetroalimentacionResponse,

    summary="Obtener retroalimentación de una entrega"                            contenido = await FileProcessor.procesar_archivo(archivo_path)        inicio = datetime.now()

)

async def obtener_retroalimentacion(                            archivos_contenido[archivo_path] = contenido        resultado = await gemini_service.generar_retroalimentacion(

    entrega_id: str,

    db: AsyncSession = Depends(get_db),                    except Exception as e:            entrega=entrega,

    current_user: Usuario = Depends(get_current_user)

):                        logger.warning(f"No se pudo procesar archivo: {e}")            tarea=tarea,

    """Obtiene la retroalimentación IA de una entrega."""

                except Exception as e:            archivos_contenido=archivos_contenido,

    result = await db.execute(

        select(EntregaTarea).where(EntregaTarea.entrega_id == entrega_id)                logger.warning(f"Error procesando archivos: {e}")            incluir_calificacion=request.incluir_calificacion,

    )

    entrega = result.scalars().first()                    nivel_detalle=request.nivel_detalle

    

    if not entrega:        # ✅ 4. Inicializar GeminiService y generar retroalimentación        )

        raise HTTPException(status_code=404, detail="Entrega no encontrada")

            config = AIConfig(        tiempo_procesamiento = (datetime.now() - inicio).total_seconds()

    # Verificar permisos

    result_tarea = await db.execute(            modelo=request.modelo,        

        select(Tarea).where(Tarea.tarea_id == entrega.tarea_id)

    )            temperatura=0.7,        # ✅ 5. Guardar resultado en BD

    tarea = result_tarea.scalars().first()

                max_tokens=2000        retroalimentacion = RetroalimentacionIA(

    if (str(current_user.usuario_id) != str(tarea.docente_id) and 

        str(current_user.usuario_id) != str(entrega.estudiante_id)):        )            entrega_id=entrega.id,

        raise HTTPException(status_code=403, detail="Sin permisos")

            gemini_service = GeminiService(config)            tarea_id=tarea.id,

    retroalimentacion_parsed = parsear_retroalimentacion(entrega.retroalimentacion_ia)

                        profesor_id=current_user.id,

    return RetroalimentacionResponse(

        entrega_id=entrega.entrega_id,        inicio = datetime.now()            retroalimentacion=resultado.get("retroalimentacion_texto", ""),

        tarea_id=entrega.tarea_id,

        retroalimentacion=retroalimentacion_parsed,        resultado = await gemini_service.generar_retroalimentacion(            fortalezas=resultado.get("fortalezas", []),

        fecha_generacion=datetime.now() if retroalimentacion_parsed else None

    )            entrega=entrega,            areas_mejora=resultado.get("areas_mejora", []),



            tarea=tarea,            recursos_recomendados=resultado.get("recursos_recomendados", []),

@router.get(

    "/modelos",            archivos_contenido=archivos_contenido,            calificacion_sugerida=resultado.get("calificacion_sugerida"),

    response_model=list[ModeloIAInfo],

    summary="Listar modelos IA disponibles"            incluir_calificacion=request.incluir_calificacion,            modelo_usado=request.modelo,

)

async def listar_modelos(            nivel_detalle=request.nivel_detalle            tokens_usados=resultado.get("tokens_usados", 0),

    current_user: Usuario = Depends(get_current_user)

):        )            metadata={

    """Retorna información sobre modelos IA disponibles."""

    return [        tiempo_procesamiento = (datetime.now() - inicio).total_seconds()                "nivel_detalle": request.nivel_detalle,

        ModeloIAInfo(

            nombre="gemini-2.5-flash",                        "tiempo_procesamiento": tiempo_procesamiento,

            descripcion="Modelo rápido y eficiente - Recomendado",

            costo_entrada=0.075,        # ✅ 5. Preparar datos para guardar en BD                "version_api": "1.0"

            costo_salida=0.3,

            velocidad="rapido",        retroalimentacion_data = crear_retroalimentacion_dict(            }

            capaz_multimedia=True

        ),            retroalimentacion_texto=resultado.get("retroalimentacion_texto", ""),        )

        ModeloIAInfo(

            nombre="gemini-2.5-pro",            fortalezas=resultado.get("fortalezas", []),        

            descripcion="Modelo premium - Mayor precisión",

            costo_entrada=1.5,            areas_mejora=resultado.get("areas_mejora", []),        db.add(retroalimentacion)

            costo_salida=6.0,

            velocidad="normal",            recursos_recomendados=resultado.get("recursos_recomendados", []),        await db.commit()

            capaz_multimedia=True

        ),            calificacion_sugerida=resultado.get("calificacion_sugerida"),        await db.refresh(retroalimentacion)

        ModeloIAInfo(

            nombre="gemini-2.0-flash",            modelo_usado=request.modelo,        

            descripcion="Modelo rápido anterior",

            costo_entrada=0.075,            nivel_profundidad=request.nivel_detalle,        # ✅ 6. Retornar respuesta

            costo_salida=0.3,

            velocidad="rapido",            tokens_usados=resultado.get("tokens_usados", 0),        return RetroalimentacionResponse(

            capaz_multimedia=True

        )            confianza=0.95            retroalimentacion_id=retroalimentacion.id,

    ]

        )            entrega_id=entrega.id,

                    tarea_id=tarea.id,

        # ✅ 6. Guardar en BD (UPDATE entregas_tareas.retroalimentacion_ia)            fortalezas=resultado.get("fortalezas", []),

        stmt = update(EntregaTarea).where(            areas_mejora=resultado.get("areas_mejora", []),

            EntregaTarea.entrega_id == request.entrega_id            retroalimentacion_texto=resultado.get("retroalimentacion_texto", ""),

        ).values(            calificacion_sugerida=resultado.get("calificacion_sugerida"),

            retroalimentacion_ia=retroalimentacion_data            modelo_usado=request.modelo,

        )            tokens_usados=resultado.get("tokens_usados", 0),

        await db.execute(stmt)            tiempo_procesamiento=tiempo_procesamiento,

        await db.commit()            creado_en=retroalimentacion.creado_en

                )

        # ✅ 7. Obtener entrega actualizada    

        result_updated = await db.execute(    except HTTPException:

            select(EntregaTarea).where(EntregaTarea.entrega_id == request.entrega_id)        raise

        )    except Exception as e:

        entrega_updated = result_updated.scalars().first()        logger.error(f"Error generando retroalimentación: {e}", exc_info=True)

                raise HTTPException(status_code=500, detail=f"Error procesando retroalimentación: {str(e)}")

        # ✅ 8. Retornar respuesta

        retroalimentacion_parsed = parsear_retroalimentacion(entrega_updated.retroalimentacion_ia)

        # ============================================================================

        return RetroalimentacionResponse(# ENDPOINTS - RETROALIMENTACIÓN MASIVA (BACKGROUND)

            entrega_id=entrega_updated.entrega_id,# ============================================================================

            tarea_id=entrega_updated.tarea_id,

            retroalimentacion=retroalimentacion_parsed,@router.post(

            fecha_generacion=datetime.now()    "/retroalimentacion-masiva",

        )    response_model=BulkRetroalimentacionResponse,

        summary="Generar retroalimentación para múltiples tareas",

    except HTTPException:    description="Procesa retroalimentación de múltiples entregas en background"

        raise)

    except Exception as e:async def generar_retroalimentacion_masiva(

        logger.error(f"Error generando retroalimentación: {e}", exc_info=True)    request: BulkRetroalimentacionRequest,

        raise HTTPException(status_code=500, detail=f"Error procesando retroalimentación: {str(e)}")    background_tasks: BackgroundTasks,

    db: AsyncSession = Depends(get_db),

    current_user: Usuario = Depends(get_current_user)

# ============================================================================):

# ENDPOINTS - RETROALIMENTACIÓN MASIVA (BACKGROUND)    """

# ============================================================================    🚀 ENDPOINT REAL - Procesa múltiples entregas en background

    

@router.post(    - Retorna job_id inmediatamente

    "/retroalimentacion-masiva",    - Procesa entregas en background

    response_model=BulkRetroalimentacionResponse,    - Envía notificación cuando finaliza

    summary="Generar retroalimentación para múltiples tareas",    """

    description="Procesa retroalimentación de múltiples entregas en background"    # Crear job ID

)    job_id = str(uuid4())

async def generar_retroalimentacion_masiva(    

    request: BulkRetroalimentacionRequest,    # Verificar permisos y validar entregas

    background_tasks: BackgroundTasks,    entregas = []

    db: AsyncSession = Depends(get_db),    for entrega_id in request.entrega_ids:

    current_user: Usuario = Depends(get_current_user)        result = await db.execute(

):            select(Entrega).where(Entrega.id == entrega_id)

    """        )

    🚀 ENDPOINT REAL - Procesa múltiples entregas en background        entrega = result.scalars().first()

            

    - Retorna job_id inmediatamente        if not entrega:

    - Procesa entregas en background            continue

    - Envía notificación cuando finaliza        

    """        tarea = await db.get(Tarea, entrega.tarea_id)

    # Crear job ID        if tarea and tarea.docente_id == current_user.id:

    job_id = str(uuid4())            entregas.append((entrega, tarea))

        

    # Verificar permisos y validar entregas    if not entregas:

    entregas = []        raise HTTPException(

    for entrega_id in request.entrega_ids:            status_code=400,

        result = await db.execute(            detail="No se encontraron entregas válidas para procesar"

            select(EntregaTarea).where(EntregaTarea.entrega_id == entrega_id)        )

        )    

        entrega = result.scalars().first()    # Agregar tarea en background

            background_tasks.add_task(

        if not entrega:        procesar_retroalimentacion_masiva,

            continue        job_id=job_id,

                entregas=entregas,

        result_tarea = await db.execute(        request=request,

            select(Tarea).where(Tarea.tarea_id == entrega.tarea_id)        profesor_id=current_user.id

        )    )

        tarea = result_tarea.scalars().first()    

            return BulkRetroalimentacionResponse(

        if tarea and str(tarea.docente_id) == str(current_user.usuario_id):        job_id=job_id,

            entregas.append((entrega, tarea))        total_entregas=len(entregas),

            estado="procesando",

    if not entregas:        progreso=0

        raise HTTPException(    )

            status_code=400,

            detail="No se encontraron entregas válidas para procesar"

        )async def procesar_retroalimentacion_masiva(

        job_id: str,

    # Agregar tarea en background    entregas: list[tuple],

    background_tasks.add_task(    request: BulkRetroalimentacionRequest,

        procesar_retroalimentacion_masiva,    profesor_id: int

        job_id=job_id,):

        entregas=entregas,    """

        request=request    🔄 Función background - Procesa entregas secuencialmente

    )    

        Para cada entrega:

    return BulkRetroalimentacionResponse(    - Genera retroalimentación con Gemini

        job_id=job_id,    - Almacena en BD

        total_entregas=len(entregas),    - Actualiza progreso

        estado="procesando",    - Envía notificación al estudiante

        progreso=0    """

    )    from src.db.database import SessionLocal

    

    db = SessionLocal()

async def procesar_retroalimentacion_masiva(    

    job_id: str,    config = AIConfig(

    entregas: list[tuple],        modelo=request.modelo,

    request: BulkRetroalimentacionRequest        temperatura=0.7,

):        max_tokens=2000

    """    )

    🔄 Función background - Procesa entregas secuencialmente    gemini_service = GeminiService(config)

        

    Para cada entrega:    for idx, (entrega, tarea) in enumerate(entregas):

    - Genera retroalimentación con Gemini        try:

    - Almacena en BD (entregas_tareas.retroalimentacion_ia)            # Procesar archivos

    - Actualiza progreso            archivos_contenido = {}

    - Envía notificación al estudiante            if entrega.archivos_adjuntos:

    """                for archivo_path in entrega.archivos_adjuntos:

    from src.db.database import AsyncSession, create_async_engine                    try:

    from src.db.database import get_db                        contenido = await FileProcessor.procesar_archivo(archivo_path)

                            archivos_contenido[archivo_path] = contenido

    config = AIConfig(                    except Exception as e:

        modelo=request.modelo,                        logger.warning(f"No se pudo procesar archivo {archivo_path}: {e}")

        temperatura=0.7,            

        max_tokens=2000            # Generar retroalimentación

    )            resultado = await gemini_service.generar_retroalimentacion(

    gemini_service = GeminiService(config)                entrega=entrega,

                    tarea=tarea,

    for idx, (entrega, tarea) in enumerate(entregas):                archivos_contenido=archivos_contenido,

        try:                incluir_calificacion=request.incluir_calificacion,

            # Procesar archivos                nivel_detalle=request.nivel_detalle

            archivos_contenido = {}            )

            if entrega.archivos_adicionales:            

                try:            # Guardar en BD

                    archivos_list = entrega.archivos_adicionales if isinstance(entrega.archivos_adicionales, list) else [entrega.archivos_adicionales]            retroalimentacion = RetroalimentacionIA(

                    for archivo in archivos_list:                entrega_id=entrega.id,

                        try:                tarea_id=tarea.id,

                            if isinstance(archivo, dict):                profesor_id=profesor_id,

                                archivo_path = archivo.get("path") or archivo.get("url")                retroalimentacion=resultado.get("retroalimentacion_texto", ""),

                            else:                fortalezas=resultado.get("fortalezas", []),

                                archivo_path = str(archivo)                areas_mejora=resultado.get("areas_mejora", []),

                                            recursos_recomendados=resultado.get("recursos_recomendados", []),

                            if archivo_path:                calificacion_sugerida=resultado.get("calificacion_sugerida"),

                                contenido = await FileProcessor.procesar_archivo(archivo_path)                modelo_usado=request.modelo,

                                archivos_contenido[archivo_path] = contenido                tokens_usados=resultado.get("tokens_usados", 0),

                        except Exception as e:                metadata={

                            logger.warning(f"No se pudo procesar archivo: {e}")                    "nivel_detalle": request.nivel_detalle,

                except Exception as e:                    "job_id": job_id,

                    logger.warning(f"Error procesando archivos: {e}")                    "progreso": f"{idx+1}/{len(entregas)}"

                            }

            # Generar retroalimentación            )

            resultado = await gemini_service.generar_retroalimentacion(            

                entrega=entrega,            db.add(retroalimentacion)

                tarea=tarea,            await db.commit()

                archivos_contenido=archivos_contenido,            

                incluir_calificacion=request.incluir_calificacion,            logger.info(f"Retroalimentación generada para entrega {entrega.id} ({idx+1}/{len(entregas)})")

                nivel_detalle=request.nivel_detalle        

            )        except Exception as e:

                        logger.error(f"Error procesando entrega {entrega.id}: {e}", exc_info=True)

            # Preparar datos            continue

            retroalimentacion_data = crear_retroalimentacion_dict(        

                retroalimentacion_texto=resultado.get("retroalimentacion_texto", ""),        finally:

                fortalezas=resultado.get("fortalezas", []),            await db.close()

                areas_mejora=resultado.get("areas_mejora", []),

                recursos_recomendados=resultado.get("recursos_recomendados", []),

                calificacion_sugerida=resultado.get("calificacion_sugerida"),# ============================================================================

                modelo_usado=request.modelo,# ENDPOINTS - OBTENER RETROALIMENTACIÓN

                nivel_profundidad=request.nivel_detalle,# ============================================================================

                tokens_usados=resultado.get("tokens_usados", 0),

                job_id=job_id@router.get(

            )    "/retroalimentacion/{retroalimentacion_id}",

                response_model=RetroalimentacionResponse,

            # TODO: Guardar en BD con db session async    summary="Obtener retroalimentación"

            logger.info(f"Retroalimentación generada para entrega {entrega.entrega_id} ({idx+1}/{len(entregas)})"))

        async def obtener_retroalimentacion(

        except Exception as e:    retroalimentacion_id: int,

            logger.error(f"Error procesando entrega {entrega.entrega_id}: {e}", exc_info=True)    db: AsyncSession = Depends(get_db),

            continue    current_user: Usuario = Depends(get_current_user)

):

    """Obtiene una retroalimentación existente."""

# ============================================================================    

# ENDPOINTS - OBTENER RETROALIMENTACIÓN    retroalimentacion = await db.get(RetroalimentacionIA, retroalimentacion_id)

# ============================================================================    

    if not retroalimentacion:

@router.get(        raise HTTPException(status_code=404, detail="Retroalimentación no encontrada")

    "/retroalimentacion/{entrega_id}",    

    response_model=RetroalimentacionResponse,    # Verificar permisos (profesor o estudiante de la entrega)

    summary="Obtener retroalimentación de una entrega"    entrega = await db.get(Entrega, retroalimentacion.entrega_id)

)    

async def obtener_retroalimentacion(    if (current_user.id != retroalimentacion.profesor_id and 

    entrega_id: str,        current_user.id != entrega.estudiante_id):

    db: AsyncSession = Depends(get_db),        raise HTTPException(status_code=403, detail="No tienes permiso para ver esto")

    current_user: Usuario = Depends(get_current_user)    

):    return RetroalimentacionResponse(

    """Obtiene la retroalimentación IA de una entrega."""        retroalimentacion_id=retroalimentacion.id,

            entrega_id=retroalimentacion.entrega_id,

    result = await db.execute(        tarea_id=retroalimentacion.tarea_id,

        select(EntregaTarea).where(EntregaTarea.entrega_id == entrega_id)        fortalezas=retroalimentacion.fortalezas,

    )        areas_mejora=retroalimentacion.areas_mejora,

    entrega = result.scalars().first()        retroalimentacion_texto=retroalimentacion.retroalimentacion,

            calificacion_sugerida=retroalimentacion.calificacion_sugerida,

    if not entrega:        modelo_usado=retroalimentacion.modelo_usado,

        raise HTTPException(status_code=404, detail="Entrega no encontrada")        tokens_usados=retroalimentacion.tokens_usados,

            tiempo_procesamiento=0,

    # Verificar permisos (profesor o estudiante de la entrega)        creado_en=retroalimentacion.creado_en

    result_tarea = await db.execute(    )

        select(Tarea).where(Tarea.tarea_id == entrega.tarea_id)

    )

    tarea = result_tarea.scalars().first()@router.get(

        "/retroalimentacion-entrega/{entrega_id}",

    if (str(current_user.usuario_id) != str(tarea.docente_id) and     response_model=list[RetroalimentacionResponse],

        str(current_user.usuario_id) != str(entrega.estudiante_id)):    summary="Obtener todas las retroalimentaciones de una entrega"

        raise HTTPException(status_code=403, detail="No tienes permiso para ver esto"))

    async def obtener_retroalimentaciones_entrega(

    retroalimentacion_parsed = parsear_retroalimentacion(entrega.retroalimentacion_ia)    entrega_id: int,

        db: AsyncSession = Depends(get_db),

    return RetroalimentacionResponse(    current_user: Usuario = Depends(get_current_user)

        entrega_id=entrega.entrega_id,):

        tarea_id=entrega.tarea_id,    """Obtiene todas las retroalimentaciones de una entrega."""

        retroalimentacion=retroalimentacion_parsed,    

        fecha_generacion=datetime.now() if retroalimentacion_parsed else None    entrega = await db.get(Entrega, entrega_id)

    )    if not entrega:

        raise HTTPException(status_code=404, detail="Entrega no encontrada")

    

# ============================================================================    # Verificar permisos

# ENDPOINTS - INFORMACIÓN DE MODELOS    if current_user.id != entrega.estudiante_id:

# ============================================================================        raise HTTPException(status_code=403, detail="No tienes permiso para ver esto")

    

@router.get(    result = await db.execute(

    "/modelos",        select(RetroalimentacionIA).where(RetroalimentacionIA.entrega_id == entrega_id)

    response_model=list[ModeloIAInfo],    )

    summary="Listar modelos IA disponibles"    retroalimentaciones = result.scalars().all()

)    

async def listar_modelos(    return [

    current_user: Usuario = Depends(get_current_user)        RetroalimentacionResponse(

):            retroalimentacion_id=r.id,

    """Retorna información sobre modelos IA disponibles."""            entrega_id=r.entrega_id,

    return [            tarea_id=r.tarea_id,

        ModeloIAInfo(            fortalezas=r.fortalezas,

            nombre="gemini-2.5-flash",            areas_mejora=r.areas_mejora,

            descripcion="Modelo rápido y eficiente - Recomendado para la mayoría de casos",            retroalimentacion_texto=r.retroalimentacion,

            costo_entrada=0.075,            calificacion_sugerida=r.calificacion_sugerida,

            costo_salida=0.3,            modelo_usado=r.modelo_usado,

            velocidad="rapido",            tokens_usados=r.tokens_usados,

            capaz_multimedia=True            tiempo_procesamiento=0,

        ),            creado_en=r.creado_en

        ModeloIAInfo(        )

            nombre="gemini-2.5-pro",        for r in retroalimentaciones

            descripcion="Modelo premium - Mayor precisión para análisis complejos",    ]

            costo_entrada=1.5,

            costo_salida=6.0,

            velocidad="normal",# ============================================================================

            capaz_multimedia=True# ENDPOINTS - INFORMACIÓN DE MODELOS

        ),# ============================================================================

        ModeloIAInfo(

            nombre="gemini-2.0-flash",@router.get(

            descripcion="Modelo rápido anterior - Compatible pero menos recomendado",    "/modelos",

            costo_entrada=0.075,    response_model=list[ModeloIAInfo],

            costo_salida=0.3,    summary="Listar modelos IA disponibles"

            velocidad="rapido",)

            capaz_multimedia=Trueasync def listar_modelos(

        )    current_user: Usuario = Depends(get_current_user)

    ]):

    """Retorna información sobre modelos IA disponibles."""
    return [
        ModeloIAInfo(
            nombre="gemini-2.5-flash",
            descripcion="Modelo rápido y eficiente - Recomendado para la mayoría de casos",
            costo_entrada=0.075,
            costo_salida=0.3,
            velocidad="rapido",
            capaz_multimedia=True
        ),
        ModeloIAInfo(
            nombre="gemini-2.5-pro",
            descripcion="Modelo premium - Mayor precisión para análisis complejos",
            costo_entrada=1.5,
            costo_salida=6.0,
            velocidad="normal",
            capaz_multimedia=True
        ),
        ModeloIAInfo(
            nombre="gemini-2.0-flash",
            descripcion="Modelo rápido anterior - Compatible pero menos recomendado",
            costo_entrada=0.075,
            costo_salida=0.3,
            velocidad="rapido",
            capaz_multimedia=True
        )
    ]
