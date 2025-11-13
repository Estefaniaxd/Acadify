# 📚 PLAN MAESTRO - SISTEMA ACADÉMICO ROBUSTO Y PROFESIONAL

> **Objetivo**: Diseñar un sistema académico que sirva para CUALQUIER tipo de institución educativa sin modificaciones.
> **Fecha**: 30 de Octubre 2025
> **Estado**: Documento de Diseño y Planificación

---

## 🎯 VISIÓN GLOBAL

### Tipos de Instituciones que debe soportar:
1. **Universidades**: Programas de pregrado, posgrado, facultades, departamentos
2. **Colegios**: Primaria, bachillerato, grados, salones
3. **Institutos Técnicos**: SENA-like, programas técnicos, tecnológicos
4. **Academias de Idiomas**: Niveles (A1-C2), intensivos, regulares
5. **Conservatorios**: Música, arte, danza, niveles de formación
6. **Centros de Formación Profesional**: Certificaciones, bootcamps, talleres
7. **Plataformas Online**: Cursos autodirigidos, sincrónico/asincrónico
8. **Escuelas de Oficios**: Programas cortos, prácticos, certificados

---

## 🏗️ ARQUITECTURA CONCEPTUAL PROPUESTA

### Jerarquía Universal Adaptable:

```
INSTITUCIÓN
    ↓
ESTRUCTURA ORGANIZACIONAL (flexible)
├── Facultad / Departamento / Área (Universidades)
├── Sede / Campus (Multi-sede)
└── División Académica (Opcional)
    ↓
PROGRAMA ACADÉMICO (adaptable)
├── Carrera Profesional (Universidad: 8-10 semestres)
├── Programa Técnico (SENA: 18-24 meses)
├── Grado Escolar (Colegio: K-12)
├── Nivel de Idioma (Academia: A1, A2, B1, B2, C1, C2)
├── Certificación (Bootcamp: 3-6 meses)
└── Diplomado (Extensión: 120-240 horas)
    ↓
PERÍODO ACADÉMICO (configurable por institución)
├── Semestre (16 semanas)
├── Trimestre (12 semanas)
├── Cuatrimestre (4 meses)
├── Bimestre (2 meses)
├── Módulo (4-6 semanas)
├── Ciclo Continuo (rolling admissions)
└── Anual (10 meses)
    ↓
CURSO / MATERIA / ASIGNATURA (contenido académico)
├── Curso Teórico
├── Curso Práctico / Laboratorio
├── Taller
├── Proyecto Integrador
├── Seminario
├── Electiva / Optativa
└── Obligatoria / Core
    ↓
SECCIÓN / GRUPO / PARALELO (instancia del curso)
├── Horario definido
├── Docente asignado
├── Aula/Espacio
└── Cupo de estudiantes
    ↓
SESIÓN / CLASE (encuentro específico)
├── Lunes 8:00-10:00 (recurrente)
├── Clase Virtual (link Zoom/Meet)
└── Clase Grabada (asíncrono)
    ↓
ESTUDIANTE INSCRITO
```

---

## 📋 ENTIDADES CLAVE Y CAMPOS NECESARIOS

### 1. **ESTRUCTURA_ORGANIZACIONAL** (Nueva - Flexible)
```python
# Permite modelar: Facultades, Departamentos, Áreas, Sedes, Divisiones
id: UUID
institucion_id: UUID
nombre: str  # "Facultad de Ingeniería", "Departamento de Matemáticas", "Sede Norte"
tipo: ENUM  # 'facultad', 'departamento', 'area', 'sede', 'division', 'campus'
codigo: str
padre_id: UUID  # Jerarquía: Facultad → Departamento
nivel_jerarquia: int
responsable_id: UUID  # Decano, Director, Coordinador
descripcion: text
activo: bool
metadata: JSONB  # Configuración específica
```

**Por qué es necesario:**
- Universidades grandes tienen facultades → departamentos → programas
- Colegios tienen sedes → niveles (primaria/bachillerato) → grados
- SENA tiene centros → áreas técnicas → programas
- **Solución**: Jerarquía flexible que cada institución configura

---

