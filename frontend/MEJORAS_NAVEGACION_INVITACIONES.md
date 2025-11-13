# Mejoras de Navegación y Sistema de Invitaciones

## Cambios Realizados

### 1. Limpieza de Navegación Principal (`config/navigation.ts`)

**Problema**: La navegación estaba sobrecargada con más de 50 elementos, creando una interfaz confusa.

**Solución**:
- **Admin**: Reducido a 4 elementos principales:
  - Instituciones
  - Usuarios Pendientes
  - Tienda
  - Configuración
  - ❌ Eliminado: Logros, Reportes (movidos a otras secciones o eliminados)

- **Coordinador**: Simplificado a 2 elementos esenciales:
  - Mi Institución
  - Aprobar Código (para aceptar invitaciones)
  - ❌ Eliminado: Panel Coordinador, Aprobar Usuarios, Asignación de Cursos, Seguimiento Académico

**Impacto**: Navegación más limpia y enfocada en las funciones principales de cada rol.

---

### 2. Página de Aceptación de Invitaciones

**Archivo**: `/pages/invitaciones/AceptarInvitacionPage.tsx`

**Características**:
- 🎯 Formulario simple con input para código de invitación
- ✅ Validación en tiempo real
- 🔄 Estados de carga, éxito y error
- 🎨 Diseño moderno con Framer Motion
- 🌙 Soporte para tema oscuro
- ↪️ Redirección automática al panel después de aceptar

**Endpoint Backend Esperado**:
```typescript
POST /api/invitaciones/aceptar/
Body: { codigo: string }
Headers: { Authorization: Bearer <token> }
```

**Respuesta Esperada**:
```typescript
{
  message: "Invitación aceptada exitosamente",
  institucion: {
    id: number,
    nombre: string,
    tipo: string
  }
}
```

---

### 3. Panel de Institución del Coordinador

**Archivo**: `/pages/coordinador/CoordinadorInstitucionPage.tsx`

**Características**:
- 🏢 Muestra información de la institución asignada
- 📊 Estadísticas en tiempo real:
  - Total de estudiantes
  - Total de profesores
  - Total de cursos
  - Usuarios pendientes de aprobación
- ⚡ Acciones rápidas:
  - Aprobar usuarios
  - Gestionar cursos
  - Comunicación
- 🔔 Manejo de estados:
  - Sin institución asignada → Redirige a aceptar invitación
  - Institución pendiente → Muestra badge amarillo
  - Institución activa → Muestra badge verde

**Endpoints Backend Requeridos**:

```typescript
// Obtener institución del coordinador
GET /api/coordinador/mi-institucion/
Headers: { Authorization: Bearer <token> }

Response: {
  id: number,
  nombre: string,
  tipo: string,
  ubicacion?: string,
  estado: 'activa' | 'pendiente' | 'inactiva',
  created_at: string
}

// Obtener estadísticas
GET /api/coordinador/institucion/{id}/estadisticas/
Headers: { Authorization: Bearer <token> }

Response: {
  total_estudiantes: number,
  total_profesores: number,
  total_cursos: number,
  usuarios_pendientes: number
}
```

---

### 4. Rutas Agregadas (`App.tsx`)

```typescript
// Aceptar invitación con código (requiere autenticación)
<Route path="/invitaciones/aceptar" element={<AceptarInvitacionPage />} />

// Panel de institución del coordinador
<Route path="/coordinador/institucion" element={<CoordinadorInstitucionPage />} />
```

---

## Flujo de Trabajo Completo

### Para el Administrador:
1. ✅ Crear institución en `/admin/instituciones`
2. ✅ Enviar invitación a coordinador (funcional)
3. ✅ Monitorear estado en panel de instituciones

### Para el Coordinador:
1. 📧 Recibir email con código de invitación
2. 🔑 Ir a "Aprobar Código" en la navegación → `/invitaciones/aceptar`
3. ✏️ Ingresar código de invitación
4. ✅ Sistema valida y asocia coordinador a institución
5. 🏢 Redirección automática a "Mi Institución" → `/coordinador/institucion`
6. 📊 Ver estadísticas y gestionar institución

---

## Endpoints Backend Pendientes

Para que el sistema funcione completamente, el backend necesita implementar:

