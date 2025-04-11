"""Services de traitement des données entreprises."""

import logging
from typing import Dict, List, Any
from datetime import datetime
from io import BytesIO

from src.services.aws.tracking import TrackingService
from src.services.aws import OPERATION_TYPES, STATUS
from src.services.dynamodb import AVPDownloadTracker
from src.modules.pipeline.steps.snaplogic import send_to_snaplogic
from src.modules.pipeline.utils.excel import prepare_excel
from src.modules.pipeline.steps.company.avp.collection import collect_company_avps
from src.modules.pipeline.steps.company.pdf.collection import collect_company_pdfs
from src.modules.pipeline.steps.company.alt.collection import collect_company_alternants
from src.constants.error_messages import PIPELINE_ERRORS
from src.constants import Environment

logger = logging.getLogger(__name__)


async def process_companies_and_collect_data(
    username: str,
    password: str,
    entreprises: List[Dict],
    tracking: TrackingService,
    environment: Environment = Environment.DEVELOPMENT,
) -> List[Dict]:
    """
    Traite les données pour toutes les entreprises de manière séquentielle.

    Args:
        username: Identifiant pour l'API
        password: Mot de passe pour l'API
        entreprises: Liste des entreprises à traiter
        tracking: Service de tracking
        environment: Environnement d'exécution

    Returns:
        Liste des données récupérées avec succès
    """
    try:
        if not entreprises:
            error_msg = PIPELINE_ERRORS["DATA_ERROR"].format("No companies provided")
            logger.error(error_msg)
            raise Exception(error_msg)

        # Initialisation du tracker de téléchargement
        download_tracker = AVPDownloadTracker(environment)

        # Traitement séquentiel
        all_data = []
        successful_data = []

        for entreprise in entreprises:
            try:
                siret = entreprise.get("siret")
                if not siret:
                    logger.warning("SIRET manquant pour une entreprise")
                    continue

                # Collecte des données
                logger.info(f"Traitement de l'entreprise {siret}...")
                avps = await collect_company_avps(
                    siret=siret,
                    tracking=tracking,
                    environment=environment,
                    username=username,
                    password=password,
                    entreprise=entreprise,
                )
                pdfs = await collect_company_pdfs(
                    siret=siret,
                    tracking=tracking,
                    username=username,
                    password=password,
                    entreprise=entreprise,
                    avps=avps,
                )
                alternants = await collect_company_alternants(
                    siret=siret,
                    tracking=tracking,
                    username=username,
                    password=password,
                    entreprise=entreprise,
                )

                if avps or pdfs or alternants:
                    data = {
                        "entreprise": entreprise,
                        "data": {
                            "siret": siret,
                            "avps": avps,
                            "pdfs": pdfs,
                            "alternants": alternants,
                            "processed_at": datetime.now().isoformat(),
                        },
                    }
                    successful_data.append(data)
                    logger.info(f"✓ Données collectées avec succès pour {siret}")

                    # Marquer comme téléchargé si succès
                    if data["data"].get("avps"):
                        for avp in data["data"]["avps"]:
                            # Ne marquer dans DynamoDB que les nouveaux AVPs (delta=True)
                            if avp.get("delta", False) and "id" in avp:
                                await download_tracker.mark_avp_downloaded(
                                    siret=siret,
                                    avp_id=str(avp["id"]),
                                    metadata={
                                        "download_date": datetime.now().isoformat(),
                                        "delta": True,
                                    },
                                )

                all_data.append(
                    {
                        "entreprise": entreprise,
                        "data": {
                            "siret": siret,
                            "status": STATUS["SUCCESS"],
                            "error": None,
                        },
                    }
                )

            except Exception as e:
                error_msg = PIPELINE_ERRORS["COMPANY_ERROR"].format(siret, str(e))
                logger.error(error_msg)
                await tracking.log_pipeline_operation(
                    OPERATION_TYPES["COMPANY_ERROR"],
                    siret=siret,
                    status=STATUS["ERROR"],
                    error=error_msg,
                    metadata={"siret": siret},
                )
                all_data.append(
                    {
                        "entreprise": entreprise,
                        "data": {
                            "siret": siret,
                            "status": STATUS["ERROR"],
                            "error": str(e),
                        },
                    }
                )

        # Vérifier si des données ont été récupérées
        if not successful_data:
            error_msg = PIPELINE_ERRORS["DATA_ERROR"].format(
                "No data could be retrieved from any company"
            )
            logger.error(error_msg)
            raise Exception(error_msg)

        return successful_data

    except Exception as e:
        error_msg = PIPELINE_ERRORS["PROCESS_ERROR"].format(str(e))
        logger.error(error_msg)
        logger.error("Stack trace complète:", exc_info=True)
        raise Exception(error_msg) from e