### 2. **PROGRAMA** (Mejorado - Súper Robusto)
```python
# Actual (básico): 5 campos
# Propuesto: 35+ campos

# IDENTIFICACIÓN
programa_id: UUID
institucion_id: UUID
estructura_organizacional_id: UUID  # Facultad/Departamento/Área
codigo: str UNIQUE  # "ING-SIST-001", "TEC-SOFT-2024"
nombre: str  # "Ingeniería de Sistemas"
nombre_corto: str  # "Ing. Sistemas"
titulo_otorgado: str  # "Ingeniero de Sistemas", "Técnico en..."

# CLASIFICACIÓN
tipo_programa: ENUM  # Ver más abajo
nivel_educativo: ENUM  # Ver más abajo
modalidad: ENUM  # presencial, virtual, hibrido, distancia, dual
area_conocimiento_id: UUID  # STEM, Humanidades, Artes, etc.

# DURACIÓN Y ESTRUCTURA
duracion_total: int  # En unidades (semestres, trimestres, meses)
unidad_duracion: ENUM  # 'semestre', 'trimestre', 'mes', 'año', 'hora'
num_periodos: int  # 10 semestres, 6 trimestres, 18 meses
creditos_totales: int  # Créditos académicos requeridos
horas_totales: int  # Total horas lectivas

# GESTIÓN ACADÉMICA
director_id: UUID  # Director del programa
coordinador_id: UUID  # Coordinador académico
comite_curricular: JSONB  # Array de usuarios en el comité

# ADMISIÓN
requiere_admision: bool
requisitos_admision: JSONB
  # {
  #   "puntaje_minimo_icfes": 280,
  #   "documentos": ["diploma_bachiller", "fotocopia_cedula"],
  #   "entrevista_requerida": true,
  #   "prueba_especifica": "Matemáticas"
  # }
cupos_por_periodo: int
fecha_proxima_admision: date

# COSTOS (si aplica)
costo_inscripcion: decimal
costo_matricula: decimal
costo_por_credito: decimal
costo_total_estimado: decimal
becas_disponibles: JSONB

# CONTENIDO ACADÉMICO
perfil_aspirante: text
perfil_egresado: text
objetivos: text[]
competencias: JSONB
  # [
  #   {"nombre": "Pensamiento crítico", "nivel": "avanzado"},
  #   {"nombre": "Programación", "nivel": "experto"}
  # ]
plan_estudios_url: str  # PDF del plan de estudios
malla_curricular: JSONB  # Estructura de semestres/ciclos

# ACREDITACIÓN
acreditado: bool
entidad_acreditadora: str  # "Ministerio Educación", "CNA"
fecha_acreditacion: date
vigencia_acreditacion: date
resolucion_aprobacion: str  # "Resolución 1234 de 2024"

# ESTADO Y CONFIGURACIÓN
estado: ENUM  # 'activo', 'inactivo', 'suspension', 'proceso_cierre'
permite_inscripcion: bool
visible_publico: bool
destacado: bool
orden_visualizacion: int

# METADATA
metadata: JSONB
  # {
  #   "tipo_metodologia": "PBL",
  #   "enfoque": "internacional",
  #   "doble_titulacion": true,
  #   "practicas_empresariales": true
  # }

# AUDITORÍA
created_at: timestamp
updated_at: timestamp
created_by_id: UUID
```

**ENUMs necesarios:**
```python
class TipoPrograma(str, enum.Enum):
    # Educación Superior
    pregrado = "pregrado"
    especializacion = "especializacion"
    maestria = "maestria"
    doctorado = "doctorado"
    
    # Educación Técnica y Tecnológica
    tecnico_profesional = "tecnico_profesional"
    tecnologico = "tecnologico"
    tecnico_laboral = "tecnico_laboral"
    
    # Educación Básica y Media
    preescolar = "preescolar"
    basica_primaria = "basica_primaria"
    basica_secundaria = "basica_secundaria"
    educacion_media = "educacion_media"
    
    # Educación Continua
    diplomado = "diplomado"
    curso_corto = "curso_corto"
    certificacion = "certificacion"
    bootcamp = "bootcamp"
    taller = "taller"
    seminario = "seminario"
    
    # Educación Artística
    formacion_musical = "formacion_musical"
    formacion_artes_visuales = "formacion_artes_visuales"
    formacion_artes_escenicas = "formacion_artes_escenicas"
    
    # Idiomas
    programa_idiomas = "programa_idiomas"
    
    # Otros
    educacion_informal = "educacion_informal"
    educacion_trabajo = "educacion_trabajo"

class NivelEducativo(str, enum.Enum):
    # Marco ISCED (UNESCO)
    nivel_0_primera_infancia = "nivel_0"  # 0-5 años
    nivel_1_primaria = "nivel_1"  # 6-11 años
    nivel_2_secundaria_baja = "nivel_2"  # 12-14 años
    nivel_3_secundaria_alta = "nivel_3"  # 15-17 años
    nivel_4_post_secundaria = "nivel_4"  # Técnico
    nivel_5_terciaria_ciclo_corto = "nivel_5"  # Tecnólogo (2-3 años)
    nivel_6_grado = "nivel_6"  # Pregrado (4-5 años)
    nivel_7_maestria = "nivel_7"  # Maestría
    nivel_8_doctorado = "nivel_8"  # Doctorado
    
    # Formación Continua
    educacion_continua = "educacion_continua"
    formacion_laboral = "formacion_laboral"
```

---