### 1. Aceptar Invitación con Código
```python
@router.post("/invitaciones/aceptar/")
async def aceptar_invitacion(
    datos: AceptarInvitacionSchema,  # { codigo: str }
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Buscar invitación por código
    invitacion = db.query(InvitacionCoordinador)\
        .filter(InvitacionCoordinador.codigo == datos.codigo)\
        .filter(InvitacionCoordinador.estado == "pendiente")\
        .first()
    
    if not invitacion:
        raise HTTPException(404, "Código inválido o ya utilizado")
    
    # 2. Verificar que el email coincida
    if invitacion.email_destino != current_user.email:
        raise HTTPException(403, "Este código no fue enviado a tu email")
    
    # 3. Asignar coordinador a institución
    current_user.rol = "coordinador"
    current_user.institucion_id = invitacion.institucion_id
    
    # 4. Actualizar invitación
    invitacion.estado = "aceptada"
    invitacion.fecha_aceptacion = datetime.now()
    
    # 5. Actualizar institución a activa
    institucion = db.query(Institucion).get(invitacion.institucion_id)
    institucion.estado = "activa"
    
    db.commit()
    
    return {
        "message": "Invitación aceptada exitosamente",
        "institucion": {
            "id": institucion.id,
            "nombre": institucion.nombre,
            "tipo": institucion.tipo
        }
    }
```

### 2. Obtener Institución del Coordinador
```python
@router.get("/coordinador/mi-institucion/")
async def obtener_mi_institucion(
    current_user: Usuario = Depends(get_current_coordinador),
    db: Session = Depends(get_db)
):
    if not current_user.institucion_id:
        raise HTTPException(404, "No tienes una institución asignada")
    
    institucion = db.query(Institucion).get(current_user.institucion_id)
    
    return {
        "id": institucion.id,
        "nombre": institucion.nombre,
        "tipo": institucion.tipo,
        "ubicacion": institucion.ubicacion,
        "estado": institucion.estado,
        "created_at": institucion.created_at.isoformat()
    }
```

### 3. Obtener Estadísticas de Institución
```python
@router.get("/coordinador/institucion/{institucion_id}/estadisticas/")
async def obtener_estadisticas(
    institucion_id: int,
    current_user: Usuario = Depends(get_current_coordinador),
    db: Session = Depends(get_db)
):
    # Verificar que el coordinador pertenece a esta institución
    if current_user.institucion_id != institucion_id:
        raise HTTPException(403, "No tienes acceso a esta institución")
    
    total_estudiantes = db.query(Usuario)\
        .filter(Usuario.institucion_id == institucion_id)\
        .filter(Usuario.rol == "estudiante")\
        .count()
    
    total_profesores = db.query(Usuario)\
        .filter(Usuario.institucion_id == institucion_id)\
        .filter(Usuario.rol.in_(["profesor", "docente"]))\
        .count()
    
    total_cursos = db.query(Curso)\
        .filter(Curso.institucion_id == institucion_id)\
        .count()
    
    usuarios_pendientes = db.query(Usuario)\
        .filter(Usuario.institucion_id == institucion_id)\
        .filter(Usuario.estado == "pendiente")\
        .count()
    
    return {
        "total_estudiantes": total_estudiantes,
        "total_profesores": total_profesores,
        "total_cursos": total_cursos,
        "usuarios_pendientes": usuarios_pendientes
    }
```

---

## Próximos Pasos

1. ⚠️ **Backend**: Implementar los 3 endpoints mencionados arriba
2. ⚠️ **Backend**: Asegurar que el modelo `InvitacionCoordinador` tenga campo `codigo`
3. ⚠️ **Backend**: Agregar trailing slash a todos los endpoints (`/api/invitaciones/aceptar/`)
4. ✅ **Frontend**: Navegación limpia y funcional
5. ✅ **Frontend**: Páginas de invitación y panel creadas

---

## Pruebas Recomendadas

### Flujo Completo:
1. Admin crea institución "Test University"
2. Admin envía invitación a `coordinador@test.com`
3. Coordinador inicia sesión
4. Coordinador navega a "Aprobar Código"
5. Coordinador ingresa código del email
6. Sistema redirige a "Mi Institución"
7. Panel muestra "Test University" con estadísticas en 0
8. Estado de institución cambia a "activa"

### Casos de Error:
- Código inválido → Mostrar error
- Código ya usado → Mostrar error
- Email no coincide → Mostrar error
- Sin autenticación → Redirigir a login
- Institución ya asignada → Manejar apropiadamente
