# 🔧 Configuración Chrome DevTools MCP

## ✅ Configuración Completada

El MCP de Chrome DevTools ha sido configurado exitosamente. Ahora puedo acceder a las herramientas de desarrollo de Chrome para ayudarte a depurar errores en tiempo real.

## 🚀 Cómo Usar

### Opción 1: Script Automático (Recomendado)

1. **Ejecuta el script** (en una terminal separada):

   ```bash
   cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify
   ./start-chrome-debug.sh
   ```

2. **Deja esa terminal abierta** - Chrome se ejecutará con debugging habilitado

3. **Usa el navegador normalmente** - Navega a tu aplicación y reproduce el error

4. **Yo podré ver**:
   - Logs de la consola
   - Errores de red (404, 422, etc.)
   - Estado de las requests
   - Variables del DOM
   - Storage (localStorage, sessionStorage)

### Opción 2: Manual

Si ya tienes Chrome abierto, ciérralo completamente y ejecuta:

```bash
# Linux/Arch:
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug

# O con Chromium:
chromium --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
```

## 🔄 Activar el MCP

1. **Reinicia VS Code/Cline** para que reconozca la configuración
2. O ejecuta el comando: `Cline: Reload MCP Servers`
3. Verifica que aparezca `chrome-devtools` en la lista de MCPs disponibles

## 📍 Archivos de Configuración Creados

- `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` - Configuración global
- `.vscode/mcp-settings.json` - Configuración del workspace
- `start-chrome-debug.sh` - Script para iniciar Chrome con debugging

## 🎯 Capacidades del MCP

Una vez conectado, podré:

✅ **Leer logs de consola** - Ver todos los console.log, errors, warnings
✅ **Inspeccionar Network** - Ver requests fallidas (404, 422, etc.)
✅ **Evaluar JavaScript** - Ejecutar código en el contexto de la página
✅ **Inspeccionar Storage** - Ver localStorage, cookies, etc.
✅ **Tomar screenshots** - Capturar el estado visual
✅ **Emular dispositivos** - Probar responsive
✅ **Medir performance** - Encontrar cuellos de botella

## 🐛 Troubleshooting

### El MCP no se conecta

1. Verifica que Chrome esté corriendo con debugging:

   ```bash
   curl http://localhost:9222/json/version
   ```

   Deberías ver información del navegador.

2. Verifica que no haya otro proceso usando el puerto 9222:

   ```bash
   lsof -i :9222
   ```

3. Reinicia VS Code completamente.

### Chrome no inicia con el script

Verifica qué ejecutable de Chrome tienes:

```bash
which google-chrome chromium chromium-browser
```

Edita `start-chrome-debug.sh` si necesitas cambiar el ejecutable.

## 📝 Siguiente Paso

**DESPUÉS DE CONFIGURAR EL MCP**, necesitas:

1. ✅ **Reiniciar el backend** (como mencioné antes):

   ```bash
   cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend
   source venv/bin/activate.fish
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. ✅ **Iniciar Chrome con debugging**:

   ```bash
   ./start-chrome-debug.sh
   ```

3. ✅ **Reproducir el error** en el navegador

4. ✅ **Yo podré ver los logs en tiempo real** y ayudarte a diagnosticar

---

## 🔗 Referencias

- [Chrome DevTools MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/chrome-devtools)
- [Chrome Remote Debugging](https://developer.chrome.com/docs/devtools/remote-debugging/)
