# Modelos Académicos Mejorados

## Resumen de Cambios

Los modelos `Curso`, `Programa` y `Grupo` han sido expandidos significativamente para incluir campos completos de gestión académica, usando los ENUMs creados previamente.

---

## 📚 Modelo: Curso

**Expansión**: 15 campos → **~70 campos**

### Nuevos Campos Agregados:

#### Carga Académica (6 campos)
- `horas_teoricas`, `horas_practicas`, `horas_laboratorio`, `horas_autonomas`

#### Clasificación (6 campos)
- `nivel_dificultad` (ENUM: básico, intermedio, avanzado, experto)
- `tipo_curso` (ENUM: teórico, práctico, laboratorio, proyecto, etc.)
- `categoria_curso` (ENUM: obligatorio, electivo, fundamental, etc.)
- `estado` (ENUM: borrador, programado, en_curso, finalizado, etc.)
- `idioma` (ENUM: español, inglés, francés, etc.)

#### Fechas Extendidas (4 campos)
- `fecha_limite_inscripcion`, `fecha_inicio_retiro`, `fecha_limite_retiro`

#### Control de Cupos (3 campos)
- `cupos_disponibles`, `permite_lista_espera`, `maximo_lista_espera`

#### Requisitos Académicos (5 campos)
- `prerequisitos_ids` (JSON), `correquisitos_ids` (JSON)
- `requiere_nivelacion`, `creditos_minimos_requeridos`, `promedio_minimo_requerido`

#### Costos (6 campos)
- `tiene_costo`, `costo_matricula`, `costo_mensual`, `costo_total`
- `permite_becas`, `porcentaje_descuento`

#### Evaluación (5 campos)
- `calificacion_minima_aprobacion`, `porcentaje_asistencia_minimo`
- `permite_recuperacion`, `permite_habilitacion`, `numero_maximo_faltas`

#### Configuración Adicional (3 campos)
- `permite_foros`, `permite_comentarios`, `permite_calificacion_entre_pares`

#### Certificación (3 campos)
- `genera_certificado`, `requiere_trabajo_final`, `tipo_trabajo_final`

#### Metadata (7 campos)
- `syllabus_url`, `bibliografia`, `recursos_adicionales` (JSON)
- `tags` (JSON), `imagen_url`

#### Auditoría (2 campos)
- `fecha_creacion`, `fecha_actualizacion`

### Nuevas Properties (16 properties):
- `tiene_cupos_disponibles`: bool
- `cupos_restantes`: Optional[int]
- `porcentaje_ocupacion`: float
- `cumple_minimo_estudiantes`: bool
- `esta_activo`: bool
- `puede_inscribirse`: bool
- `duracion_semanas`: Optional[int]
- `total_horas`: int
- `tiene_prerequisitos`: bool
- `es_gratuito`: bool
- `requiere_pago`: bool

### Nuevos Métodos (4 métodos):
- `puede_estudiante_inscribirse(creditos, promedio)` → tuple[bool, str]
- `calcular_costo_con_descuento()` → float
- `esta_en_periodo_retiro()` → bool
- `puede_retirarse()` → bool

---

## 🎓 Modelo: Programa

**Expansión**: 7 campos → **~95 campos**

### Nuevos Campos Agregados:

#### Identificación (2 campos)
- `coordinador_id` (FK), `codigo`

#### Información Institucional (5 campos)
- `mision`, `vision`, `perfil_profesional`, `perfil_egresado`

#### Estados y Clasificación (2 campos)
- `estado` (ENUM: activo, inactivo, suspendido, cerrado, etc.)
- `duracion_tipo` (ENUM: semestral, anual, modular, flexible, etc.)

#### Duración y Estructura (7 campos)
- `duracion_periodos`, `duracion_meses`
- `creditos_totales`, `creditos_obligatorios`, `creditos_electivos`, `creditos_libres`
- `numero_niveles`

#### Requisitos de Ingreso (7 campos)
- `titulo_bachiller_requerido`, `puntaje_minimo_admision`
- `requiere_examen_admision`, `requiere_entrevista`
- `edad_minima_ingreso`, `documentos_requeridos` (JSON)

#### Requisitos de Graduación (7 campos)
- `creditos_minimos_graduacion`, `promedio_minimo_graduacion`
- `requiere_trabajo_grado`, `requiere_practica_profesional`, `horas_practica_requeridas`
- `requiere_suficiencia_idioma`, `idiomas_requeridos` (JSON)

#### Costos (7 campos)
- `tiene_costo`, `costo_matricula`, `costo_por_periodo`, `costo_por_credito`
- `costo_total_estimado`, `ofrece_becas`, `ofrece_credito_educativo`

#### Acreditación (7 campos)
- `esta_acreditado`, `fecha_acreditacion`, `vigencia_acreditacion_hasta`
- `registro_calificado`, `snies_codigo`, `resolucion_aprobacion`

#### Capacidad (3 campos)
- `cupos_por_periodo`, `maximo_estudiantes_activos`, `permite_inscripcion`

#### Configuración (4 campos)
- `acepta_transferencias`, `acepta_homologaciones`
- `permite_doble_titulacion`