### 3. **PERIODO_ACADEMICO** (Nueva - CRÍTICA)
```python
# Base del calendario académico

periodo_id: UUID
institucion_id: UUID

# IDENTIFICACIÓN
codigo: str UNIQUE  # "2024-1", "2025-A", "TRIM-2024-3"
nombre: str  # "Primer Semestre 2024", "Período Septiembre-Diciembre"
nombre_corto: str  # "2024-1"

# TIPO Y DURACIÓN
tipo_periodo: ENUM  # 'semestral', 'trimestral', 'cuatrimestral', 'bimestral', 'mensual', 'modular', 'anual', 'continuo'
año: int
numero_periodo: int  # 1, 2, 3 (para identificar dentro del año)

# FECHAS ACADÉMICAS
fecha_inicio: date
fecha_fin: date
total_semanas: int

# FECHAS DE INSCRIPCIÓN
fecha_inicio_inscripcion_regular: date
fecha_fin_inscripcion_regular: date
fecha_inicio_inscripcion_tardia: date
fecha_fin_inscripcion_tardia: date
recargo_inscripcion_tardia: decimal

# FECHAS DE AJUSTE
fecha_inicio_adicion_materias: date
fecha_fin_adicion_materias: date
fecha_inicio_retiro_sin_penalizacion: date
fecha_fin_retiro_sin_penalizacion: date
fecha_limite_retiro: date
penalizacion_retiro_tardio: str  # "W en acta", "50% reembolso"

# FECHAS EVALUACIONES
fecha_inicio_parciales: date
fecha_fin_parciales: date
fecha_inicio_examenes_finales: date
fecha_fin_examenes_finales: date
fecha_inicio_habilitaciones: date
fecha_fin_habilitaciones: date

# FECHAS ADMINISTRATIVAS
fecha_publicacion_notas: date
fecha_limite_reclamos: date
fecha_cierre_notas: date

# CALENDARIO ESPECÍFICO
dias_festivos: JSONB  # Array de fechas sin clases
recesos_academicos: JSONB  
  # [
  #   {"inicio": "2024-12-20", "fin": "2024-12-31", "tipo": "vacaciones"}
  # ]

# ESTADO
estado: ENUM  # 'programado', 'preinscripciones', 'inscripciones_abiertas', 'en_curso', 'evaluaciones', 'finalizado', 'cancelado'
es_periodo_actual: bool  # Solo uno puede ser true

# CONFIGURACIÓN
permite_inscripcion_estudiantes_nuevos: bool
permite_inscripcion_estudiantes_antiguos: bool
permite_inscripcion_externos: bool
permite_cursos_intersemestrales: bool
requiere_pago_previo_inscripcion: bool

# LÍMITES
max_creditos_regulares: int  # Ej: 18 créditos
min_creditos_regulares: int  # Ej: 12 créditos
max_creditos_con_permiso: int  # Ej: 21 créditos

# METADATA
metadata: JSONB
  # {
  #   "calendario_tipo": "A",  # Algunas universidades tienen calendario A y B
  #   "periodo_especial": false,
  #   "intersemestral": false
  # }

created_at: timestamp
```

**Por qué es crítico:**
- Sin períodos académicos NO puedes manejar inscripciones
- Cada institución tiene su propio calendario
- Fechas de inscripción varían por institución
- Base para todo el flujo académico

---

### 4. **CURSO** (Mejorado - Más Robusto)
```python
# Actual: 20 campos
# Propuesto: 45+ campos

# ACTUAL (mantener)
curso_id, institucion_id, coordinador_id, programa_id
nombre, descripcion, objetivos, codigo_curso, codigo_acceso
creditos, horas_academicas, modalidad
fecha_inicio, fecha_fin
activo, permite_inscripcion, maximo_estudiantes, minimo_estudiantes

# AGREGAR:

# CLASIFICACIÓN ACADÉMICA
area_conocimiento_id: UUID  # STEM, Humanidades, etc.
sub_area_conocimiento: str
tipo_curso: ENUM  # 'teorico', 'practico', 'teorico_practico', 'laboratorio', 'taller', 'proyecto', 'seminario', 'electiva'
categoria_curso: ENUM  # 'obligatorio', 'electivo', 'fundamental', 'profesional', 'libre'
nivel_curso: int  # 1-10, para ordenar en malla curricular
nivel_dificultad: ENUM  # 'basico', 'intermedio', 'avanzado', 'experto'

# INFORMACIÓN ACADÉMICA DETALLADA
silabo_url: str  # PDF del sílabo
contenido_programatico: JSONB
  # [
  #   {
  #     "unidad": 1,
  #     "titulo": "Introducción a la Programación",
  #     "temas": ["Variables", "Ciclos", "Condicionales"],
  #     "semanas": 3,
  #     "objetivos": ["Comprender variables", "Aplicar ciclos"]
  #   }
  # ]
competencias: JSONB
  # [
  #   {"competencia": "Pensamiento algorítmico", "nivel_esperado": "intermedio"},
  #   {"competencia": "Resolución de problemas", "nivel_esperado": "avanzado"}
  # ]
resultados_aprendizaje: text[]
  # ["Al finalizar, el estudiante será capaz de...", "Diseñará algoritmos..."]
metodologia: text
estrategias_ensenanza: text[]
bibliografia_obligatoria: JSONB
bibliografia_complementaria: JSONB

# REQUISITOS
prerequisitos_texto: text  # "Haber aprobado Matemáticas I y II"
conocimientos_previos: text[]
habilidades_requeridas: text[]

# EVALUACIÓN
sistema_calificacion: ENUM  # 'numerico', 'conceptual', 'aprobado_reprobado', 'creditos'
nota_minima_aprobacion: decimal  # 3.0, 60%, etc.
criterios_evaluacion: JSONB
  # [
  #   {"tipo": "Parciales", "porcentaje": 40},
  #   {"tipo": "Proyecto Final", "porcentaje": 30},
  #   {"tipo": "Talleres", "porcentaje": 20},
  #   {"tipo": "Participación", "porcentaje": 10}
  # ]

# CONFIGURACIÓN DE MATERIALES
carpeta_drive_id: str
carpeta_drive_url: str
permite_material_estudiantes: bool
requiere_aprobacion_material: bool

# IDIOMA Y ACCESIBILIDAD
idioma_principal: ENUM  # 'español', 'ingles', 'frances', etc.
subtitulos_disponibles: bool
material_accesible: bool  # Para estudiantes con discapacidad

# RECURSOS Y HERRAMIENTAS
recursos_necesarios: JSONB
  # {
  #   "software": ["Python 3.11", "VS Code"],
  #   "hardware": "Computador con 8GB RAM",
  #   "plataformas": ["GitHub", "Replit"]
  # }
herramientas_lms: JSONB  # Integración Moodle, Canvas, etc.

# COSTOS (si aplica)
tiene_costo_adicional: bool
costo_materiales: decimal
costo_laboratorio: decimal

# ESTADÍSTICAS Y CONTROL
veces_ofertado: int
tasa_aprobacion_historica: decimal
calificacion_promedio_estudiantes: decimal  # Rating del curso

# VISIBILIDAD
visible_catalogo: bool
destacado: bool
requiere_autorizacion_inscripcion: bool

# METADATA
tags: text[]  # ["programacion", "python", "backend", "web"]
metadata: JSONB

# AUDITORÍA
created_at, updated_at, created_by_id, updated_by_id
```

