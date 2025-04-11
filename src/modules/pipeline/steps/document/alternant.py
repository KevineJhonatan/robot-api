"""Services de gestion des alternants."""

import logging
from typing import Dict, List

from src.services.aws.tracking import TrackingService
from src.services.aws import OPERATION_TYPES, STATUS
from src.modules.webscrapping.services import fetch_alts

logger = logging.getLogger(__name__)

async def fetch_alternants(username: str, password: str, emp_id: str, siret: str, tracking: TrackingService) -> List[Dict]:
    """
    Récupère la liste des alternants pour une entreprise.
    
    Args:
        username: Identifiant pour l'API
        password: Mot de passe pour l'API
        emp_id: ID de l'entreprise
        siret: SIRET de l'entreprise
        tracking: Service de tracking AWS
        
    Returns:
        Liste des alternants
        
    Raises:
        Exception: En cas d'erreur lors de la récupération
    """
    try:
        logger.info(f"Récupération des alternants pour {siret}")
        alternants = await fetch_alts(username, password, emp_id)
        logger.info(f"Alternants récupérés pour {siret}.")
        
        await tracking.log_pipeline_operation(
            OPERATION_TYPES['ALTERNANTS_DONE'],
            metadata={'siret': siret, 'count': len(alternants) if isinstance(alternants, (list, dict)) else 0}
        )
        
        return alternants
        
    except Exception as e:
        error_msg = f"Failed to fetch alternants for {siret}: {str(e)}"
        logger.error(error_msg)
        
        await tracking.log_pipeline_operation(
            OPERATION_TYPES['ALTERNANTS_DONE'],
            status=STATUS['ERROR'],
            error=error_msg,
            metadata={'siret': siret}
        )
        
        raise Exception(error_msg) from e
