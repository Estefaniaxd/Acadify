# 📚 Documentación Acadify Backend

Bienvenido a la documentación completa del backend de Acadify, una plataforma educativa moderna construida con FastAPI.

---

## 📂 Estructura

```
backend/
├── src/                    # Código fuente principal
│   ├── api/               # Endpoints REST
│   ├── core/              # Configuración y utilidades core
│   ├── crud/              # Operaciones CRUD
│   ├── models/            # Modelos SQLAlchemy
│   ├── schemas/           # Schemas Pydantic
│   ├── services/          # Lógica de negocio
│   └── utils/             # Utilidades
│
├── scripts/               # Scripts de utilidad
│   ├── performance/       # Tests de performance (Locust)
│   ├── sql/              # Scripts SQL
│   └── *.py              # Scripts de análisis y utilidades
│
├── migrations/            # Migraciones Alembic
│   ├── versions/         # Versiones de migraciones
│   └── 001_sistema_misiones.sql
│
├── tests/                # Tests unitarios
├── TEST/                 # Tests de integración y debug
├── docs/                 # Documentación técnica
│   └── reports/         # Reportes de proyecto
│
├── alembic/             # Configuración Alembic
├── Docs/                # Documentación adicional
└── BACKUP_LEGACY/       # Backups antiguos
```

---

## 🚀 Inicio Rápido

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 3. Ejecutar migraciones
```bash
# Con Alembic
alembic upgrade head

# O con script directo
cd migrations
python ejecutar_migracion.py
```

### 4. Iniciar servidor
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📁 Carpetas Principales

### `/src` - Código Fuente
Contiene toda la lógica de la aplicación organizada por capas:
- **api/**: Endpoints y rutas REST
- **models/**: Modelos de base de datos (SQLAlchemy)
- **schemas/**: Validación de datos (Pydantic)
- **crud/**: Operaciones de base de datos
- **services/**: Lógica de negocio
- **core/**: Configuración, seguridad, utilidades

### `/scripts` - Scripts de Utilidad
Scripts para mantenimiento, análisis y testing:
- **performance/**: Tests de carga con Locust
- **sql/**: Scripts SQL directos
- Análisis de modelos y tablas
- Población de datos de prueba
- Verificación de integridad

### `/migrations` - Migraciones de Base de Datos
- Migraciones Alembic en `/alembic/versions/`
- Scripts SQL directos para sistemas complejos
- README con instrucciones de ejecución

### `/tests` - Tests Automatizados
Tests unitarios organizados por módulo

### `/TEST` - Tests de Integración
Tests de debugging y verificación manual

---

## 🗄️ Base de Datos

### Tecnología
- **PostgreSQL 14+**
- **SQLAlchemy ORM**
- **Alembic** para migraciones

### Módulos Principales

#### 👥 Usuarios y Autenticación
- Usuarios, roles, permisos
- Autenticación JWT
- OAuth2 con password flow

#### 🏫 Sistema Académico
- Instituciones
- Cursos y asignaturas
- Estudiantes y profesores
- Inscripciones

#### 📝 Sistema de Evaluaciones
- Exámenes y quizzes
- Preguntas y respuestas
- Calificaciones automáticas
- Banco de preguntas

#### 🎮 Sistema de Gamificación
- **Misiones**: Diarias, semanales, mensuales
- **Monedas**: AcadiCoins (sistema de economía)
- **Tienda**: Items, avatares, accesorios
- **Logros**: Sistema de achievements
- **Rachas**: Seguimiento de actividad

#### 👤 Sistema de Avatares
- Personalización completa
- Categorías: cabeza, cuerpo, ropa, accesorios
- Inventario de usuario
- Sistema de compra con monedas

#### 💬 Sistema de Comunicación
- Chat en tiempo real (WebSockets)
- Notificaciones push
- Sistema de mensajería
- Reacciones y comentarios

---

## 🔧 Scripts Útiles

### Análisis y Verificación
```bash
# Verificar sistema de evaluaciones
python scripts/verify_evaluation_system_complete.py

# Verificar tablas de BD
python scripts/verify_tables_exist.py

# Analizar modelos
python scripts/analyze_all_models.py
```

### Datos de Prueba
```bash
# Crear datos de ejemplo
python scripts/create_sample_data.py

# Crear assets de avatares
python scripts/load_initial_assets.py

# Insertar datos de test
python scripts/insert_test_data.py
```

### Performance Testing
```bash
# Test básico de autenticación
locust -f scripts/performance/locustfile_auth.py

# Test completo del sistema
locust -f scripts/performance/locustfile.py
```

---

## 📊 APIs Principales

### Autenticación
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Registro
- `POST /api/auth/refresh` - Refrescar token

### Académico
- `GET /api/academic/cursos` - Listar cursos
- `GET /api/academic/instituciones` - Instituciones
- `POST /api/academic/inscripcion` - Inscribir estudiante

### Evaluaciones
- `GET /api/assessment/examenes` - Listar exámenes
- `POST /api/assessment/responder` - Responder examen
- `GET /api/assessment/calificaciones` - Ver calificaciones

### Gamificación
- `GET /api/gamification/misiones` - Misiones disponibles
- `POST /api/gamification/reclamar` - Reclamar recompensa
- `GET /api/gamification/tienda` - Items de tienda
- `POST /api/gamification/comprar` - Comprar item

### Avatares
- `GET /api/avatar/mi-avatar` - Mi avatar
- `PUT /api/avatar/actualizar` - Actualizar avatar
- `GET /api/avatar/inventario` - Mi inventario

### Comunicación
- `WebSocket /ws/chat/{room_id}` - Chat en tiempo real
- `GET /api/communication/mensajes` - Historial
- `POST /api/communication/enviar` - Enviar mensaje

---

## 🔐 Seguridad

- JWT para autenticación
- Password hashing con bcrypt
- Validación de permisos por endpoint
- CORS configurado
- Rate limiting en endpoints sensibles

---

## 🧪 Testing

```bash
# Tests unitarios
pytest tests/

# Tests con coverage
pytest --cov=src tests/

# Tests de integración
python TEST/test_api_integration.py
```

---

## 📈 Performance

- Redis para caché y sesiones
- Índices optimizados en BD
- Lazy loading de relaciones
- Paginación en listados
- Compresión de respuestas

---

## 📞 Soporte

Ver documentación principal en `/docs/` del proyecto.

---

**Última actualización**: Noviembre 2025