---

### 5. **SECCION** (antes "Grupo" - Renombrar y Mejorar)
```python
# Representa una instancia específica de un curso en un período

seccion_id: UUID
curso_id: UUID
periodo_academico_id: UUID  # NUEVO - CRÍTICO

# IDENTIFICACIÓN
codigo_seccion: str  # "A", "B", "01", "02", "NRC-12345"
nombre: str  # "Sección A - Mañana", "Grupo 01 - Virtual"
numero_seccion: int  # Para ordenamiento

# DOCENTE
docente_titular_id: UUID
docente_auxiliar_id: UUID  # Profesor de práctica/monitor
monitor_id: UUID  # Estudiante monitor

# CAPACIDAD Y CUPOS
capacidad_minima: int  # Mínimo para abrir (ej: 15)
capacidad_maxima: int  # Máximo permitido (ej: 40)
capacidad_actual: int  # Estudiantes inscritos actualmente
lista_espera_activa: bool
capacidad_lista_espera: int

# MODALIDAD Y HORARIO
modalidad: ENUM  # 'presencial', 'virtual', 'hibrido'
tipo_encuentro: ENUM  # 'sincronico', 'asincronico', 'mixto'
plataforma_virtual: str  # "Zoom", "Meet", "Teams"
link_clases_virtuales: str

# UBICACIÓN FÍSICA (si es presencial/híbrido)
edificio: str
salon_principal: str
laboratorio_asignado: str

# FECHAS
fecha_inicio: date
fecha_fin: date
fecha_primer_clase: date
fecha_ultima_clase: date

# ESTADO
estado: ENUM  
  # 'programada' - Creada pero no abierta
  # 'abierta' - Permite inscripciones
  # 'llena' - Cupos agotados
  # 'lista_espera' - Llena pero con lista de espera
  # 'en_curso' - Clases iniciadas
  # 'finalizada' - Período terminado
  # 'cancelada' - No se abrió por falta de estudiantes
  # 'suspendida' - Pausada temporalmente

# CONFIGURACIÓN DE INSCRIPCIÓN
permite_inscripcion: bool
requiere_aprobacion_manual: bool
requiere_prerequisitos: bool
permite_oyentes: bool  # Estudiantes que asisten sin créditos
costo_adicional: decimal  # Si tiene costo extra

# VISIBILIDAD Y RESTRICCIONES
visible_estudiantes: bool
solo_programa_especifico: bool  # Solo estudiantes de cierto programa
solo_estudiantes_regulares: bool
permite_estudiantes_externos: bool

# CONFIGURACIÓN ACADÉMICA
permite_retiro: bool
fecha_limite_retiro: date
penalizacion_retiro: str
porcentaje_asistencia_minimo: decimal  # 80%

# ESTADÍSTICAS
total_horas_programadas: int
total_sesiones_programadas: int
sesiones_realizadas: int
tasa_asistencia_actual: decimal

# METADATA
metadata: JSONB
  # {
  #   "grupo_especial": false,
  #   "curso_verano": false,
  #   "intensivo": false,
  #   "honores": false
  # }

# AUDITORÍA
created_at, updated_at, created_by_id
```

