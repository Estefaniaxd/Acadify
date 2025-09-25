# CI/CD Acadify

![GitHub CI](https://github.com/JuanEstebanMartinezM/Acadify/actions/workflows/main.yml/badge.svg)
[![GitLab CI](https://gitlab.com/tu-usuario/tu-repo/badges/main/pipeline.svg)](https://gitlab.com/tu-usuario/tu-repo/-/pipelines)

Este repositorio utiliza integración continua (CI) tanto en **GitHub Actions** como en **GitLab CI** para automatizar pruebas y calidad de código en backend (Python) y frontend (Node.js/React).

## ¿Qué hace el pipeline CI?

- **Backend (Python):**
  - Instala dependencias desde `backend/requirements.txt`.
  - Cachea los paquetes de pip para acelerar builds futuros.
  - Ejecuta linter `flake8` para asegurar calidad de código.
  - Corre los tests con `pytest` y muestra resultados.

- **Frontend (Node.js/React):**
  - Instala dependencias desde `frontend/package.json`.
  - Cachea `node_modules` para builds más rápidos.
  - Ejecuta linter `eslint` para verificar estilo y errores comunes.
  - Compila el frontend con `npm run build`.
  - Corre tests si están definidos en el proyecto.

## ¿Cuándo se ejecuta?

- En cada push o merge request a las ramas principales (`develop`, `main`).
- En cada pull request (GitHub) o merge request (GitLab).

## ¿Dónde ver el estado?

- **GitHub:** El badge de arriba muestra el estado actual del pipeline CI en GitHub Actions.
- **GitLab:** El badge muestra el estado del pipeline en GitLab CI (ajusta la URL a tu repo real).

---

¿Quieres agregar deploy automático, coverage o notificaciones? ¡Solo pídelo!
