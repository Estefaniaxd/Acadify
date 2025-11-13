# 📊 Documentación de Base de Datos - Acadify

**Fecha de generación**: 2025-10-29
**Total de tablas**: 53

---

## 📋 Índice de Tablas

1. [AdministradorSistema](#administradorsistema)
2. [ArchivoChat](#archivochat)
3. [Asistencia](#asistencia)
4. [ChatBot](#chatbot)
5. [ChatGrupo](#chatgrupo)
6. [Clase](#clase)
7. [Comentario](#comentario)
8. [Coordinador](#coordinador)
9. [Curso](#curso)
10. [CursoDocente](#cursodocente)
11. [Docente](#docente)
12. [EscalaCalificacion](#escalacalificacion)
13. [Estudiante](#estudiante)
14. [EstudianteGrupo](#estudiantegrupo)
15. [FAQBot](#faqbot)
16. [Grupo](#grupo)
17. [GrupoCurso](#grupocurso)
18. [HistorialPuntos](#historialpuntos)
19. [Insignia](#insignia)
20. [Institucion](#institucion)
21. [InstitucionCoordinador](#institucioncoordinador)
22. [MaterialClase](#materialclase)
23. [MaterialCurso](#materialcurso)
24. [MaterialEducativo](#materialeducativo)
25. [OAuthProvider](#oauthprovider)
26. [Plataforma](#plataforma)
27. [Programa](#programa)
28. [Reacciones](#reacciones)
29. [Recompensa](#recompensa)
30. [Tema](#tema)
31. [TemaPersonalizado](#temapersonalizado)
32. [TemaPredefinido](#temapredefinido)
33. [Usuario](#usuario)
34. [UsuarioInsignia](#usuarioinsignia)
35. [UsuarioPuntos](#usuariopuntos)
36. [UsuarioRecompensa](#usuariorecompensa)
37. [ValorCalificacion](#valorcalificacion)
38. [avatar_asset](#avatar_asset)
39. [banco_preguntas](#banco_preguntas)
40. [configuracion_evaluaciones](#configuracion_evaluaciones)
41. [entregas_tareas](#entregas_tareas)
42. [estadisticas_examen](#estadisticas_examen)
43. [eventos_anti_trampa](#eventos_anti_trampa)
44. [examenes](#examenes)
45. [intentos_examen](#intentos_examen)
46. [mensajes](#mensajes)
47. [notificaciones](#notificaciones)
48. [preguntas_examen](#preguntas_examen)
49. [respuestas_estudiante](#respuestas_estudiante)
50. [rubricas](#rubricas)
51. [salas_chat](#salas_chat)
52. [tareas](#tareas)
53. [user_avatar](#user_avatar)

---

## AdministradorSistema

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| administrador_id | uuid | NO | - | ✅ |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| administrador_id | Usuario.usuario_id | Usuario |

---

## ArchivoChat

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| archivo_id | uuid | NO | gen_random_uuid() | ✅ |
| chat_grupo_id | uuid | NO | - |  |
| usuario_id | uuid | YES | - |  |
| nombre_archivo | text | NO | - |  |
| url_archivo | text | NO | - |  |
| fecha_envio | timestamp with time zone | NO | now() |  |
| tipo_archivo | text | YES | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| chat_grupo_id | ChatGrupo.chat_grupo_id | ChatGrupo |
| usuario_id | Usuario.usuario_id | Usuario |

---

## Asistencia

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| asistencia_id | uuid | NO | gen_random_uuid() | ✅ |
| clase_id | uuid | NO | - |  |
| estudiante_id | uuid | NO | - |  |
| estado | USER-DEFINED | NO | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| clase_id | Clase.clase_id | Clase |
| estudiante_id | Estudiante.estudiante_id | Estudiante |

---

## ChatBot

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| chat_bot_id | uuid | NO | gen_random_uuid() | ✅ |
| nombre | character varying(100) | NO | - |  |
| descripcion | text | NO | - |  |
| foto_perfil_url | text | NO | - |  |
| activo | boolean | YES | - |  |
| fecha_registro | date | YES | now() |  |

### Índices

- `ChatBot_nombre_key`

---

## ChatGrupo

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| chat_grupo_id | uuid | NO | gen_random_uuid() | ✅ |
| grupo_id | uuid | NO | - |  |
| fecha_creacion | timestamp with time zone | NO | now() |  |
| descripcion | text | YES | - |  |
| foto_perfil | text | YES | - |  |
| permite_archivos | boolean | NO | true |  |
| capacidad_almacenamiento | integer | NO | 52428800 |  |
| estado_chat | USER-DEFINED | NO | 'activo'::estado_chat_grupo |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| grupo_id | Grupo.grupo_id | Grupo |

---

## Clase

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| clase_id | uuid | NO | gen_random_uuid() | ✅ |
| grupo_curso_id | uuid | NO | - |  |
| plataforma_id | uuid | YES | - |  |
| titulo | text | NO | - |  |
| descripcion | text | YES | - |  |
| hora_inicio | timestamp with time zone | NO | now() |  |
| duracion | interval | NO | - |  |
| link_videollamada | text | NO | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| grupo_curso_id | GrupoCurso.grupo_curso_id | GrupoCurso |
| plataforma_id | Plataforma.plataforma_id | Plataforma |

---

## Comentario

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| comentario_id | uuid | NO | gen_random_uuid() | ✅ |
| curso_id | uuid | NO | - |  |
| autor_id | uuid | NO | - |  |
| contenido | text | NO | - |  |
| tipo | USER-DEFINED | NO | 'comentario'::tipocomentario |  |
| archivos_adjuntos | json | YES | - |  |
| comentario_padre_id | uuid | YES | - |  |
| fecha_creacion | timestamp with time zone | NO | now() |  |
| fecha_actualizacion | timestamp with time zone | YES | - |  |
| fecha_eliminacion | timestamp with time zone | YES | - |  |
| esta_eliminado | boolean | NO | false |  |
| editado | boolean | NO | false |  |
| activo | boolean | NO | true |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| curso_id | Curso.curso_id | Curso |
| autor_id | Usuario.usuario_id | Usuario |
| comentario_padre_id | Comentario.comentario_id | Comentario |

### Índices

- `idx_comentarios_curso_id`
- `idx_comentarios_padre_id`
- `idx_comentarios_autor_id`
- `idx_comentarios_fecha_creacion`
- `idx_comentarios_curso_tipo_fecha`
- `idx_comentario_curso_id`
- `idx_comentario_autor_id`
- `idx_comentario_fecha_creacion`
- `idx_comentario_tipo`
- `idx_comentario_activo`
- `idx_comentario_curso_fecha`
- `idx_comentario_autor_fecha`
- `idx_comentario_tipo_activo`
- `idx_comentario_padre`

---

## Coordinador

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| coordinador_id | uuid | NO | - | ✅ |
| horario_atencion | character varying(50) | YES | - |  |
| fecha_inicio_carrera | date | NO | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| coordinador_id | Usuario.usuario_id | Usuario |

---

## Curso

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| curso_id | uuid | NO | gen_random_uuid() | ✅ |
| institucion_id | uuid | NO | - |  |
| coordinador_id | uuid | YES | - |  |
| programa_id | uuid | NO | - |  |
| nombre | character varying(50) | NO | - |  |
| descripcion | text | YES | - |  |
| modalidad | USER-DEFINED | NO | - |  |
| fecha_inicio | date | YES | - |  |
| fecha_fin | date | YES | - |  |
| objetivos | text | YES | - |  |
| codigo_curso | character varying(20) | YES | - |  |
| codigo_acceso | character varying(10) | YES | - |  |
| creditos | integer | YES | 0 |  |
| horas_academicas | integer | YES | 0 |  |
| activo | boolean | NO | true |  |
| permite_inscripcion | boolean | NO | true |  |
| maximo_estudiantes | integer | YES | - |  |
| minimo_estudiantes | integer | YES | 1 |  |
| permite_material_estudiantes | boolean | NO | false |  |
| requiere_aprobacion_material | boolean | NO | true |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| coordinador_id | Coordinador.coordinador_id | Coordinador |
| institucion_id | Institucion.institucion_id | Institucion |
| programa_id | Programa.programa_id | Programa |

### Índices

- `Curso_codigo_acceso_key`
- `idx_curso_codigo_acceso`
- `idx_curso_institucion_id`
- `idx_curso_programa_id`
- `idx_curso_coordinador_id`
- `idx_curso_institucion_programa`
- `uq_curso_nombre`

---

## CursoDocente

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| curso_id | uuid | NO | - | ✅ |
| docente_id | uuid | NO | - | ✅ |
| fecha_asignacion | date | YES | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| curso_id | Curso.curso_id | Curso |
| docente_id | Docente.docente_id | Docente |

---

## Docente

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| docente_id | uuid | NO | - | ✅ |
| area_conocimiento | character varying(50) | NO | - |  |
| fecha_vinculacion | date | NO | - |  |
| tipo_vinculacion | USER-DEFINED | NO | 'planta'::tipo_vinculacion_institucion |  |
| titulo_academico | character varying(50) | YES | - |  |
| horas_semanales | smallint | YES | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| docente_id | Usuario.usuario_id | Usuario |

---

## EscalaCalificacion

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| escala_id | uuid | NO | gen_random_uuid() | ✅ |
| institucion_id | uuid | NO | - |  |
| nombre | character varying(50) | NO | - |  |
| tipo | USER-DEFINED | NO | - |  |
| min_valor | numeric | YES | - |  |
| max_valor | numeric | YES | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| institucion_id | Institucion.institucion_id | Institucion |

---

## Estudiante

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| estudiante_id | uuid | NO | - | ✅ |
| programa_id | uuid | YES | - |  |
| fecha_ingreso | date | NO | - |  |
| creditos_aprobados | smallint | YES | - |  |
| etapa_formativa | USER-DEFINED | NO | 'i'::etapa_formativa_estudiante |  |
| promedio_acumulado | numeric | YES | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| estudiante_id | Usuario.usuario_id | Usuario |
| programa_id | Programa.programa_id | Programa |

---

## EstudianteGrupo

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| grupo_id | uuid | NO | - | ✅ |
| estudiante_id | uuid | NO | - | ✅ |
| fecha_vinculacion | date | NO | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| estudiante_id | Estudiante.estudiante_id | Estudiante |
| grupo_id | Grupo.grupo_id | Grupo |

### Índices

- `idx_estudiante_grupo_grupo_id`
- `idx_estudiante_grupo_estudiante_id`
- `idx_estudiante_grupo_estudiante_grupo`

---

## FAQBot

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| faq_id | uuid | NO | gen_random_uuid() | ✅ |
| pregunta | text | NO | - |  |
| respuesta | text | NO | - |  |
| categoria | character varying(50) | NO | - |  |
| ultima_actualizacion | timestamp without time zone | YES | - |  |

---

## Grupo

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| grupo_id | uuid | NO | gen_random_uuid() | ✅ |
| programa_id | uuid | NO | - |  |
| docente_tutor_id | uuid | YES | - |  |
| nombre | character varying(50) | NO | - |  |
| jornada | USER-DEFINED | NO | 'manana'::jornada_grupo |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| docente_tutor_id | Docente.docente_id | Docente |
| programa_id | Programa.programa_id | Programa |

### Índices

- `Grupo_docente_tutor_id_key`

---

## GrupoCurso

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| grupo_curso_id | uuid | NO | gen_random_uuid() | ✅ |
| grupo_id | uuid | NO | - |  |
| curso_id | uuid | NO | - |  |
| docente_id | uuid | NO | - |  |
| fecha_asignacion | date | YES | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| curso_id | Curso.curso_id | Curso |
| docente_id | Docente.docente_id | Docente |
| grupo_id | Grupo.grupo_id | Grupo |

### Índices

- `idx_grupo_curso_curso_id`
- `idx_grupo_curso_docente_id`
- `uq_grupo_curso`

---

## HistorialPuntos

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| historial_id | uuid | NO | gen_random_uuid() | ✅ |
| usuario_id | uuid | YES | - |  |
| cambio | integer | NO | - |  |
| motivo | text | YES | - |  |
| fecha | timestamp with time zone | NO | now() |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| usuario_id | Usuario.usuario_id | Usuario |

---

## Insignia

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| insignia_id | uuid | NO | gen_random_uuid() | ✅ |
| nombre | character varying(100) | NO | - |  |
| descripcion | text | YES | - |  |
| imagen_url | text | YES | - |  |
| tipo | USER-DEFINED | NO | 'manual'::tipo_insignia |  |
| es_unica | boolean | NO | - |  |

### Índices

- `Insignia_nombre_key`

---

## Institucion

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| institucion_id | uuid | NO | gen_random_uuid() | ✅ |
| administrador_id_creador | uuid | YES | - |  |
| nombre | character varying(150) | NO | - |  |
| sigla | character varying(20) | YES | - |  |
| lema | character varying(255) | YES | - |  |
| tipo_institucion | USER-DEFINED | NO | - |  |
| usa_programas | boolean | NO | - |  |
| nivel_educativo | USER-DEFINED | NO | - |  |
| sector | USER-DEFINED | NO | - |  |
| direccion | character varying(255) | YES | - |  |
| ciudad | character varying(100) | YES | - |  |
| pais | character varying(100) | NO | - |  |
| correo_institucional | character varying(100) | NO | - |  |
| telefono | character varying(30) | NO | - |  |
| nit | character varying(20) | YES | - |  |
| estado | USER-DEFINED | NO | 'pendiente'::estado_institucion |  |
| fecha_creacion | timestamp with time zone | YES | now() |  |
| fecha_activacion | timestamp with time zone | YES | - |  |
| dominio | character varying(255) | YES | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| administrador_id_creador | Usuario.usuario_id | Usuario |

### Índices

- `idx_institucion_dominio`
- `Institucion_correo_institucional_key`
- `Institucion_nit_key`
- `Institucion_nombre_key`
- `Institucion_sigla_key`

---

## InstitucionCoordinador

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| institucion_id | uuid | NO | - | ✅ |
| coordinador_id | uuid | NO | - | ✅ |
| fecha_asignacion | date | NO | - |  |
| estado | USER-DEFINED | NO | 'activo'::estado_coordinador |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| coordinador_id | Coordinador.coordinador_id | Coordinador |
| institucion_id | Institucion.institucion_id | Institucion |

---

## MaterialClase

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| material_clase_id | uuid | NO | - | ✅ |
| clase_id | uuid | YES | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| clase_id | Clase.clase_id | Clase |
| material_clase_id | MaterialEducativo.material_id | MaterialEducativo |

### Índices

- `idx_material_clase_clase_id`

---

## MaterialCurso

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| material_curso_id | uuid | NO | - | ✅ |
| curso_id | uuid | NO | - | ✅ |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| curso_id | Curso.curso_id | Curso |
| material_curso_id | MaterialEducativo.material_id | MaterialEducativo |

### Índices

- `idx_material_curso_curso_id`

---

## MaterialEducativo

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| material_id | uuid | NO | gen_random_uuid() | ✅ |
| titulo | character varying(100) | NO | - |  |
| descripcion | text | YES | - |  |
| tipo_material | USER-DEFINED | NO | - |  |
| url_archivo | character varying(255) | NO | - |  |
| formato_archivo | character varying(10) | NO | - |  |

---

## OAuthProvider

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| oauth_provider_id | uuid | NO | gen_random_uuid() | ✅ |
| usuario_id | uuid | NO | - |  |
| provider | character varying(50) | NO | - |  |
| provider_user_id | character varying(255) | NO | - |  |
| provider_email | character varying(255) | NO | - |  |
| fecha_vinculacion | timestamp with time zone | NO | now() |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| usuario_id | Usuario.usuario_id | Usuario |

### Índices

- `uq_provider_user`

---

## Plataforma

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| plataforma_id | uuid | NO | gen_random_uuid() | ✅ |
| nombre | character varying(50) | NO | - |  |
| url_base | text | NO | - |  |
| tipo_integracion | USER-DEFINED | NO | - |  |
| requiere_cuenta | boolean | NO | - |  |
| es_gratuita | boolean | YES | - |  |

### Índices

- `Plataforma_nombre_key`

---

## Programa

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| programa_id | uuid | NO | gen_random_uuid() | ✅ |
| institucion_id | uuid | NO | - |  |
| nombre | character varying(100) | NO | - |  |
| descripcion | text | YES | - |  |
| nivel | USER-DEFINED | NO | - |  |
| tipo | USER-DEFINED | NO | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| institucion_id | Institucion.institucion_id | Institucion |

### Índices

- `uq_programa_nombre`

---

## Reacciones

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| reaccion_id | uuid | NO | - | ✅ |
| comentario_id | uuid | NO | - |  |
| usuario_id | uuid | NO | - |  |
| emoji | character varying(10) | NO | - |  |
| tipo | character varying(20) | YES | - |  |
| fecha_creacion | timestamp without time zone | NO | CURRENT_TIMESTAMP |  |
| activo | boolean | NO | true |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| comentario_id | Comentario.comentario_id | Comentario |
| usuario_id | Usuario.usuario_id | Usuario |

### Índices

- `idx_reacciones_comentario_usuario`
- `uq_user_emoji_per_comment`
- `idx_reacciones_comentario_id`
- `idx_reacciones_usuario_id`
- `idx_reacciones_emoji`
- `idx_reacciones_activo`

---

## Recompensa

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| recompensa_id | uuid | NO | gen_random_uuid() | ✅ |
| nombre | character varying(100) | NO | - |  |
| descripcion | text | YES | - |  |
| costo_puntos | integer | NO | - |  |
| tipo | USER-DEFINED | NO | 'otro'::tipo_recompensa_enum |  |

---

## Tema

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| tema_id | uuid | NO | gen_random_uuid() | ✅ |
| nombre | character varying(100) | NO | - |  |
| emoji | character varying(8) | NO | - |  |

---

## TemaPersonalizado

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| tema_id | uuid | NO | - | ✅ |
| usuario_id | uuid | YES | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| tema_id | Tema.tema_id | Tema |
| usuario_id | Usuario.usuario_id | Usuario |

### Índices

- `uq_nombre_predefinido`

---

## TemaPredefinido

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| tema_id | uuid | NO | - | ✅ |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| tema_id | Tema.tema_id | Tema |

### Índices

- `TemaPredefinido_tema_id_key`

---

## Usuario

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| usuario_id | uuid | NO | gen_random_uuid() | ✅ |
| correo_institucional | character varying(100) | YES | - |  |
| username | character varying(50) | YES | - |  |
| nombres | character varying(100) | NO | - |  |
| apellidos | character varying(100) | NO | - |  |
| tipo_documento | USER-DEFINED | NO | - |  |
| numero_documento | character varying(20) | NO | - |  |
| rol | USER-DEFINED | NO | - |  |
| password_hash | character varying(255) | NO | - |  |
| estado_cuenta | USER-DEFINED | NO | 'activo'::estado_cuenta_usuario |  |
| fecha_creacion | timestamp with time zone | YES | now() |  |
| ultimo_acceso | timestamp with time zone | YES | now() |  |
| perfil_url | text | YES | - |  |
| portada_url | text | YES | - |  |
| telefono | character varying(20) | YES | - |  |
| descripcion | text | YES | - |  |
| email_verified | boolean | NO | false |  |
| failed_login_attempts | smallint | NO | 0 |  |
| locked_until | timestamp with time zone | YES | - |  |
| twofa_enabled | boolean | NO | false |  |
| twofa_secret | character varying(32) | YES | - |  |

### Índices

- `idx_usuario_rol`
- `idx_usuario_estado_cuenta`
- `idx_usuario_rol_estado`
- `idx_usuario_nombres_busqueda`
- `ix_Usuario_correo_institucional`
- `ix_Usuario_numero_documento`
- `ix_Usuario_username`
- `ix_Usuario_usuario_id`

---

## UsuarioInsignia

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| usuario_id | uuid | NO | - | ✅ |
| insignia_id | uuid | NO | - | ✅ |
| otorgada_por | uuid | YES | - |  |
| fecha_otorgada | timestamp with time zone | NO | now() |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| insignia_id | Insignia.insignia_id | Insignia |
| otorgada_por | Usuario.usuario_id | Usuario |
| usuario_id | Usuario.usuario_id | Usuario |

### Índices

- `idx_insignias_usuario_usuario_id`

---

## UsuarioPuntos

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| usuario_id | uuid | NO | - | ✅ |
| puntos_acumulados | integer | NO | 0 |  |
| cambio | integer | NO | - |  |
| motivo | text | YES | - |  |
| fecha | timestamp with time zone | NO | now() |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| usuario_id | Usuario.usuario_id | Usuario |

### Índices

- `idx_usuario_puntos_usuario_id`

---

## UsuarioRecompensa

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| usuario_recompensa_id | uuid | NO | - | ✅ |
| usuario_id | uuid | YES | - |  |
| recompensa_id | uuid | YES | - |  |
| fecha_canje | timestamp with time zone | YES | now() |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| recompensa_id | Recompensa.recompensa_id | Recompensa |
| usuario_id | Usuario.usuario_id | Usuario |

---

## ValorCalificacion

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| valor_id | uuid | NO | gen_random_uuid() | ✅ |
| escala_id | uuid | NO | - |  |
| valor | character varying(10) | NO | - |  |
| descripcion | character varying(100) | YES | - |  |
| orden | smallint | YES | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| escala_id | EscalaCalificacion.escala_id | EscalaCalificacion |

---

## avatar_asset

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| id | uuid | NO | gen_random_uuid() | ✅ |
| category | character varying(50) | NO | - |  |
| filename | character varying(255) | NO | - |  |
| display_name | character varying(100) | YES | - |  |
| file_size | integer | NO | - |  |
| width | integer | NO | - |  |
| height | integer | NO | - |  |
| meta_info | json | YES | - |  |
| is_active | character varying(1) | NO | 'Y'::character varying |  |
| created_at | timestamp with time zone | NO | now() |  |
| updated_at | timestamp with time zone | NO | now() |  |
| target_gender | character varying(20) | NO | 'unisex'::character varying |  |

### Índices

- `avatar_asset_filename_key`
- `ix_avatar_asset_id`
- `ix_avatar_asset_category`
- `ix_avatar_asset_target_gender`

---

## banco_preguntas

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| pregunta_id | character varying | NO | - | ✅ |
| titulo | text | NO | - |  |
| descripcion | text | YES | - |  |
| tipo_pregunta | character varying(50) | NO | - |  |
| dificultad | character varying(50) | YES | 'medio'::character varying |  |
| materia | character varying(100) | YES | - |  |
| tema | character varying(200) | YES | - |  |
| subtema | character varying(200) | YES | - |  |
| opciones_respuesta | json | YES | - |  |
| respuesta_correcta | json | YES | - |  |
| explicacion | text | YES | - |  |
| imagen_url | character varying(500) | YES | - |  |
| audio_url | character varying(500) | YES | - |  |
| video_url | character varying(500) | YES | - |  |
| archivos_adjuntos | json | YES | - |  |
| creado_por | character varying | NO | - |  |
| institucion_id | character varying | YES | - |  |
| es_publica | boolean | YES | false |  |
| tags | json | YES | - |  |
| categoria | character varying(100) | YES | - |  |
| nivel_educativo | character varying(50) | YES | - |  |
| puntuacion_sugerida | double precision | YES | '1'::double precision |  |
| tiempo_estimado_segundos | integer | YES | - |  |
| veces_utilizada | integer | YES | 0 |  |
| promedio_aciertos | double precision | YES | - |  |
| calificacion_dificultad | double precision | YES | - |  |
| fecha_creacion | timestamp with time zone | YES | now() |  |
| fecha_actualizacion | timestamp with time zone | YES | - |  |
| ultima_vez_utilizada | timestamp with time zone | YES | - |  |
| revisado_por | character varying | YES | - |  |
| fecha_revision | timestamp with time zone | YES | - |  |
| estado_revision | character varying(50) | YES | 'pendiente'::character varying |  |
| comentarios_revision | text | YES | - |  |

---

## configuracion_evaluaciones

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| config_id | character varying | NO | - | ✅ |
| tiempo_gracia_segundos | integer | YES | 300 |  |
| maximo_intentos_globales | integer | YES | 5 |  |
| tiempo_minimo_entre_intentos | integer | YES | 3600 |  |
| max_cambios_pestana_permitidos | integer | YES | 5 |  |
| tiempo_max_inactividad_global | integer | YES | 1800 |  |
| habilitar_deteccion_copia_texto | boolean | YES | true |  |
| habilitar_deteccion_pantalla_completa | boolean | YES | true |  |
| algoritmo_calificacion_ensayos | character varying(100) | YES | 'keyword_matching'::character varying |  |
| umbral_similitud_plagio | double precision | YES | '0.8'::double precision |  |
| habilitar_feedback_automatico | boolean | YES | true |  |
| notificar_intento_finalizado | boolean | YES | true |  |
| notificar_resultado_disponible | boolean | YES | true |  |
| notificar_tiempo_restante | boolean | YES | true |  |
| tiempo_notificacion_previa_minutos | integer | YES | 10 |  |
| guardar_progreso_cada_segundos | integer | YES | 30 |  |
| habilitar_recuperacion_sesion | boolean | YES | true |  |
| tiempo_expiracion_backup_horas | integer | YES | 72 |  |
| institucion_id | character varying | YES | - |  |
| aplicar_globalmente | boolean | YES | true |  |
| creado_por | character varying | NO | - |  |
| fecha_creacion | timestamp with time zone | YES | now() |  |
| fecha_actualizacion | timestamp with time zone | YES | - |  |

---

## entregas_tareas

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| entrega_id | character varying | NO | - | ✅ |
| tarea_id | character varying | NO | - |  |
| estudiante_id | uuid | NO | - |  |
| titulo_entrega | character varying(200) | YES | - |  |
| descripcion_entrega | text | YES | - |  |
| comentarios_estudiante | text | YES | - |  |
| archivo_url | character varying(500) | YES | - |  |
| archivos_adicionales | json | YES | - |  |
| contenido_texto | text | YES | - |  |
| enlaces_externos | json | YES | - |  |
| fecha_entrega | timestamp with time zone | YES | - |  |
| fecha_limite_original | timestamp with time zone | YES | - |  |
| numero_intento | integer | YES | - |  |
| es_entrega_tardia | boolean | YES | - |  |
| calificacion | double precision | YES | - |  |
| calificacion_letras | character varying(5) | YES | - |  |
| comentarios_docente | text | YES | - |  |
| rubrica_calificacion | json | YES | - |  |
| estado | character varying(50) | YES | - |  |
| es_final | boolean | YES | - |  |
| requiere_revision | boolean | YES | - |  |
| tiempo_empleado | integer | YES | - |  |
| dificultad_percibida | integer | YES | - |  |
| satisfaccion_estudiante | integer | YES | - |  |
| fecha_creacion | timestamp with time zone | YES | now() |  |
| fecha_actualizacion | timestamp with time zone | YES | - |  |
| calificado_por | uuid | YES | - |  |
| fecha_calificacion | timestamp with time zone | YES | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| calificado_por | Usuario.usuario_id | Usuario |
| estudiante_id | Usuario.usuario_id | Usuario |
| tarea_id | tareas.tarea_id | tareas |

### Índices

- `idx_entregas_tarea_id`
- `idx_entregas_estudiante_id`
- `idx_entregas_estado`

---

## estadisticas_examen

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| estadistica_id | character varying | NO | - | ✅ |
| examen_id | character varying | NO | - |  |
| total_estudiantes_asignados | integer | YES | 0 |  |
| total_intentos_realizados | integer | YES | 0 |  |
| total_intentos_finalizados | integer | YES | 0 |  |
| total_aprobados | integer | YES | 0 |  |
| total_reprobados | integer | YES | 0 |  |
| puntuacion_promedio | double precision | YES | '0'::double precision |  |
| puntuacion_mediana | double precision | YES | '0'::double precision |  |
| puntuacion_maxima_obtenida | double precision | YES | '0'::double precision |  |
| puntuacion_minima_obtenida | double precision | YES | '0'::double precision |  |
| desviacion_estandar | double precision | YES | '0'::double precision |  |
| tiempo_promedio_minutos | double precision | YES | '0'::double precision |  |
| tiempo_maximo_empleado | integer | YES | 0 |  |
| tiempo_minimo_empleado | integer | YES | 0 |  |
| estadisticas_preguntas | json | YES | - |  |
| preguntas_mas_dificiles | json | YES | - |  |
| preguntas_mas_faciles | json | YES | - |  |
| patrones_abandono | json | YES | - |  |
| tiempo_por_pregunta | json | YES | - |  |
| fecha_calculo | timestamp with time zone | YES | now() |  |
| fecha_ultima_actualizacion | timestamp with time zone | YES | - |  |
| incluir_intentos_incompletos | boolean | YES | false |  |
| periodo_calculo | character varying(50) | YES | 'completo'::character varying |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| examen_id | examenes.examen_id | examenes |

---

## eventos_anti_trampa

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| evento_id | character varying | NO | - | ✅ |
| intento_id | character varying | NO | - |  |
| tipo_evento | character varying(50) | NO | - |  |
| descripcion | text | YES | - |  |
| datos_evento | json | YES | - |  |
| ip_address | character varying(45) | YES | - |  |
| user_agent | text | YES | - |  |
| timestamp | timestamp with time zone | YES | now() |  |
| es_sospechoso | boolean | YES | false |  |
| nivel_riesgo | character varying(20) | YES | 'bajo'::character varying |  |
| requiere_revision | boolean | YES | false |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| intento_id | intentos_examen.intento_id | intentos_examen |

---

## examenes

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| examen_id | character varying | NO | - | ✅ |
| titulo | character varying(200) | NO | - |  |
| descripcion | text | YES | - |  |
| tipo_examen | character varying(50) | NO | 'evaluacion'::character varying |  |
| estado_examen | character varying(50) | NO | 'borrador'::character varying |  |
| tiempo_limite | integer | NO | 60 |  |
| fecha_inicio | timestamp with time zone | YES | - |  |
| fecha_limite | timestamp with time zone | YES | - |  |
| intentos_permitidos | integer | YES | 1 |  |
| requiere_contraseña | boolean | YES | false |  |
| contraseña_acceso | character varying(100) | YES | - |  |
| randomizar_preguntas | boolean | YES | false |  |
| mostrar_resultados_inmediatos | boolean | YES | true |  |
| permitir_revision | boolean | YES | true |  |
| mostrar_respuestas_correctas | boolean | YES | true |  |
| modo_pantalla_completa | boolean | YES | false |  |
| bloquear_navegacion | boolean | YES | false |  |
| detectar_cambio_pestana | boolean | YES | false |  |
| tiempo_maximo_inactividad | integer | YES | 300 |  |
| puntuacion_total | double precision | NO | '100'::double precision |  |
| puntuacion_minima_aprobacion | double precision | YES | '60'::double precision |  |
| calificacion_automatica | boolean | YES | true |  |
| curso_id | character varying | YES | - |  |
| grupo_id | character varying | YES | - |  |
| creado_por | character varying | NO | - |  |
| fecha_creacion | timestamp with time zone | YES | now() |  |
| fecha_actualizacion | timestamp with time zone | YES | - |  |
| configuracion_avanzada | json | YES | - |  |
| instrucciones | text | YES | - |  |
| total_preguntas | integer | YES | 0 |  |
| total_intentos | integer | YES | 0 |  |
| promedio_calificacion | double precision | YES | - |  |

---

## intentos_examen

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| intento_id | character varying | NO | - | ✅ |
| examen_id | character varying | NO | - |  |
| estudiante_id | character varying | NO | - |  |
| numero_intento | integer | NO | - |  |
| estado_intento | character varying(50) | NO | 'en_progreso'::character varying |  |
| fecha_inicio | timestamp with time zone | YES | now() |  |
| fecha_fin | timestamp with time zone | YES | - |  |
| tiempo_total_segundos | integer | YES | - |  |
| tiempo_limite_vencido | boolean | YES | false |  |
| puntuacion_obtenida | double precision | YES | '0'::double precision |  |
| puntuacion_maxima | double precision | NO | - |  |
| porcentaje | double precision | YES | - |  |
| aprobado | boolean | YES | - |  |
| preguntas_respondidas | integer | YES | 0 |  |
| total_preguntas | integer | NO | - |  |
| pregunta_actual | integer | YES | 1 |  |
| cambios_pestana_detectados | integer | YES | 0 |  |
| tiempo_inactividad_total | integer | YES | 0 |  |
| ip_address | character varying(45) | YES | - |  |
| user_agent | text | YES | - |  |
| eventos_sospechosos | json | YES | - |  |
| orden_preguntas | json | YES | - |  |
| configuracion_intento | json | YES | - |  |
| finalizado_por | character varying(50) | YES | 'estudiante'::character varying |  |
| comentarios_finalizacion | text | YES | - |  |
| fecha_revision | timestamp with time zone | YES | - |  |
| revisado_por | character varying | YES | - |  |
| comentarios_profesor | text | YES | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| examen_id | examenes.examen_id | examenes |

---

## mensajes

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| id | uuid | NO | - | ✅ |
| sala_id | uuid | NO | - |  |
| usuario_id | uuid | NO | - |  |
| contenido | text | YES | - |  |
| contenido_html | text | YES | - |  |
| tipo_mensaje | character varying(50) | YES | - |  |
| archivos_urls | json | YES | - |  |
| metadatos_archivos | json | YES | - |  |
| mensaje_padre_id | uuid | YES | - |  |
| tiene_respuestas | boolean | YES | - |  |
| numero_respuestas | integer | YES | - |  |
| menciones_usuarios | json | YES | - |  |
| menciones_ia | boolean | YES | - |  |
| menciones_todos | boolean | YES | - |  |
| estado | character varying(50) | YES | - |  |
| fecha_creacion | timestamp without time zone | YES | now() |  |
| fecha_actualizacion | timestamp without time zone | YES | - |  |
| fecha_eliminacion | timestamp without time zone | YES | - |  |
| reacciones | json | YES | - |  |
| es_importante | boolean | YES | - |  |
| es_anuncio | boolean | YES | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| sala_id | salas_chat.id | salas_chat |
| mensaje_padre_id | mensajes.id | mensajes |

---

## notificaciones

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| id | uuid | NO | - | ✅ |
| usuario_id | uuid | NO | - |  |
| titulo | character varying(255) | NO | - |  |
| mensaje | text | YES | - |  |
| tipo_notificacion | character varying(50) | YES | - |  |
| sala_id | uuid | YES | - |  |
| mensaje_id | uuid | YES | - |  |
| tarea_id | uuid | YES | - |  |
| curso_id | uuid | YES | - |  |
| leida | boolean | YES | - |  |
| enviada_email | boolean | YES | - |  |
| enviada_push | boolean | YES | - |  |
| fecha_creacion | timestamp without time zone | YES | now() |  |
| fecha_lectura | timestamp without time zone | YES | - |  |
| fecha_envio_email | timestamp without time zone | YES | - |  |
| datos_adicionales | json | YES | - |  |
| url_accion | character varying(500) | YES | - |  |
| icono | character varying(100) | YES | - |  |
| color | character varying(7) | YES | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| sala_id | salas_chat.id | salas_chat |
| mensaje_id | mensajes.id | mensajes |

### Índices

- `idx_notificaciones_usuario_id`
- `idx_notificaciones_leida`
- `idx_notificaciones_usuario_leida_fecha`
- `idx_notificaciones_tipo`

---

## preguntas_examen

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| pregunta_id | character varying | NO | - | ✅ |
| examen_id | character varying | NO | - |  |
| titulo | text | NO | - |  |
| descripcion | text | YES | - |  |
| tipo_pregunta | character varying(50) | NO | - |  |
| orden | integer | NO | - |  |
| puntuacion | double precision | NO | '1'::double precision |  |
| es_obligatoria | boolean | YES | true |  |
| tiempo_limite_segundos | integer | YES | - |  |
| opciones_respuesta | json | YES | - |  |
| respuesta_correcta | json | YES | - |  |
| explicacion | text | YES | - |  |
| puntos_respuesta_parcial | boolean | YES | false |  |
| dificultad | character varying(50) | YES | 'medio'::character varying |  |
| imagen_url | character varying(500) | YES | - |  |
| audio_url | character varying(500) | YES | - |  |
| video_url | character varying(500) | YES | - |  |
| archivos_adjuntos | json | YES | - |  |
| banco_pregunta_id | character varying | YES | - |  |
| tags | json | YES | - |  |
| fecha_creacion | timestamp with time zone | YES | now() |  |
| fecha_actualizacion | timestamp with time zone | YES | - |  |
| veces_utilizada | integer | YES | 0 |  |
| promedio_aciertos | double precision | YES | - |  |
| tiempo_promedio_respuesta | double precision | YES | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| examen_id | examenes.examen_id | examenes |
| banco_pregunta_id | banco_preguntas.pregunta_id | banco_preguntas |

---

## respuestas_estudiante

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| respuesta_id | character varying | NO | - | ✅ |
| intento_id | character varying | NO | - |  |
| pregunta_id | character varying | NO | - |  |
| respuesta_estudiante | json | YES | - |  |
| texto_respuesta | text | YES | - |  |
| puntuacion_obtenida | double precision | YES | '0'::double precision |  |
| puntuacion_maxima | double precision | NO | - |  |
| es_correcta | boolean | YES | - |  |
| calificada_automaticamente | boolean | YES | false |  |
| fecha_respuesta | timestamp with time zone | YES | now() |  |
| tiempo_empleado_segundos | integer | YES | - |  |
| fecha_ultima_modificacion | timestamp with time zone | YES | - |  |
| historial_respuestas | json | YES | - |  |
| numero_modificaciones | integer | YES | 0 |  |
| feedback_automatico | text | YES | - |  |
| feedback_profesor | text | YES | - |  |
| mostrar_respuesta_correcta | boolean | YES | false |  |
| palabras_clave_encontradas | json | YES | - |  |
| similitud_respuesta_correcta | double precision | YES | - |  |
| version_pregunta | character varying(50) | YES | - |  |
| metadata_respuesta | json | YES | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| intento_id | intentos_examen.intento_id | intentos_examen |
| pregunta_id | preguntas_examen.pregunta_id | preguntas_examen |

---

## rubricas

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| rubrica_id | character varying | NO | - | ✅ |
| nombre | character varying(200) | NO | - |  |
| descripcion | text | YES | - |  |
| criterios | json | NO | - |  |
| puntuacion_total | double precision | NO | - |  |
| es_publica | boolean | YES | - |  |
| es_plantilla | boolean | YES | - |  |
| activa | boolean | YES | - |  |
| fecha_creacion | timestamp with time zone | YES | now() |  |
| fecha_actualizacion | timestamp with time zone | YES | - |  |
| creado_por | character varying | NO | - |  |

---

## salas_chat

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| id | uuid | NO | - | ✅ |
| nombre | character varying(255) | NO | - |  |
| descripcion | text | YES | - |  |
| tipo_sala | character varying(50) | NO | - |  |
| curso_id | uuid | YES | - |  |
| grupo_id | uuid | YES | - |  |
| tarea_id | uuid | YES | - |  |
| es_publica | boolean | YES | - |  |
| permite_archivos | boolean | YES | - |  |
| permite_menciones | boolean | YES | - |  |
| permite_hilos | boolean | YES | - |  |
| moderacion_activa | boolean | YES | - |  |
| creador_id | uuid | NO | - |  |
| fecha_creacion | timestamp without time zone | YES | now() |  |
| fecha_actualizacion | timestamp without time zone | YES | - |  |
| ultimo_mensaje_fecha | timestamp without time zone | YES | - |  |
| configuracion_json | json | YES | - |  |
| tags | character varying(500) | YES | - |  |

---

## tareas

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| tarea_id | character varying | NO | - | ✅ |
| docente_id | uuid | NO | - |  |
| titulo | character varying(200) | NO | - |  |
| descripcion | text | YES | - |  |
| instrucciones | text | YES | - |  |
| objetivos | text | YES | - |  |
| tipo_tarea | USER-DEFINED | NO | 'ensayo'::tipo_tarea |  |
| prioridad | USER-DEFINED | NO | 'media'::prioridad_tarea |  |
| grupo_id | uuid | NO | - |  |
| tags | character varying(500) | YES | - |  |
| fecha_asignacion | timestamp with time zone | YES | now() |  |
| fecha_limite | timestamp with time zone | NO | - |  |
| fecha_inicio_disponible | timestamp with time zone | YES | - |  |
| tiempo_estimado | integer | YES | - |  |
| permite_entrega_tardia | boolean | YES | - |  |
| penalizacion_tardia | double precision | YES | - |  |
| intentos_maximos | integer | YES | - |  |
| formato_entrega | character varying(200) | YES | - |  |
| tamano_maximo_mb | double precision | YES | - |  |
| puntuacion_maxima | double precision | NO | - |  |
| peso_evaluacion | double precision | YES | - |  |
| rubrica_id | character varying | YES | - |  |
| estado | USER-DEFINED | NO | 'asignada'::estado_tarea |  |
| es_grupal | boolean | YES | - |  |
| es_publica | boolean | YES | - |  |
| requiere_aprobacion | boolean | YES | - |  |
| configuracion_json | json | YES | - |  |
| recursos_necesarios | text | YES | - |  |
| criterios_evaluacion | text | YES | - |  |
| activa | boolean | YES | - |  |
| fecha_creacion | timestamp with time zone | YES | now() |  |
| fecha_actualizacion | timestamp with time zone | YES | - |  |
| creado_por | uuid | YES | - |  |
| actualizado_por | uuid | YES | - |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| creado_por | Usuario.usuario_id | Usuario |
| actualizado_por | Usuario.usuario_id | Usuario |
| docente_id | Usuario.usuario_id | Usuario |
| grupo_id | Grupo.grupo_id | Grupo |
| rubrica_id | rubricas.rubrica_id | rubricas |

### Índices

- `idx_tareas_grupo_id`
- `idx_tareas_docente_id`
- `idx_tareas_fecha_limite`
- `idx_tareas_estado`

---

## user_avatar

### Columnas

| Columna | Tipo | Nullable | Default | PK |
|---------|------|----------|---------|-----|
| id | uuid | NO | gen_random_uuid() | ✅ |
| user_id | uuid | NO | - |  |
| name | character varying(100) | NO | - |  |
| layers | json | NO | - |  |
| image_url | character varying(500) | NO | - |  |
| layers_hash | character varying(64) | NO | - |  |
| is_active | boolean | NO | false |  |
| is_public | boolean | NO | true |  |
| created_at | timestamp with time zone | NO | now() |  |
| updated_at | timestamp with time zone | NO | now() |  |
| base_gender | character varying(20) | NO | 'male'::character varying |  |

### Relaciones (Foreign Keys)

| Columna | Referencia | Tabla Relacionada |
|---------|-----------|-------------------|
| user_id | Usuario.usuario_id | Usuario |

### Índices

- `ix_user_avatar_id`
- `ix_user_avatar_user_id`
- `ix_user_avatar_layers_hash`

---