**Por qué renombrar "Grupo" a "Sección":**
- "Grupo" es ambiguo (¿grupo de estudiantes? ¿grupo de Facebook?)
- "Sección" es término académico estándar internacional
- Claridad: "Matemáticas 101 - Sección A" vs "Matemáticas 101 - Grupo A"
- Mejora comprensión del modelo

---

### 6. **HORARIO** (Nueva - Gestión de Tiempo)
```python
horario_id: UUID
seccion_id: UUID

# TIEMPO
dia_semana: ENUM  # 'lunes', 'martes', ..., 'domingo'
hora_inicio: time
hora_fin: time
duracion_minutos: int  # Calculado automático

# TIPO DE SESIÓN
tipo_sesion: ENUM  # 'teorica', 'practica', 'laboratorio', 'tutoria', 'examen'
es_recurrente: bool  # true = se repite semanalmente
fecha_inicio_vigencia: date
fecha_fin_vigencia: date

# UBICACIÓN
modalidad: ENUM  # 'presencial', 'virtual', 'hibrido'
aula_id: UUID  # FK a tabla Aula (nueva)
edificio: str
salon: str
url_clase_virtual: str

# EXCEPCIONES (días que NO hay clase)
fechas_excepcion: JSONB  # ["2024-12-25", "2024-01-01"]
fechas_adicionales: JSONB  # Clases extras fuera del horario

# ESTADO
activo: bool
conflicto_detectado: bool
resuelto: bool

# AUDITORÍA
created_at, updated_at
```

**Tabla relacionada: AULA**
```python
aula_id: UUID
institucion_id: UUID
estructura_organizacional_id: UUID  # Sede/Campus/Edificio

codigo_aula: str  # "A-101", "LAB-203"
nombre: str  # "Sala de Conferencias Principal"
edificio: str
piso: int
numero: str

tipo_aula: ENUM  # 'salon_clase', 'laboratorio_computo', 'laboratorio_quimica', 'auditorio', 'biblioteca', 'sala_virtual'

capacidad: int
area_m2: decimal

# EQUIPAMIENTO
equipamiento: JSONB
  # {
  #   "proyector": true,
  #   "computadores": 30,
  #   "aire_acondicionado": true,
  #   "tablero_digital": false,
  #   "microfono": true,
  #   "camaras": 2
  # }

# DISPONIBILIDAD
disponible_reserva: bool
requiere_autorizacion: bool
horario_disponibilidad: JSONB  # Lunes-Viernes 6am-10pm

estado: ENUM  # 'activa', 'mantenimiento', 'fuera_servicio'
activo: bool
```

---

### 7. **INSCRIPCION** (Nueva - CRÍTICO)
```python
inscripcion_id: UUID
estudiante_id: UUID
seccion_id: UUID
periodo_academico_id: UUID

# TIPO Y ESTADO
tipo_inscripcion: ENUM
  # 'regular' - Estudiante regular del programa
  # 'especial' - Estudiante de otro programa
  # 'oyente' - Asiste sin créditos
  # 'convalidacion' - Para convalidar créditos
  # 'repeticion' - Repitiendo el curso
  # 'validacion' - Por validación de conocimientos
  # 'intersemestral' - Curso de verano/intersemestral
  # 'nivelacion' - Curso de nivelación

estado: ENUM
  # 'pre_inscrita' - Carrito de compras
  # 'pendiente_pago' - Esperando pago
  # 'pendiente_aprobacion' - Requiere autorización coordinador
  # 'aprobada' - Inscripción confirmada
  # 'rechazada' - No cumple requisitos o cupo lleno
  # 'en_espera' - Lista de espera
  # 'retirada_estudiante' - Estudiante canceló
  # 'retirada_administrativa' - Institución canceló
  # 'completada' - Curso finalizado con nota

# FECHAS DEL FLUJO
fecha_solicitud: timestamp
fecha_aprobacion: timestamp
fecha_rechazo: timestamp
fecha_pago: timestamp
fecha_retiro: timestamp
fecha_finalizacion: timestamp

# CONTROL DE LISTA DE ESPERA
en_lista_espera: bool
posicion_lista_espera: int
fecha_ingreso_lista_espera: timestamp

# PRIORIDAD (para resolver quién entra primero)
prioridad: int  # 1=alta, 5=normal, 10=baja
  # Ejemplos de prioridad:
  # - Estudiante de último semestre: prioridad 1
  # - Estudiante regular en semestre normal: prioridad 5
  # - Estudiante de otro programa: prioridad 8
razon_prioridad: str

# APROBACIONES Y VALIDACIONES
requiere_prerequisitos: bool
prerequisitos_cumplidos: bool
prerequisitos_validados_por_id: UUID
fecha_validacion_prerequisitos: timestamp

requiere_aprobacion_coordinador: bool
aprobado_por_id: UUID
motivo_aprobacion: text

# RECHAZO
motivo_rechazo: ENUM
  # 'cupo_lleno'
  # 'prerequisitos_no_cumplidos'
  # 'conflicto_horario'
  # 'no_pertenece_programa'
  # 'deuda_financiera'
  # 'suspension_academica'
  # 'otro'
motivo_rechazo_detalle: text

# RETIRO
tipo_retiro: ENUM  # 'voluntario', 'administrativo', 'fuerza_mayor'
motivo_retiro: text
con_reembolso: bool
porcentaje_reembolso: decimal
penalizacion: str  # "W en el acta", "Pérdida de créditos"

# PAGOS (si aplica)
costo_inscripcion: decimal
costo_curso: decimal
descuento_aplicado: decimal
monto_pagado: decimal
monto_pendiente: decimal
forma_pago: str
comprobante_pago_url: str

# CALIFICACIÓN FINAL
nota_final: decimal
estado_aprobacion: ENUM  # 'aprobado', 'reprobado', 'retirado', 'en_curso'
creditos_otorgados: int

# ASISTENCIA Y PARTICIPACIÓN
total_asistencias: int
total_inasistencias: int
porcentaje_asistencia: decimal
cumple_asistencia_minima: bool

# OBSERVACIONES
observaciones_estudiante: text  # Comentarios del estudiante al inscribirse
observaciones_administrativas: text
requiere_ajustes_especiales: bool  # Discapacidad, etc.
ajustes_especiales: JSONB

# AUDITORÍA
created_at, updated_at, created_by_id, updated_by_id

# CONSTRAINTS
UNIQUE(estudiante_id, seccion_id, periodo_academico_id)
```

