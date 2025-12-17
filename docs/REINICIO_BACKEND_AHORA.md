# 🚀 REINICIO BACKEND - INSTRUCCIONES CRÍTICAS

## EL PROBLEMA:
- El backend aún corre con código VIEJO
- POST funciona (200) pero GET falla (500)
- Hemos hecho cambios pero NO se aplican hasta reiniciar

## LA SOLUCIÓN:

### PASO 1: Abre una NUEVA terminal (cmd/bash)

### PASO 2: Ejecuta ESTOS COMANDOS UNO POR UNO:

```bash
# 1. Ve al directorio backend
cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend

# 2. Mata TODOS los procesos Python/uvicorn
pkill -9 -f uvicorn
pkill -9 -f python

# 3. Espera 3 segundos
sleep 3

# 4. Activa el venv
source venv/bin/activate

# 5. Inicia el backend FRESH
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

### PASO 3: Espera a ver ESTO en la terminal:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### PASO 4: Vuelve al navegador y haz click en "ENTREGAR TAREA" de nuevo

---

## ¿QUÉ CAMBIAMOS?

✅ **tarea_service.py**: Agregadas conversiones JSON completas
✅ **curso_tareas.py**: Endpoint GET ahora retorna JSONResponse PURO (sin Pydantic)
✅ **tarea_schemas.py**: Removidas configuraciones duplicadas

---

## SI AÚN FALLA:

1. Abre DevTools → Console (F12)
2. Copia el error exacto
3. Verifica que ves "✅ Application startup complete" en la terminal

---

**⚠️ EJECUTA LOS COMANDOS AHORA Y CUÉNTAME CUANDO VEAS "Uvicorn running"**
