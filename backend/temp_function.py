@router.get("/mis-cursos")
async def obtener_mis_cursos():
    """
    Endpoint temporal simplificado para debuggear
    """
    try:
        print(f"📚 INICIANDO obtener_mis_cursos (debug)...")
        
        # Devolver respuesta simple sin BD para verificar que el endpoint funciona
        return {
            "success": True,
            "message": "Aún no te has unido a ningún curso",
            "data": [],
            "total": 0,
            "source": "debug",
            "user_role": "temporal",
            "empty_state": True,
            "empty_message": "¡Únete a un curso para comenzar tu aprendizaje! Usa el botón 'Nuevo Curso' para inscribirte con un código."
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": True,
            "message": "Error temporal",
            "data": [],
            "total": 0,
            "source": "error",
            "user_role": "temporal",
            "empty_state": True,
            "empty_message": "Ocurrió un problema al cargar los cursos. Intenta nuevamente."
        }