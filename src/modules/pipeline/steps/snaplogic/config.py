"""Configuration pour l'intégration SnapLogic."""

from typing import Optional
from pydantic import BaseModel
from src.config import config

class SnapLogicConfig(BaseModel):
    """Configuration pour l'API SnapLogic."""
    BASE_URL: str = config('SNAPLOGIC_BASE_URL', cast=str)
    UPLOAD_ENDPOINT: str = config('SNAPLOGIC_UPLOAD_ENDPOINT', cast=str)
    BEARER: str = config('SNAPLOGIC_BEARER', cast=str)
    NOTIFICATION_ENDPOINT: str = config('SNAPLOGIC_NOTIFICATION_ENDPOINT', cast=str)
    NOTIFICATION_BEARER: str = config('SNAPLOGIC_NOTIFICATION_BEARER', cast=str)
    TIMEOUT: int = config('SNAPLOGIC_TIMEOUT', cast=int, default=3600)

def reload_config():
    """Recharge la configuration depuis le fichier .env"""
    global snaplogic_config
    snaplogic_config = SnapLogicConfig()

# Configuration instance
snaplogic_config = SnapLogicConfig()

# Types MIME
MIME_TYPES = {
    'EXCEL': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'PDF': 'application/pdf',
    'JSON': 'application/json'
}

def get_headers(batch_id: Optional[str] = None) -> dict:
    """
    Retourne les headers pour l'API SnapLogic.
    
    Args:
        batch_id: Optionnel, identifiant du batch pour le tracking
        
    Returns:
        Headers pour l'API
    """
    return {
        'Authorization': snaplogic_config.BEARER,  # BEARER contient déjà "Bearer"
        # Ne pas spécifier Content-Type pour l'envoi multipart
        # aiohttp le fera automatiquement avec la bonne boundary
    }
