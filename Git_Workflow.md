# Git Workflow – Proyecto [Acadify]

## Convención de commits
Usamos una convención semántica para identificar rápidamente los cambios:

- `feat()`: nueva funcionalidad
- `fix()`: corrección de errores
- `docs()`: documentación
- `style()`: cambios de formato/estilo
- `refactor()`: reestructuración de código
- `test()`: pruebas

Ejemplo:  
- `feat(ui) diseño base frontend`  
- `fix(ui) mejora diseño`

---

## Frecuencia de push/pull
- **Pull:** al iniciar cada jornada de trabajo.  
- **Push:** al finalizar cada jornada o completar una tarea importante.  
- Esto garantiza sincronización constante y evita conflictos.

---

## Política de ramas
- `main`: versión estable, lista para entrega.  
- `develop`: rama base de desarrollo.  
- `feature/*`: ramas para nuevas funcionalidades.  

---

## Política de pull requests
- Idealmente, los `feature/*` se integran a `develop` mediante pull requests.  
- Las fusiones a `main` deben hacerse solo desde `develop`.  
- En este proyecto algunas integraciones se hicieron directas por tiempo, pero se deja la política recomendada para futuras implementaciones.
