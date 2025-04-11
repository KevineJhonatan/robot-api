"""Services pour le pipeline de traitement."""

import os
import logging
import tempfile
from typing import Dict, Optional
from datetime import datetime

from src.services.aws import TrackingService, STATUS, OPERATION_TYPES
from src.modules.pipeline.steps.company.processing import (
    process_companies_and_collect_data,
    prepare_excel_and_upload_to_snaplogic,
)
from src.modules.pipeline.steps.company.collection import fetch_company_list
from src.modules.pipeline.steps.snaplogic import retry_failed_snaplogic
from src.modules.pipeline.steps.snaplogic.temp_files import (
    cleanup_temp_files,
    find_latest_temp_file,
    remove_temp_files,
)
from src.constants import Environment

logger = logging.getLogger(__name__)


async def run_pipeline_service(
    username: str, 
    password: str, 
    environment: Environment = Environment.DEVELOPMENT,
    max_companies: Optional[int] = None
) -> Dict:
    """
    Service principal qui orchestre le pipeline complet.

    Args:
        username: Nom d'utilisateur pour l'authentification
        password: Mot de passe pour l'authentification
        environment: Environnement d'exécution (DEVELOPMENT, TEST, PRODUCTION)
        max_companies: Si spécifié, limite le nombre d'entreprises à traiter
    """
    tracking = TrackingService(environment)

    try:
        # Vérifier s'il existe des données temporaires à renvoyer
        temp_path = await find_latest_temp_file()

        if temp_path:
            logger.info(f"Fichier temporaire trouvé : {temp_path}")
            logger.info(
                "Tentative de renvoyer les données précédentes à Snaplogic avant de scraper"
            )

            try:
                # Retenter l'envoi à Snaplogic
                await retry_failed_snaplogic(temp_path, tracking)
                logger.info("Envoi des données temporaires réussi, fin du pipeline")
                return {
                    "status": STATUS["SUCCESS"],
                    "message": "Successfully resent data from temporary file",
                }

            except Exception as e:
                logger.error(f"Échec de l'envoi des données temporaires : {str(e)}")
                logger.info("Reprise du pipeline normal avec nouveau scraping")

        # Nettoyer les anciens fichiers temporaires
        await remove_temp_files()

        # Démarrer le tracking
        logger.info("Démarrage du pipeline...")
        await tracking.log_pipeline_operation(
            OPERATION_TYPES["PIPELINE_START"], status=STATUS["RUNNING"]
        )

        # Début du pipeline
        logger.info("Démarrage de la phase de scraping...")
        await tracking.log_pipeline_operation(
            OPERATION_TYPES["SCRAPING_START"], status=STATUS["RUNNING"]
        )

        try:
            # Récupération des entreprises
            logger.info(
                f"Tentative de récupération des entreprises avec l'utilisateur {username}..."
            )
            entreprises = await fetch_company_list(username, password, tracking)
            
            if max_companies:
                logger.info(f"Limitation à {max_companies} entreprises pour le test")
                entreprises = entreprises[:max_companies]
                
            logger.info(f"✓ Récupération réussie de {len(entreprises)} entreprises")

            # Traitement des données
            logger.info("Démarrage du traitement des données des entreprises...")
            successful_data = await process_companies_and_collect_data(
                username, password, entreprises, tracking
            )
            logger.info("✓ Traitement des données terminé avec succès")

            # Préparation et envoi des données
            logger.info("Préparation et envoi des données vers Snaplogic...")
            result = await prepare_excel_and_upload_to_snaplogic(
                entreprises, successful_data, tracking
            )
            logger.info("✓ Envoi des données vers Snaplogic terminé")

            # Marquer le pipeline comme terminé avec succès
            end_time = datetime.now().isoformat()
            logger.info(f"Pipeline terminé avec succès à {end_time}")
            await tracking.log_pipeline_operation(
                OPERATION_TYPES["SCRAPING_START"],
                status=STATUS["SUCCESS"],
                metadata={"end_time": end_time},
            )

            await tracking.log_pipeline_operation(
                OPERATION_TYPES["PIPELINE_SUCCESS"], status=STATUS["COMPLETED"]
            )

            return {"status": "success", "message": "Pipeline completed successfully"}

        except Exception as e:
            # En cas d'erreur, marquer le pipeline comme échoué
            error_msg = str(e)
            end_time = datetime.now().isoformat()
            logger.error(f"Erreur dans le pipeline: {error_msg}")
            logger.error(f"Stack trace:", exc_info=True)
            await tracking.log_pipeline_operation(
                OPERATION_TYPES["SCRAPING_START"],
                status=STATUS["FAILED"],
                error=error_msg,
                metadata={"end_time": end_time},
            )
            await tracking.log_pipeline_operation(
                OPERATION_TYPES["PIPELINE_ERROR"],
                status=STATUS["FAILED"],
                error=error_msg,
            )
            raise Exception(error_msg)

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise
    finally:
        # Nettoyer les vieux fichiers temporaires
        await cleanup_temp_files()
