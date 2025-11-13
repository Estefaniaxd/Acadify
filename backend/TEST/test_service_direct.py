"""Test directo del servicio de invitaciones para ver el error"""
import sys
sys.path.insert(0, '/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend')

from src.db.session import SessionLocal
from src.services.invitation_service import InvitationService

db = SessionLocal()

try:
    # El código 189429 debería existir del test anterior
    result = InvitationService.validar_y_obtener_info(db, "189429")
    print(f"✓ Resultado: {result}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
