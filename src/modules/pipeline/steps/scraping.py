"""Services de scraping pour le pipeline."""

import logging
from typing import Dict, List

from src.services.aws.tracking import TrackingService
from src.services.aws import OPERATION_TYPES, STATUS
from src.modules.webscrapping.services import get_entreprises, fetch_avps, fetch_alts
from src.modules.pipeline.steps.company.pdf.collection import collect_company_pdfs

logger = logging.getLogger(__name__)

async def collect_company_documents(username: str, password: str, entreprise: dict, tracking: TrackingService) -> Dict:
    """Scrape toutes les données pour une entreprise."""
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
        
        # Récupération des alternants
        logger.info(f"Récupération des alternants pour {siret}")
        alternants = await fetch_alts(username, password, entreprise['empId'])
        logger.info(f"Alternants récupérés pour {siret}.")
        await tracking.log_pipeline_operation(
            OPERATION_TYPES['ALTERNANTS_DONE'],
            metadata={'siret': siret, 'count': len(alternants) if isinstance(alternants, (list, dict)) else 0}
        )
        
        result = {
            'avps': avps,
            'alternants': alternants,
            'pdf_content': pdf_contents
        }
        return result
        
    except Exception as e:
        error_msg = f"Failed scraping for {siret}: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

async def fetch_company_list(username: str, password: str, tracking: TrackingService) -> List[Dict]:
    """Récupère toutes les entreprises."""
    try:
        entreprises = await get_entreprises(username, password)
        await tracking.log_pipeline_operation(
            OPERATION_TYPES['ENTREPRISES_DONE'],
            metadata={'count': len(entreprises)}
        )
        return entreprises
    except Exception as e:
        error_msg = f"Failed getting enterprises: {str(e)}"
        logger.error(error_msg)
        await tracking.log_pipeline_operation(
            OPERATION_TYPES['SCRAPING_ERROR'],
            status=STATUS['FAILED'],
            error=error_msg
        )
        raise
