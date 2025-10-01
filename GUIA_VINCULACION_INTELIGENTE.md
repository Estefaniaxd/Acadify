# 🎯 **Guía de Vinculación Inteligente de Estudiantes**

## 📋 **Resumen del Sistema**

Acadify ahora cuenta con un sistema de **vinculación inteligente** que conecta automáticamente a los usuarios con sus instituciones educativas usando dos métodos:

1. **🚀 Vinculación por Dominio de Email** (Automática)
2. **📧 Vinculación por Código de Invitación** (Manual)

---

## 🏗️ **Arquitectura del Sistema Académico**

### **Jerarquía Institucional:**
```
🏫 INSTITUCIÓN (Raíz)
  └── 📚 PROGRAMA (Carrera/Plan de estudios)
      └── 📖 CURSO (Materia específica)
          └── 👥 GRUPO (Sección con horario)
              └── 👨‍🎓 ESTUDIANTES (Inscritos)
```

### **Ejemplos Prácticos:**
- **🏫 Colegio Alejandro Obregón**
  - 📚 Bachillerato Científico
    - 📖 Matemáticas (H6QQEW)
    - 📖 Programación POO (QSCEZ7)
    - 📖 Historia Universal (X6MZFU)

---

## 🚀 **Método 1: Vinculación por Dominio de Email**

### **¿Cómo Funciona?**
El sistema reconoce automáticamente ciertos dominios de email y vincula al usuario con la institución correspondiente.

### **Dominios Configurados:**
| Dominio | Institución | Programa Por Defecto |
|---------|-------------|----------------------|
| `@arp.edu.co` | Colegio Alejandro Obregón | Bachillerato Científico |
| `@uniejemplo.edu` | Universidad Ejemplo | Ingeniería de Sistemas |
| `@colegio-ao.edu` | Colegio Alejandro Obregón | Bachillerato Científico |

### **Ejemplo de Flujo:**
1. Usuario: `admin@arp.edu.co`
2. Sistema detecta dominio: `arp.edu.co`
3. **✅ Vinculación automática** → Colegio Alejandro Obregón
4. Usuario puede inscribirse a cursos inmediatamente

---

## 📧 **Método 2: Vinculación por Código de Invitación**

### **¿Cuándo se Usa?**
- Email con dominio no registrado (ej: `estudiante@gmail.com`)
- Instituciones que prefieren control manual
- Usuarios que necesitan vinculación específica

### **Códigos de Prueba Disponibles:**
| Código | Institución | Programa |
|--------|-------------|----------|
| `INV-2025-ARP-001` | Colegio Alejandro Obregón | Bachillerato Científico |
| `INV-2025-UNEJ-001` | Universidad Ejemplo | Ingeniería de Sistemas |
| `INV-2025-ARP-MED` | Colegio Alejandro Obregón | Bachillerato Médico |
| `TEST-ARP-2025` | Colegio Alejandro Obregón | Bachillerato Científico |

### **Ejemplo de Flujo:**
1. Usuario: `estudiante@gmail.com`
2. Sistema NO reconoce dominio
3. **📧 Solicita código de invitación**
4. Usuario ingresa: `TEST-ARP-2025`
5. **✅ Vinculación exitosa** → Colegio Alejandro Obregón

---

## 🎮 **Cómo Probar el Sistema**

### **Paso 1: Usuarios con Email Institucional**
```bash
# 1. Iniciar sesión con usuario que tenga email @arp.edu.co
# 2. Ir a módulo académico
# 3. Si aparece modal de vinculación, hacer clic en "🎯 Auto-Vincular"
# 4. ✅ Vinculación automática exitosa
```

### **Paso 2: Usuarios con Email Externo**
```bash
# 1. Iniciar sesión con usuario que tenga email @gmail.com
# 2. Ir a módulo académico  
# 3. Modal de vinculación → "🎯 Auto-Vincular"
# 4. Sistema muestra modal de código de invitación
# 5. Ingresar: TEST-ARP-2025
# 6. ✅ Vinculación por código exitosa
```

### **Paso 3: Inscripción a Cursos**
```bash
# Después de vinculación exitosa:
# 1. Botón "Unirse a Curso"
# 2. Ingresar código: H6QQEW, QSCEZ7, o X6MZFU
# 3. ✅ Inscripción exitosa (solo cursos de tu institución)
```

