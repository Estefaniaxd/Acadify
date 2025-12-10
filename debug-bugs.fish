#!/usr/bin/env fish
# DEBUG_BUGS.fish - Script para debuggear los dos bugs críticos

echo "🔍 DEBUG: Problemas de archivos y respuestas"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend

# Obtener el venv Python
set PYTHON /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend/venv/bin/python

echo ""
echo "1️⃣ Verificando que los cambios se aplicaron..."
echo "─────────────────────────────────────────────"

$PYTHON -c "
import sys
sys.path.insert(0, '.')

# Revisar que la línea duplicada fue removida
with open('src/services/academic/comentario_service.py', 'r') as f:
    content = f.read()
    
# Buscar la línea 147 - debe NO tener duplicación
if 'comentario.archivos_lista = archivos_validos' in content:
    count = content.count('comentario.archivos_lista = archivos_validos')
    if count == 1:
        print('✅ FIX #1 APLICADO: Solo una asignación de archivos_lista')
    else:
        print(f'⚠️  WARNING: {count} asignaciones encontradas (debería ser 1)')
else:
    print('❌ ERROR: No se encontró asignación de archivos_lista')

# Verificar que obtener_comentarios_curso carga respuestas
if 'obtener_respuestas' in content:
    print('✅ FIX #2 APLICADO: obtener_comentarios_curso carga respuestas')
else:
    print('❌ ERROR: obtener_comentarios_curso NO carga respuestas')
"

echo ""
echo "2️⃣ Revisando query de obtener_comentarios_curso..."
echo "─────────────────────────────────────────────────────"

$PYTHON -c "
import sys
sys.path.insert(0, '.')
from src.services.academic.comentario_service import ComentarioService
import inspect

# Obtener el código del método
source = inspect.getsource(ComentarioService.obtener_comentarios_curso)

# Verificar que busca por comentario_padre_id IS NULL
if 'comentario_padre_id IS NULL' in source:
    print('✅ Query SOLO obtiene comentarios raíz (comentario_padre_id IS NULL)')
else:
    print('⚠️  WARNING: Query podría estar obteniendo también respuestas')

# Verificar que llama obtener_respuestas
if 'obtener_respuestas' in source:
    print('✅ Se está cargando respuestas para cada comentario')
else:
    print('❌ ERROR: NO se cargan respuestas de comentarios')
"

echo ""
echo "3️⃣ Verificando frontend send de comentario_padre_id..."
echo "─────────────────────────────────────────────────────────"

if [ -f ../frontend/src/modules/academico/CourseDetail.tsx ]
    grep -A2 'handleAddComment' ../frontend/src/modules/academico/CourseDetail.tsx | grep -q 'comentario_padre_id'
    if [ $status -eq 0 ]
        echo "✅ Frontend envía comentario_padre_id"
    else
        echo "❌ Frontend NO envía comentario_padre_id"
    end
else
    echo "⚠️  No se puede verificar frontend"
end

echo ""
echo "4️⃣ Verificando archivos_adjuntos en response..."
echo "────────────────────────────────────────────────"

$PYTHON -c "
import sys
sys.path.insert(0, '.')
from src.services.academic.comentario_service import ComentarioService
import inspect

# Revisar que _enriquecer_archivos_adjuntos se usa
source = inspect.getsource(ComentarioService.obtener_comentarios_curso)
count = source.count('_enriquecer_archivos_adjuntos')
print(f'✅ _enriquecer_archivos_adjuntos se llama {count} veces en obtener_comentarios_curso')

# Revisar que también se usa en obtener_respuestas
source2 = inspect.getsource(ComentarioService.obtener_respuestas)
if '_enriquecer_archivos_adjuntos' in source2:
    print('✅ _enriquecer_archivos_adjuntos se usa también en obtener_respuestas')
else:
    print('❌ obtener_respuestas NO enriquece archivos')
"

echo ""
echo "5️⃣ Resumiendo estado..."
echo "──────────────────────"
echo ""
echo "🎯 ESPERADO después de FIX:"
echo "   • Backend guarda comentario_padre_id cuando es respuesta"
echo "   • Backend NO retorna respuestas en array raíz"
echo "   • Backend SÍ retorna respuestas en campo 'respuestas' de cada comentario"
echo "   • Backend enriquece archivos en AMBOS (comentarios y respuestas)"
echo "   • Frontend mapea comentario_padre_id correctamente"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "   1. Verificar logs del backend mientras creas comentario+respuesta+archivo"
echo "   2. En frontend, abrir DevTools y revisar Network (response del GET)"
echo "   3. Si archivos desaparecen: revisar que _enriquecer_archivos_adjuntos retorna datos"
echo "   4. Si respuestas aparecen como nuevos: revisar que respuestas array no está vacío"