**Flujo de estados de inscripción:**
```
1. PRE_INSCRITA (estudiante selecciona en carrito)
     ↓
2. PENDIENTE_PAGO (confirma inscripción)
     ↓
3. PENDIENTE_APROBACION (si requiere autorización)
     ↓
4. APROBADA (todo OK, inscripción confirmada)
     ↓
5. EN_CURSO (período académico iniciado)
     ↓
6. COMPLETADA (curso finalizado con nota)

CAMINOS ALTERNATIVOS:
- RECHAZADA (no cumple requisitos)
- EN_ESPERA (cupo lleno)
- RETIRADA (estudiante cancela)
```

---

### 8. **PREREQUISITO** (Nueva - Gestión de Dependencias)
```python
prerequisito_id: UUID
curso_id: UUID  # Curso que REQUIERE el prerequisito
curso_prerequisito_id: UUID  # Curso que ES prerequisito

# TIPO DE RELACIÓN
tipo: ENUM
  # 'obligatorio' - Debe haberse cursado y aprobado
  # 'recomendado' - Se sugiere pero no es obligatorio
  # 'equivalente' - Puede reemplazarse por otro curso
  # 'corequisito' - Debe cursarse al mismo tiempo

es_corequisito: bool  # Deben cursarse simultáneamente

# CONDICIONES DE APROBACIÓN
requiere_aprobacion: bool
nota_minima_requerida: decimal  # 3.0, 60, etc.
requiere_creditos: bool
creditos_minimos_requeridos: int

# ALTERNATIVAS (puede cumplir con uno de varios)
grupo_alternativas: int
  # Ejemplo: 
  # - Curso "Programación Avanzada" requiere:
  #   - (Programación I [grupo 1] O Programación Básica [grupo 1])
  #   - Y (Matemáticas I [grupo 2] O Cálculo I [grupo 2])
  # Si grupo_alternativas = 1, cualquiera de ese grupo sirve

# VALIDACIÓN AUTOMÁTICA
validacion_automatica: bool
permite_excepcion: bool  # Coordinador puede aprobar sin cumplir

# DESCRIPCIÓN
descripcion_requisito: text  # "Haber aprobado con mínimo 3.5"
visible_estudiante: bool

# VIGENCIA
fecha_inicio_vigencia: date
fecha_fin_vigencia: date
activo: bool

# AUDITORÍA
created_at, updated_at
```

**Tabla auxiliar para manejar equivalencias:**
```python
# EQUIVALENCIA_CURSO
equivalencia_id: UUID
curso_id: UUID
curso_equivalente_id: UUID
porcentaje_equivalencia: decimal  # 100% = totalmente equivalente
observaciones: text
aprobado_por_id: UUID
fecha_aprobacion: date
```

---

## 🔄 FLUJOS CLAVE QUE EL SISTEMA DEBE SOPORTAR

### FLUJO 1: Inscripción de Estudiante
```
1. Estudiante consulta catálogo de cursos del período
2. Verifica prerrequisitos automáticamente
3. Sistema detecta conflictos de horario
4. Estudiante pre-inscribe cursos (carrito)
5. Sistema valida:
   - Cupos disponibles
   - Conflictos de horario
   - Prerrequisitos cumplidos
   - Límite de créditos
   - Deudas financieras
6. Si requiere aprobación → notifica coordinador
7. Coordinador aprueba/rechaza
8. Si aprueba → Estudiante paga (si aplica)
9. Inscripción CONFIRMADA
10. Sistema actualiza cupos y genera horario
```