---

## 🔧 **Endpoints API Nuevos**

### **Auto-Vinculación Inteligente**
```http
POST /academic/auto-vincular-estudiante
Authorization: Bearer {token}

# Respuesta exitosa por dominio:
{
  "success": true,
  "message": "¡Vinculación automática exitosa!",
  "programa": "Bachillerato Científico",
  "institucion": "Colegio Alejandro Obregón",
  "metodo": "dominio_email",
  "dominio": "arp.edu.co"
}

# Respuesta requiere código:
{
  "success": false,
  "requires_invitation": true,
  "message": "Tu dominio no está registrado...",
  "user_email": "usuario@gmail.com",
  "dominio": "gmail.com"
}
```

### **Vinculación por Código**
```http
POST /academic/vincular-por-codigo
Authorization: Bearer {token}
Content-Type: application/json

{
  "codigo_invitacion": "TEST-ARP-2025"
}

# Respuesta:
{
  "success": true,
  "message": "¡Vinculación exitosa!",
  "programa": "Bachillerato Científico",
  "institucion": "Colegio Alejandro Obregón",
  "metodo": "codigo_invitacion",
  "codigo_usado": "TEST-ARP-2025"
}
```

### **Generar Código de Invitación** *(Para Coordinadores)*
```http
POST /academic/generar-codigo-invitacion
Authorization: Bearer {token}
Content-Type: application/json

{
  "programa_id": "UUID_DEL_PROGRAMA",
  "descripcion": "Código para estudiantes de nuevo ingreso"
}

# Respuesta:
{
  "success": true,
  "codigo_invitacion": "INV-2025-COL-123",
  "programa": "Bachillerato Científico",
  "institucion": "Colegio Alejandro Obregón",
  "instrucciones": "Comparte este código con estudiantes..."
}
```

---

## 🔍 **Solución de Problemas**

### **❌ "Error obteniendo tus cursos"**
**Causa:** Usuario no tiene perfil de estudiante vinculado
**Solución:** Ir a módulo académico → Aparecerá modal de vinculación automáticamente

### **❌ "Código de invitación inválido"**
**Causa:** Código incorrecto o mal escrito
**Solución:** Verificar códigos de prueba en tabla anterior

### **❌ "Solo puedes inscribirte a cursos de tu institución"**
**Causa:** Intentando inscribirse a curso de otra institución
**Solución:** Usar códigos de curso de la misma institución del usuario

### **❌ "Tu sesión ha expirado"**
**Causa:** Token JWT vencido
**Solución:** Cerrar sesión e iniciar sesión nuevamente

---

## 🎯 **Funcionalidades Implementadas**

### **✅ Completado:**
- Auto-detección de dominios institucionales
- Sistema de códigos de invitación
- Validación de pertenencia institucional
- UI intuitiva con modales mejorados
- Manejo de errores específicos
- Recargar automático de datos post-vinculación

### **🚧 Pendiente por Implementar:**
- Tabla `CodigoInvitacion` en base de datos
- Expiración automática de códigos
- Panel de administración para generar códigos
- Notificaciones por email
- Logs de vinculaciones

---

## 📊 **Datos de Prueba**

### **Cursos Disponibles:**
- **H6QQEW** - Matemáticas (Colegio Alejandro Obregón)
- **QSCEZ7** - Programación POO (Colegio Alejandro Obregón)  
- **X6MZFU** - Historia Universal (Colegio Alejandro Obregón)

### **Usuarios de Prueba Recomendados:**
1. **admin@arp.edu.co** → Vinculación automática
2. **estudiante@gmail.com** → Código TEST-ARP-2025
3. **profesor@uniejemplo.edu** → Vinculación automática a Universidad Ejemplo

---

## 🚀 **Próximos Pasos**

1. **Base de Datos:** Crear tabla `CodigoInvitacion` con campos:
   - `codigo`, `programa_id`, `creado_por`, `fecha_expiracion`, `usado`

2. **Panel Admin:** Interfaz para coordinadores generar códigos

3. **Notificaciones:** Email automático con códigos de invitación

4. **Analytics:** Dashboard de vinculaciones y uso de códigos

5. **Seguridad:** Rate limiting y validación avanzada

---

*✨ **¡El sistema de vinculación inteligente está listo para uso!** ✨*