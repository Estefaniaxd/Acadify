import pyotp
import qrcode
import io
import base64
from typing import Optional
from src.core.config import settings


class TwoFAService:
    """Servicio para manejo de 2FA con TOTP"""
    
    def __init__(self):
        self.issuer_name = "Acadify"
    
    def generate_secret(self) -> str:
        """Generar secret único para TOTP"""
        return pyotp.random_base32()
    
    def generate_provisioning_uri(
        self, 
        secret: str, 
        user_email: str
    ) -> str:
        """
        Generar URI de aprovisionamiento para apps 2FA
        
        Args:
            secret: Secret TOTP
            user_email: Email del usuario
        
        Returns:
            str: URI otpauth://
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=user_email,
            issuer_name=self.issuer_name
        )
    
    def generate_qr_code_base64(self, provisioning_uri: str) -> str:
        """
        Generar código QR en base64 para el URI de aprovisionamiento
        
        Args:
            provisioning_uri: URI otpauth://
        
        Returns:
            str: Imagen QR en base64
        """
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
    
    def verify_totp(self, secret: str, token: str, window: int = 1) -> bool:
        """
        Verificar código TOTP
        
        Args:
            secret: Secret TOTP del usuario
            token: Código de 6 dígitos ingresado
            window: Ventana de tolerancia (períodos de 30s)
        
        Returns:
            bool: True si el código es válido
        """
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, window=window)
        except Exception:
            return False
    
    def generate_backup_codes(self, count: int = 8) -> list[str]:
        """
        Generar códigos de respaldo para 2FA
        
        Args:
            count: Número de códigos a generar
        
        Returns:
            list: Lista de códigos de respaldo
        """
        codes = []
        for _ in range(count):
            # Generar código de 8 dígitos
            code = pyotp.random_base32()[:8]
            codes.append(code)
        return codes
    
    def is_backup_code_valid(self, code: str, stored_codes: list[str]) -> bool:
        """
        Verificar si un código de respaldo es válido
        
        Args:
            code: Código ingresado por el usuario
            stored_codes: Códigos de respaldo almacenados
        
        Returns:
            bool: True si el código es válido
        """
        return code.upper() in [c.upper() for c in stored_codes]
