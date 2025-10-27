#!/usr/bin/env python3

# Script de prueba para verificar que el endpoint funciona

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/test-cursos")
async def test_mis_cursos():
    """Endpoint de prueba simple"""
    try:
        print("📚 Test endpoint funcionando...")
        
        cursos_mock = [
            {
                "id": "1",
                "nombre": "Historia Universal",
                "codigo": "HIS201",
                "descripcion": "Curso de historia",
                "modalidad": "semestral",
                "fecha_inicio": "2025-01-15",
                "fecha_fin": "2025-06-15",
                "fecha_creacion": "2025-01-15T10:00:00",
                "estado": "finalizado",
                "activo": False,
                "profesor": "Dr. García",
                "estudiantes": 0,
                "grupos": 1,
                "progreso": 100,
                "creditos": 3,
                "horas_academicas": 48
            }
        ]
        
        return JSONResponse({
            "success": True,
            "message": "Cursos de prueba obtenidos exitosamente",
            "data": cursos_mock,
            "total": len(cursos_mock),
            "source": "mock",
            "user_role": "temporal"
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return JSONResponse(
            status_code=500, 
            content={"error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)