### FLUJO 2: Apertura de Período Académico
```
1. Admin crea nuevo período académico
2. Define fechas (inscripciones, clases, exámenes)
3. Coordinadores crean secciones de cursos
4. Asignan docentes y horarios
5. Sistema valida conflictos de horario (docente/aula)
6. Se publican cursos para inscripción
7. Período abre inscripciones automáticamente
8. Estudiantes se inscriben
9. Sistema cierra inscripciones automáticamente
10. Inician clases
```

### FLUJO 3: Gestión de Cupos y Listas de Espera
```
1. Estudiante intenta inscribir curso lleno
2. Sistema ofrece lista de espera
3. Estudiante acepta entrar en lista (posición N)
4. Otro estudiante se retira → Cupo disponible
5. Sistema notifica automáticamente al primero en lista
6. Estudiante tiene 48h para confirmar
7. Si no confirma → Pasa al siguiente en lista
8. Si confirma → Inscripción automática
```

### FLUJO 4: Validación de Prerrequisitos
```
1. Estudiante intenta inscribir "Programación II"
2. Sistema verifica:
   - ¿Cursó "Programación I"?
   - ¿La aprobó?
   - ¿Nota >= 3.0?
3. Si NO cumple:
   - Bloquea inscripción
   - Muestra requisitos faltantes
   - Ofrece alternativa (si hay curso equivalente)
4. Si cumple parcialmente:
   - Permite solicitar excepción
   - Notifica a coordinador
5. Coordinador puede aprobar manualmente
```

---

## 🎨 CONFIGURACIÓN POR TIPO DE INSTITUCIÓN

### Universidad
```json
{
  "estructura_organizacional": ["Facultad", "Departamento"],
  "tipo_programa": "pregrado",
  "nivel_educativo": "nivel_6_grado",
  "duracion": {"valor": 10, "unidad": "semestre"},
  "tipo_periodo": "semestral",
  "sistema_creditos": true,
  "creditos_por_semestre_min": 12,
  "creditos_por_semestre_max": 18,
  "requiere_prerequisitos": true,
  "permite_electivas": true,
  "tiene_practicas": true
}
```

### Instituto SENA
```json
{
  "estructura_organizacional": ["Centro", "Área Técnica"],
  "tipo_programa": "tecnico_profesional",
  "nivel_educativo": "nivel_4_post_secundaria",
  "duracion": {"valor": 18, "unidad": "mes"},
  "tipo_periodo": "continuo",
  "sistema_creditos": false,
  "sistema_fichas": true,
  "modalidad_dominante": "presencial",
  "tiene_etapa_practica": true,
  "duracion_etapa_practica": {"valor": 6, "unidad": "mes"}
}
```

### Academia de Idiomas
```json
{
  "estructura_organizacional": ["Sede"],
  "tipo_programa": "programa_idiomas",
  "nivel_educativo": "educacion_continua",
  "duracion": {"valor": 6, "unidad": "mes"},
  "tipo_periodo": "bimestral",
  "sistema_niveles": "MCER",  // A1, A2, B1, B2, C1, C2
  "niveles": ["A1", "A2", "B1", "B2", "C1", "C2"],
  "duracion_nivel": {"valor": 2, "unidad": "mes"},
  "permite_intensivos": true,
  "requiere_examen_clasificacion": true
}
```

### Colegio
```json
{
  "estructura_organizacional": ["Sede", "Nivel", "Grado"],
  "tipo_programa": "basica_primaria",
  "nivel_educativo": "nivel_1_primaria",
  "duracion": {"valor": 1, "unidad": "año"},
  "tipo_periodo": "anual",
  "sistema_creditos": false,
  "sistema_notas": "numerico_1_a_5",
  "grados": ["1°", "2°", "3°", "4°", "5°"],
  "jornadas": ["mañana", "tarde"],
  "salon_fijo": true,
  "mismo_docente_varias_materias": true
}
```

---

## 📊 TABLAS RESUMEN

### Prioridad de Implementación

| # | Entidad | Prioridad | Esfuerzo | Dependencias |
|---|---------|-----------|----------|--------------|
| 1 | **PeriodoAcademico** | 🔴 CRÍTICO | 2 días | Institución |
| 2 | **Mejora Programa** | 🔴 CRÍTICO | 2 días | Institución, Estructura Org |
| 3 | **Inscripcion** | 🔴 CRÍTICO | 3 días | Estudiante, Sección, Período |
| 4 | **Seccion** (renombrar Grupo) | 🟡 ALTA | 2 días | Curso, Período, Docente |
| 5 | **Horario** + Aula | 🟡 ALTA | 3 días | Sección |
| 6 | **Prerequisito** | 🟡 ALTA | 2 días | Curso |
| 7 | **EstructuraOrganizacional** | 🟡 ALTA | 2 días | Institución |
| 8 | **Mejora Curso** | 🟢 MEDIA | 2 días | Programa, Área |
| 9 | **AreaConocimiento** | 🟢 MEDIA | 1 día | Institución |
| 10 | **ContenidoProgramatico** | 🟢 MEDIA | 1 día | Curso |

