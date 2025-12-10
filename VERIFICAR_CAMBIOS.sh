#!/usr/bin/env bash

# 🔍 SCRIPT DE VERIFICACIÓN - Sistema de Archivos en Entregas
# Este script verifica que todos los cambios estén aplicados correctamente

echo "=" 
echo "🔍 VERIFICACIÓN DEL SISTEMA DE ARCHIVOS - 21 Nov 2025"
echo "="
echo ""

# 1. Verificar Backend Cambio #1 (retorna archivos_metadata)
echo "1️⃣ Verificando Cambio #1 Backend (entregar_tarea retorna archivos_metadata)..."
if grep -q '"archivos": archivos_metadata or \[\]' backend/src/services/academic/tarea_service.py; then
    echo "   ✅ Cambio #1 aplicado correctamente"
    echo "      Line contiene: 'archivos_metadata or []'"
else
    echo "   ❌ Cambio #1 NO aplicado"
    echo "      Verificar línea ~520 de tarea_service.py"
    echo "      Debe decir: \"archivos\": archivos_metadata or []"
fi
echo ""

# 2. Verificar Backend Cambio #2 (UPDATE en lugar de DELETE)
echo "2️⃣ Verificando Cambio #2 Backend (cancelar preserva archivos)..."
if grep -q "UPDATE entregas_tareas" backend/src/services/academic/tarea_service.py && \
   ! grep -q "DELETE FROM entregas_tareas" backend/src/services/academic/tarea_service.py; then
    echo "   ✅ Cambio #2 aplicado correctamente"
    echo "      Cancela sin eliminar (UPDATE, no DELETE)"
else
    echo "   ⚠️ Verificar Cambio #2"
    echo "      Debe haber UPDATE (sin DELETE) en cancelar_entrega()"
fi
echo ""

# 3. Verificar Frontend - handleDescargarArchivo
echo "3️⃣ Verificando Frontend - handleDescargarArchivo()..."
if grep -q "handleDescargarArchivo" frontend/src/pages/tareas/SubirTareaPage.tsx; then
    echo "   ✅ Función handleDescargarArchivo() existe"
else
    echo "   ❌ Función NO existe"
    echo "      Debe estar después de imports"
fi
echo ""

# 4. Verificar Frontend - UI POST-ENTREGA unificada
echo "4️⃣ Verificando Frontend - UI POST-ENTREGA refactorizada..."
if grep -q "Archivos subidos - MISMO DISEÑO" frontend/src/pages/tareas/SubirTareaPage.tsx; then
    echo "   ✅ UI POST-ENTREGA refactorizada"
else
    echo "   ⚠️ Verificar UI POST-ENTREGA"
    echo "      Debe usar cards individuales (no cuadro azul)"
fi
echo ""

# 5. Verificar Frontend - UI REFERENCIA unificada
echo "5️⃣ Verificando Frontend - UI REFERENCIA refactorizada..."
if grep -q "Archivos de entrega anterior cancelada - MISMO DISEÑO" frontend/src/pages/tareas/SubirTareaPage.tsx; then
    echo "   ✅ UI REFERENCIA refactorizada"
else
    echo "   ⚠️ Verificar UI REFERENCIA"
    echo "      Debe usar cards individuales (no cuadro amarillo)"
fi
echo ""

# 6. Verificar que /uploads existe
echo "6️⃣ Verificando directorio /uploads..."
if [ -d "backend/uploads/entregas" ]; then
    echo "   ✅ Directorio /uploads/entregas existe"
    ARCHIVOS=$(find backend/uploads/entregas -type f | wc -l)
    echo "      Archivos en disco: $ARCHIVOS"
else
    echo "   ⚠️ Directorio /uploads/entregas no existe"
    echo "      Se creará automáticamente al guardar archivos"
fi
echo ""

# 7. Verificar FastAPI mount /uploads
echo "7️⃣ Verificando que FastAPI monta /uploads..."
if grep -q 'app.mount("/uploads"' backend/src/main.py; then
    echo "   ✅ FastAPI monta /uploads como estático"
else
    echo "   ⚠️ FastAPI NO monta /uploads"
    echo "      Debe estar en main.py"
fi
echo ""

# 8. Listar archivos modificados
echo "8️⃣ Archivos Modificados Hoy:"
echo "   Backend:"
echo "   - backend/src/services/academic/tarea_service.py"
echo "     • Cambio #1: línea ~520 (retorna archivos_metadata)"
echo "     • Cambio #2: línea ~700 (UPDATE sin DELETE)"
echo ""
echo "   Frontend:"
echo "   - frontend/src/pages/tareas/SubirTareaPage.tsx"
echo "     • handleDescargarArchivo() función"
echo "     • UI POST-ENTREGA refactorizada"
echo "     • UI REFERENCIA refactorizada"
echo "   - frontend/src/components/features/tareas/ArchivoCard.tsx (nuevo - no usado aún)"
echo ""

# 9. Resumen
echo "=" 
echo "📋 PRÓXIMOS PASOS:"
echo "1. Reiniciar backend: cd backend && python -m uvicorn src.main:app --reload"
echo "2. Test manual: Subir archivo, entregar, ver que se muestra el nombre real"
echo "3. Verificar BD: psql -U postgres -d acadify_db -c \"SELECT archivos_adicionales FROM entregas_tareas LIMIT 1;\""
echo "="
echo ""