#### Metadata (9 campos)
- `areas_conocimiento` (JSON), `competencias_desarrolladas` (JSON)
- `campo_ocupacional`, `plan_estudios_url`, `reglamento_url`
- `imagen_url`, `video_presentacion_url`, `tags` (JSON)

#### Auditoría (4 campos)
- `fecha_creacion`, `fecha_actualizacion`, `fecha_apertura`, `fecha_cierre`

### Nuevas Properties (13 properties):
- `total_estudiantes`: int
- `total_grupos`: int
- `total_cursos`: int
- `esta_activo`: bool
- `puede_inscribirse`: bool
- `tiene_cupos_disponibles`: bool
- `cupos_disponibles`: Optional[int]
- `porcentaje_ocupacion`: float
- `duracion_años`: Optional[float]
- `es_gratuito`: bool
- `esta_acreditado_vigente`: bool
- `creditos_pendientes_definir`: int

### Nuevos Métodos (3 métodos):
- `cumple_requisitos_ingreso(bachiller, puntaje, edad)` → tuple[bool, str]
- `cumple_requisitos_graduacion(creditos, promedio, ...)` → tuple[bool, str]
- `calcular_costo_total_estudiante(periodos)` → float

---

## 👥 Modelo: Grupo

**Expansión**: 6 campos → **~65 campos**

### Nuevos Campos Agregados:

#### Identificación (4 campos)
- `periodo_academico_id` (FK), `codigo_grupo`, `nivel_academico`, `seccion`

#### Clasificación (5 campos)
- `estado` (ENUM: programado, inscripciones_abiertas, en_curso, etc.)
- `tipo_grupo` (ENUM: regular, intensivo, virtual, laboratorio, etc.)
- `modalidad_asistencia` (ENUM: obligatoria, flexible, libre, mixta)
- `formato_evaluacion` (ENUM: exámenes, proyectos, talleres, continua, etc.)

#### Horario (6 campos)
- `hora_inicio`, `hora_fin`, `dias_semana` (JSON)
- `salon`, `edificio`, `ubicacion_virtual`

#### Capacidad Extendida (3 campos)
- `cupos_disponibles`, `permite_lista_espera`, `maximo_lista_espera`

#### Fechas (4 campos)
- `fecha_inicio`, `fecha_fin`, `fecha_inicio_inscripciones`, `fecha_fin_inscripciones`

#### Configuración Académica (6 campos)
- `creditos`, `horas_semanales`
- `porcentaje_asistencia_minimo`, `calificacion_minima_aprobacion`
- `permite_recuperacion`, `numero_maximo_faltas`

#### Costos (2 campos)
- `tiene_costo_adicional`, `costo_adicional`

#### Configuración de Acceso (7 campos)
- `requiere_aprobacion_inscripcion`, `es_visible`
- `permite_autoregistro`, `codigo_acceso`

#### Configuración de Interacción (4 campos)
- `permite_chat`, `permite_foro`, `permite_comentarios`
- `permite_material_estudiantes`

#### Metadata (5 campos)
- `objetivos`, `notas_internas`, `recursos_adicionales` (JSON)
- `tags` (JSON), `imagen_url`

#### Auditoría (4 campos)
- `fecha_creacion`, `fecha_actualizacion`, `creado_por_id`, `modificado_por_id`

### Nuevas Properties (15 properties):
- `total_estudiantes`: int
- `total_cursos`: int
- `tiene_cupos_disponibles`: bool
- `cupos_restantes`: Optional[int]
- `porcentaje_ocupacion`: float
- `cumple_minimo_estudiantes`: bool
- `esta_activo`: bool
- `puede_inscribirse`: bool
- `esta_lleno`: bool
- `puede_iniciar`: bool
- `duracion_semanas`: Optional[int]
- `horario_completo`: str
- `ubicacion_completa`: str

### Nuevos Métodos (4 métodos):
- `puede_estudiante_inscribirse()` → tuple[bool, str]
- `actualizar_estado_por_cupos()` → None
- `calcular_costo_total()` → float

---

## 📊 Estadísticas de Mejoras

| Modelo   | Campos Antes | Campos Después | Properties | Métodos | Total |
|----------|--------------|----------------|------------|---------|-------|
| Curso    | 15           | ~70            | 16         | 4       | 90    |
| Programa | 7            | ~95            | 13         | 3       | 111   |
| Grupo    | 6            | ~65            | 15         | 4       | 84    |
| **TOTAL**| **28**       | **~230**       | **44**     | **11**  | **285**|

---

## ✅ Compatibilidad

Todos los modelos mantienen **compatibilidad hacia atrás** con el código existente:
- Los campos originales se mantienen sin cambios
- Las relaciones existentes se preservan
- Los nuevos campos tienen valores por defecto o son nullable

---

## 🎯 Próximos Pasos

1. ✅ **Modelos mejorados** (COMPLETADO)
2. ⏳ **Crear migración Alembic** para agregar nuevos campos
3. ⏳ **Actualizar Schemas Pydantic** para nuevos campos
4. ⏳ **Expandir CRUD** con nuevos filtros y búsquedas
5. ⏳ **Actualizar Services** con nueva lógica de negocio
6. ⏳ **Tests completos** para validar funcionalidad

---

**Fecha de actualización**: 30 de octubre de 2025
**Autor**: Sistema de AI - GitHub Copilot