**Total estimado COMPLETO**: ~20 días de desarrollo

---

## 🚀 ESTRATEGIA DE IMPLEMENTACIÓN

### FASE 1: Fundamentos (Semana 1-2)
✅ **Objetivo**: Base sólida para todo el sistema

1. **Día 1-2**: 
   - Mejorar ENUMs (programa, curso, inscripción, estados)
   - Crear modelo PeriodoAcademico completo
   - Crear migración

2. **Día 3-4**:
   - Mejorar modelo Programa (35+ campos)
   - Crear modelo EstructuraOrganizacional
   - Crear migraciones

3. **Día 5-6**:
   - Renombrar Grupo → Seccion
   - Mejorar modelo Seccion (40+ campos)
   - Actualizar todas las relaciones

4. **Día 7-8**:
   - Mejorar modelo Curso (45+ campos)
   - Crear modelo AreaConocimiento
   - Migraciones

### FASE 2: Inscripciones y Horarios (Semana 3-4)

5. **Día 9-11**:
   - Crear modelo Inscripcion completo
   - Implementar lógica de estados (FSM)
   - Crear servicio de inscripción
   - CRUD completo

6. **Día 12-14**:
   - Crear modelo Horario
   - Crear modelo Aula
   - Implementar detección conflictos
   - Servicio de horarios

7. **Día 15-16**:
   - Crear modelo Prerequisito
   - Implementar validación automática
   - Servicio de prerrequisitos

### FASE 3: Schemas y APIs (Semana 5)

8. **Día 17-18**:
   - Crear todos los schemas Pydantic
   - Validaciones de negocio
   - Documentación

9. **Día 19-20**:
   - Crear endpoints RESTful
   - Documentación OpenAPI
   - Postman collections

### FASE 4: Testing (Semana 6)

10. **Día 21-24**:
    - Tests unitarios (models, schemas)
    - Tests integración (CRUD, services)
    - Tests funcionales (endpoints)
    - Tests de flujos completos

### FASE 5: Frontend (Semana 7-8)

11. **Día 25-30**:
    - Interfaces de administración
    - Portal de inscripciones
    - Gestión de horarios
    - Reportes y dashboards

---

## 🎯 CRITERIOS DE ÉXITO

### El sistema será exitoso cuando:

✅ **Universalidad**:
- Una universidad puede configurarse completa en < 2 horas
- Un colegio puede adaptarlo sin código en < 1 hora
- SENA puede modelar sus programas técnicos sin modificaciones
- Academia de idiomas puede crear niveles MCER completos

✅ **Robustez**:
- Detección automática de conflictos de horario
- Validación automática de prerrequisitos
- Gestión de cupos con listas de espera
- Flujos de aprobación configurables

✅ **Escalabilidad**:
- Soporta 10,000+ estudiantes por institución
- Maneja 500+ cursos simultáneos
- Responde en < 200ms para consultas comunes
- Cache efectivo para reducir carga DB

✅ **Profesionalismo**:
- Documentación completa en español e inglés
- APIs RESTful con OpenAPI 3.0
- Tests coverage > 80%
- Logs estructurados para auditoría
- Respaldos automáticos diarios

---

## 📝 PRÓXIMOS PASOS INMEDIATOS

### Opción A: Implementación Secuencial (Recomendada)
Vamos paso a paso, probando cada componente:
1. PeriodoAcademico → Test → Deploy
2. Programa Mejorado → Test → Deploy
3. Inscripcion → Test → Deploy
... (continuar)

### Opción B: Implementación por Bloques
Implementamos todo un bloque funcional completo:
1. Bloque "Estructura Base" (Período + Programa + Estructura Org)
2. Bloque "Gestión Académica" (Curso + Sección + Horario)
3. Bloque "Inscripciones" (Inscripción + Prerequisito + Validaciones)

### Opción C: MVP Rápido
Implementamos solo lo CRÍTICO para un flujo mínimo funcional:
- PeriodoAcademico (simple)
- Inscripcion (básica)
- Mejora mínima Programa/Curso/Sección
- Deploy y prueba con usuarios reales
- Iteramos mejoras basadas en feedback

---

## 🤔 DECISIÓN REQUERIDA

**¿Qué enfoque prefieres?**

1. **Opción A**: Lento pero seguro (6 semanas)
2. **Opción B**: Bloques funcionales (4 semanas)
3. **Opción C**: MVP iterativo (2 semanas iniciales + mejoras)

**¿Comenzamos con algún componente específico que sea más crítico para tu caso de uso?**

Por ejemplo:
- Si tu prioridad son inscripciones → Empezamos por PeriodoAcademico + Inscripcion
- Si necesitas claridad organizacional → EstructuraOrganizacional + Programa
- Si urge horarios → Seccion + Horario + Aula

**Dime y arrancamos! 🚀**
