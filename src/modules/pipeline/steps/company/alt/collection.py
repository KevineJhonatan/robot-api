"""Service de collecte des alternants."""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from src.services.aws.tracking import TrackingService
from src.services.aws import OPERATION_TYPES, STATUS
from src.constants.error_messages import PIPELINE_ERRORS
from src.modules.webscrapping.services import fetch_alts

logger = logging.getLogger(__name__)

async def collect_company_alternants(
    siret: str,
    tracking: TrackingService,
    username: str = None,
    password: str = None,
    entreprise: Dict = None
) -> List[Dict]:
    """
    Collecte les alternants d'une entreprise.
    
    Args:
        siret: SIRET de l'entreprise
        tracking: Service de tracking
        username: Identifiant pour l'API
        password: Mot de passe pour l'API
        entreprise: Données de l'entreprise
        
    Returns:
        Liste des alternants collectés
    """
    try:
        logger.info(f"Récupération des alternants pour {siret}...")
        alternants = await fetch_alts(username, password, entreprise["empId"])
        logger.info(f"✓ {len(alternants)} alternants récupérés pour {siret}")
        
        return alternants
        
    except Exception as e:
        error_msg = PIPELINE_ERRORS['ALT_ERROR'].format(siret, str(e))
        logger.error(error_msg)
        await tracking.log_pipeline_operation(
            OPERATION_TYPES['ALT_FETCH'],
            status=STATUS['ERROR'],
            error=error_msg,
            metadata={'siret': siret}
        )
        return []
