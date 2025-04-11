"""Services de collecte des données entreprises."""

import logging
from typing import Dict, List

from src.services.aws.tracking import TrackingService
from src.services.aws import OPERATION_TYPES, STATUS
from src.modules.webscrapping.services import get_entreprises

logger = logging.getLogger(__name__)

async def fetch_company_list(username: str, password: str, tracking: TrackingService) -> List[Dict]:
    """
    Récupère la liste des entreprises.
    
    Args:
        username: Identifiant pour l'API
        password: Mot de passe pour l'API
        tracking: Service de tracking AWS
        
    Returns:
        Liste des entreprises
        
    Raises:
        Exception: En cas d'erreur lors de la récupération
    """
    try:
        logger.info("Début de la récupération de la liste des entreprises...")
        logger.info(f"Tentative d'authentification avec l'utilisateur: {username}")
        
        entreprises = (await get_entreprises(username, password))['items']
        
        if not entreprises:
            logger.warning("Aucune entreprise n'a été récupérée")
            raise Exception("La liste des entreprises est vide")
            
        logger.info(f"✓ {len(entreprises)} entreprises récupérées avec succès")
        
        await tracking.log_pipeline_operation(
            OPERATION_TYPES['COMPANIES_DONE'],
            metadata={'count': len(entreprises)}
        )
        
        return entreprises
        
    except Exception as e:
        error_msg = f"Échec de la récupération de la liste des entreprises: {str(e)}"
        logger.error(error_msg)
        logger.error("Stack trace complète:", exc_info=True)
        
        await tracking.log_pipeline_operation(
            OPERATION_TYPES['COMPANIES_DONE'],
            status=STATUS['ERROR'],
            error=error_msg
        )
        
        raise Exception(error_msg) from e
