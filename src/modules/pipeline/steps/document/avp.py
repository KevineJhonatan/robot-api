"""Service de collecte des AVPs."""

import logging
from typing import Dict, List

from src.services.aws import TrackingService, OPERATION_TYPES, STATUS
from src.modules.webscrapping.services import fetch_avps
from src.modules.pipeline.steps.company.pdf.collection import collect_company_pdfs

logger = logging.getLogger(__name__)

async def collect_company_documents(username: str, password: str, entreprise: dict, tracking: TrackingService) -> Dict:
    """
    Scrape toutes les données AVP pour une entreprise.
    
    Args:
        username: Identifiant pour l'API
        password: Mot de passe pour l'API
        entreprise: Données de l'entreprise
        tracking: Service de tracking AWS
        
    Returns:
        Dict contenant :
        - avps: Liste des AVPs
        - pdf_content: Contenu des PDFs en mémoire avec leur statut delta
          Format: {
              'siret_avp_id': {
                  'content': bytes_content,
                  'delta': bool
              }
          }
        
    Raises:
        Exception: En cas d'erreur lors du scraping
    """
    siret = entreprise['siret']
    
    try:
        logger.info(f"Début du scraping pour l'entreprise {siret}")
        
        # Récupération des AVPs
        logger.info(f"Récupération des AVPs pour {siret}")
        avps = await fetch_avps(username, password, entreprise['empId'])
        logger.info(f"AVPs récupérés pour {siret}.")
        await tracking.log_pipeline_operation(
            OPERATION_TYPES['AVPS_DONE'],
            metadata={'siret': siret, 'count': len(avps) if isinstance(avps, (list, dict)) else 0}
        )
        
        # Téléchargement des PDFs AVPs en utilisant le service spécialisé
        logger.info(f"Téléchargement des PDFs pour {siret}")
        pdf_contents = await collect_company_pdfs(
            siret=siret,
            tracking=tracking,
            username=username,
            password=password,
            entreprise=entreprise,
            avps=avps
        )
        logger.info(f"PDFs téléchargés pour {siret}.")
        
        return {
            'avps': avps,
            'pdf_content': pdf_contents
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du scraping pour {siret}: {str(e)}")
        await tracking.log_pipeline_operation(
            OPERATION_TYPES['AVPS_DONE'],
            status=STATUS['ERROR'],
            error=str(e),
            metadata={'siret': siret}
        )
        raise
