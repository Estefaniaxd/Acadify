import sys
import os
import asyncio
from sqlalchemy import text

# Add backend to path
sys.path.append(os.getcwd())

from src.core.database import SessionLocal
from src.crud.academic.tarea import crud_entrega_tarea
from src.schemas.academic.tarea_schemas import EntregaTareaResponse
from src.api.routes.invitaciones import get_mis_invitaciones
from src.models.auth.usuario import Usuario

async def debug_submissions():
    print("\n--- DEBUGGING SUBMISSIONS (Task: fdde58b0-1c15-4c65-a2c2-5cbe499ce5cf) ---")
    db = SessionLocal()
    try:
        tarea_id = "fdde58b0-1c15-4c65-a2c2-5cbe499ce5cf"
        entregas = crud_entrega_tarea.obtener_entregas_por_tarea(db=db, tarea_id=tarea_id)
        print(f"Found {len(entregas)} submissions.")
        
        for entrega in entregas:
            print(f"Checking submission {entrega.entrega_id} (Status: {entrega.estado})...")
            try:
                # Try to validate against schema
                dto = EntregaTareaResponse.model_validate(entrega)
                print("  ✅ Schema validation OK")
            except Exception as e:
                print(f"  ❌ Schema validation FAILED: {e}")
                # Print raw values to see what's wrong
                print(f"  Raw values: estado={entrega.estado}, calificacion={entrega.calificacion}")
    except Exception as e:
        print(f"❌ CRITICAL ERROR in submissions debug: {e}")
    finally:
        db.close()

async def debug_invitaciones():
    print("\n--- DEBUGGING INVITACIONES ---")
    db = SessionLocal()
    try:
        # Test import
        print("Attempting to import crud_institucion...")
        from src.crud.academic.crud_institucion import crud_institucion
        print("✅ Import successful.")
        
        # Test query logic (mocking user)
        print("Testing query logic...")
        from src.models.auth.invitation_token import InvitationToken
        invitaciones = db.query(InvitationToken).all()
        print(f"Found {len(invitaciones)} total invitations in DB.")
        
    except ImportError as e:
        print(f"❌ IMPORT ERROR: {e}")
    except Exception as e:
        print(f"❌ RUNTIME ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(debug_submissions())
    asyncio.run(debug_invitaciones())