async def prepare_excel_and_upload_to_snaplogic(
    entreprises: List[Dict],
    successful_data: List[Dict],
    tracking: TrackingService,
    environment: Environment = Environment.DEVELOPMENT,
) -> Dict[str, Any]:
    """
    Prépare et envoie les données à SnapLogic.

    Le processus comprend :
    1. Génération d'un batch_id unique
    2. Création de l'Excel avec toutes les données
    3. Préparation des métadonnées
    4. Envoi des fichiers à SnapLogic
    5. Tracking de l'opération

    Args:
        entreprises: Liste complète des entreprises
        successful_data: Données récupérées avec succès
        tracking: Service de tracking
        environment: Environnement d'exécution

    Returns:
        Dict contenant :
        - status: État de l'opération
        - message: Message de succès
        - batch_id: Identifiant unique du batch
        - processed_companies: Nombre d'entreprises traitées
        - snaplogic_response: Réponse de SnapLogic

    Raises:
        Exception: En cas d'erreur lors de la préparation ou de l'envoi
    """
    try:
        if not successful_data:
            error_msg = PIPELINE_ERRORS["DATA_ERROR"].format(
                "No successful data to process"
            )
            logger.error(error_msg)
            raise Exception(error_msg)

        # Générer un batch_id unique
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Préparation du batch {batch_id}")

        await tracking.log_pipeline_operation(
            operation_type=OPERATION_TYPES["SNAPLOGIC_SEND"],
            status=STATUS["RUNNING"],
            metadata={"batch_id": batch_id},
        )

        try:
            # Préparer l'Excel
            excel_data = BytesIO()
            await prepare_excel(successful_data, excel_data)
            excel_data.seek(0)
        except Exception as e:
            error_msg = PIPELINE_ERRORS["EXCEL_ERROR"].format(str(e))
            logger.error(error_msg)
            raise Exception(error_msg) from e

        try:
            # Extraire les PDFs
            pdfs_data = {}
            for item in successful_data:
                siret = item["entreprise"]["siret"]
                if "pdfs" in item["data"]:
                    pdfs_list = item["data"]["pdfs"]
                    for pdf_name, pdf in pdfs_list.items():
                        pdf_content = pdf["content"]
                        # Get PDF metadata
                        avp_id = (pdf_name.split(".")[0]).split("/")[-1]
                        delta = pdf.get("delta", False)
                        pdf_key = f"{siret}_{avp_id}"
                        pdfs_data[pdf_name] = {
                            "content": pdf_content,
                            "filename": f"{pdf_name}",
                            "delta": delta,
                        }
        except Exception as e:
            error_msg = PIPELINE_ERRORS["PDF_ERROR"].format(str(e))
            logger.error(error_msg)
            raise Exception(error_msg) from e

        # Préparer les métadonnées
        metadata = {
            "batch_id": batch_id,
            "timestamp": datetime.now().isoformat(),
            "entreprises": [
                {
                    "siret": e.get("siret", "N/A"),
                    "denomination": e.get("denomination", "N/A"),
                }
                for e in entreprises
            ],
            "stats": {
                "total_entreprises": len(entreprises),
                "success_count": len(successful_data),
            },
        }

        # Envoyer à SnapLogic
        response = await send_to_snaplogic(excel_data, pdfs_data, metadata, tracking)

        return {
            "status": "success",
            "message": "Data successfully sent to SnapLogic",
            "batch_id": batch_id,
            "processed_companies": len(successful_data),
            "snaplogic_response": response,
        }

    except Exception as e:
        error_msg = PIPELINE_ERRORS["DATA_ERROR"].format(str(e))
        logger.error(error_msg)
        raise Exception(error_msg) from e
