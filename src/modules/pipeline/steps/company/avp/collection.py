"""Service de collecte des AVPs."""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from src.services.aws.tracking import TrackingService
from src.services.aws import OPERATION_TYPES, STATUS
from src.services.dynamodb import AVPDownloadTracker
from src.constants.error_messages import PIPELINE_ERRORS
from src.constants import Environment
from src.modules.webscrapping.services import fetch_avps

logger = logging.getLogger(__name__)

async def collect_company_avps(
    siret: str,
    tracking: TrackingService,
    environment: Environment = Environment.DEVELOPMENT,
    username: str = None,
    password: str = None,
    entreprise: Dict = None
) -> List[Dict]:
    """
    Collecte les AVPs d'une entreprise.
    
    Args:
        siret: SIRET de l'entreprise
        tracking: Service de tracking
        environment: Environnement d'exécution
        username: Identifiant pour l'API
        password: Mot de passe pour l'API
        entreprise: Données de l'entreprise
        
    Returns:
        Liste des AVPs collectés avec leurs statuts delta
    """
    try:
        # Vérifie si les AVPs ont déjà été téléchargés
        download_tracker = AVPDownloadTracker(environment)
        cached_avps = await download_tracker.get_cached_avps(siret)
        cached_avps_set = set(cached_avps)  # Pour une recherche plus rapide
        
        # Récupérer les nouveaux AVPs
        avis_de_paiements = await fetch_avps(username, password, entreprise["empId"])
        
        # Marquer les AVPs comme delta ou non et définir les chemins PDF
        for avp in avis_de_paiements:
            if 'id' not in avp:
                logger.warning(f"AVP sans ID trouvé pour {siret}")
                continue
                
            avp_id = str(avp['id'])
            is_delta = avp_id not in cached_avps_set
            
            # Ajouter les informations de delta et le chemin du PDF
            avp['delta'] = is_delta
            avp['pdf_path'] = f"{'delta' if is_delta else 'data'}/{siret}/{avp_id}.pdf"
            
            # Marquer comme téléchargé dans DynamoDB
            if is_delta:
                await download_tracker.mark_avp_downloaded(
                    siret=siret,
                    avp_id=avp_id,
                    metadata={
                        'download_date': datetime.now().isoformat(),
                        'delta': True
                    }
                )
        
        return avis_de_paiements
        
    except Exception as e:
        error_msg = PIPELINE_ERRORS['AVP_ERROR'].format(siret, str(e))
        logger.error(error_msg)
        await tracking.log_pipeline_operation(
            OPERATION_TYPES['AVP_FETCH'],
            status=STATUS['ERROR'],
            error=error_msg,
            metadata={'siret': siret}
        )
        return []
