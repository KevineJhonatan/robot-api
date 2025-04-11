"""Service de collecte des PDFs."""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from src.services.aws.tracking import TrackingService
from src.services.aws import OPERATION_TYPES, STATUS
from src.constants.error_messages import PIPELINE_ERRORS
from src.modules.webscrapping.services import download_avps_pdfs_memory

logger = logging.getLogger(__name__)


async def collect_company_pdfs(
    siret: str,
    tracking: TrackingService,
    username: str = "",
    password: str = "",
    entreprise: Dict = {},
    avps: List[Dict] = [],
) -> Dict[str, Dict]:
    """
    Collecte les PDFs d'une entreprise.

    Args:
        siret: SIRET de l'entreprise
        tracking: Service de tracking
        username: Identifiant pour l'API
        password: Mot de passe pour l'API
        entreprise: Données de l'entreprise
        avps: Liste des AVPs à télécharger

    Returns:
        Dictionnaire des PDFs collectés avec leur statut delta
        Format: {
            'delta/siret/avp_id.pdf': {  # Pour les nouveaux AVPs
                'content': bytes_content,
                'delta': True
            },
            'data/siret/avp_id.pdf': {   # Pour les AVPs existants
                'content': bytes_content,
                'delta': False
            }
        }
    """
    try:
        if not avps:
            logger.info(f"Aucun AVP à télécharger pour {siret}")
            return {}

        logger.info(f"Téléchargement des PDFs pour {siret}...")
        pdfs = await download_avps_pdfs_memory(
            username=username,
            password=password,
            empId=entreprise["empId"],
            siret=siret,
            avps=avps,
        )

        # Réorganiser les PDFs selon leur statut delta
        organized_pdfs = {}
        for avp in avps:
            if "id" not in avp or f'{siret}_{avp["id"]}' not in pdfs:
                continue

            # Le chemin dépend du statut delta de l'AVP
            is_delta = avp.get("delta", False)
            pdf_path = f"{'delta' if is_delta else 'data'}/{siret}/{avp['id']}.pdf"

            organized_pdfs[pdf_path] = {
                "content": pdfs[f'{siret}_{avp["id"]}']["content"],
                "delta": is_delta,
            }

        logger.info(f"✓ {len(organized_pdfs)} PDFs téléchargés pour {siret}")
        return organized_pdfs

    except Exception as e:
        error_msg = PIPELINE_ERRORS["PDF_ERROR"].format(siret, str(e))
        logger.error(error_msg)
        await tracking.log_pipeline_operation(
            OPERATION_TYPES["PDF_FETCH"],
            status=STATUS["ERROR"],
            error=error_msg,
            metadata={"siret": siret},
        )
        return {}
