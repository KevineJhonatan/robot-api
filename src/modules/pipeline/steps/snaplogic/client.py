"""Client SnapLogic pour l'application."""

import os
import json
import logging
import aiohttp
import asyncio
from io import BytesIO
from typing import Dict, Any, Optional
import pickle

from .config import snaplogic_config, get_headers
from src.services.aws import TrackingService, STATUS, OPERATION_TYPES
from src.constants.error_messages import SNAPLOGIC_ERRORS, GENERAL_ERRORS
from .multipart import _create_multipart
from .temp_files import cleanup_temp_files, create_temp_file

logger = logging.getLogger(__name__)

SNAPLOGIC_URL = f"{snaplogic_config.BASE_URL}{snaplogic_config.UPLOAD_ENDPOINT}"


async def _send_http_request(
    session: aiohttp.ClientSession,
    url: str,
    form: aiohttp.FormData,
    headers: Dict[str, str],
) -> Dict[str, Any]:
    """
    Envoie une requête HTTP à SnapLogic et traite la réponse.
    """
    logging.info(f"Sending request to SnapLogic: {url}")
    logging.info(f"Headers: {headers}")

    try:
        async with session.post(
            url, data=form, headers=headers, chunked=True
        ) as response:
            logging.info(f"SnapLogic response status: {response.status}")
            response_text = await response.text()
            logging.info(f"SnapLogic response: {response_text}")

            try:
                if isinstance(response_text, str):
                    # Si la réponse est déjà un dictionnaire sous forme de chaîne, on la retourne directement
                    if response_text.startswith("{") and response_text.endswith("}"):
                        return {"status": "success", "data": response_text}
                response_data = json.loads(response_text)
                return response_data
            except json.JSONDecodeError as e:
                # Si on ne peut pas parser le JSON, on retourne quand même un succès avec les données brutes
                logging.warning(f"Could not parse SnapLogic response as JSON: {str(e)}")
                return {"status": "success", "data": response_text}

    except asyncio.TimeoutError:
        error_msg = GENERAL_ERRORS["TIMEOUT_ERROR"].format("SnapLogic")
        logging.error(error_msg)
        raise Exception(error_msg)
    except aiohttp.ClientError as e:
        error_msg = SNAPLOGIC_ERRORS["NETWORK_ERROR"].format(str(e))
        logging.error(error_msg)
        raise Exception(error_msg) from e
    except Exception as e:
        error_msg = SNAPLOGIC_ERRORS["SEND_ERROR"].format(str(e))
        logging.error(error_msg)
        raise Exception(error_msg) from e


async def _send_batch_to_snaplogic(
    session: aiohttp.ClientSession,
    excel_data: Optional[BytesIO],
    pdfs_batch: Dict[str, Dict[str, Any]],
    metadata: Dict[str, Any],
    batch_number: int,
    total_batches: int,
    tracking: TrackingService,
) -> Dict[str, Any]:
    """
    Envoie un lot de données à SnapLogic.
    """
    form = await _create_multipart(
        excel_data, pdfs_batch, metadata, batch_number, total_batches
    )
    headers = get_headers()
    response = await _send_http_request(session, SNAPLOGIC_URL, form, headers)

    # Traquer chaque batch
    await tracking.log_pipeline_operation(
        OPERATION_TYPES["SNAPLOGIC_UPLOAD"],
        status=STATUS["SUCCESS"],
        metadata={"batch_id": metadata["batch_id"], "batch_number": batch_number},
    )

    return response


async def _send_large_data(
    excel_data: BytesIO,
    pdfs_data: Dict[str, Dict[str, Any]],
    metadata: Dict[str, Any],
    tracking: TrackingService,
) -> Dict[str, Any]:
    """Envoie les données en plusieurs requêtes si elles sont trop volumineuses"""
    # Diviser en lots de 10 PDFs maximum
    pdfs_items = list(pdfs_data.items())
    batches = []
    for i in range(0, len(pdfs_items), 10):
        batch = dict(pdfs_items[i : i + 10])
        batches.append(batch)

    logger.info(f"Envoi en {len(batches)} lots")

    responses = []
    async with aiohttp.ClientSession() as session:
        for i, batch in enumerate(batches, 1):
            # Premier batch = avec Excel, autres sans
            excel = excel_data if i == 1 else None

            response = await _send_batch_to_snaplogic(
                session=session,
                excel_data=excel,
                pdfs_batch=batch,
                metadata=metadata,
                batch_number=i,
                total_batches=len(batches),
                tracking=tracking,
            )
            responses.append(response)
            logger.info(f"Batch {i}/{len(batches)} envoyé avec succès")

    return {
        "status": "success",
        "message": f"Successfully sent {len(batches)} batches",
        "parts": responses,
    }


async def send_to_snaplogic(
    excel_data: BytesIO,
    pdfs_data: Dict[str, Dict[str, Any]],
    metadata: Dict[str, Any],
    tracking: TrackingService,
) -> Dict[str, Any]:
    """
    Envoie les données à SnapLogic via son API.
    """
    try:
        # Enregistrer les données avant l'envoi au cas où
        temp_path = await create_temp_file(excel_data, pdfs_data, metadata)
        logger.info(f"Données sauvegardées dans {temp_path}")

        # Configurer la session HTTP
        timeout = aiohttp.ClientTimeout(total=3600)  # 1 heure de timeout
        headers = get_headers()

        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                # Tenter l'envoi
                if len(pdfs_data) > 10:
                    response = await _send_large_data(
                        excel_data, pdfs_data, metadata, tracking
                    )
                else:
                    form = await _create_multipart(
                        excel_data, pdfs_data, metadata, 1, 1
                    )
                    response = await _send_http_request(
                        session, SNAPLOGIC_URL, form, headers
                    )

                # Si succès, nettoyer les fichiers temporaires de ce batch
                await cleanup_temp_files(batch_id=metadata["batch_id"])
                # Et aussi les vieux fichiers
                await cleanup_temp_files(max_age_hours=24)

                return response

            except Exception as e:
                error_msg = SNAPLOGIC_ERRORS["SEND_ERROR"].format(str(e))
                logger.error(error_msg)

                # Enregistrer l'erreur dans le tracking
                await tracking.log_pipeline_operation(
                    OPERATION_TYPES["SNAPLOGIC_UPLOAD"],
                    status=STATUS["ERROR"],
                    error=error_msg,
                    metadata={"batch_id": metadata["batch_id"]},
                )

                raise Exception(error_msg) from e

    except Exception as e:
        error_msg = SNAPLOGIC_ERRORS["SEND_ERROR"].format(str(e))
        logger.error(error_msg)
        raise Exception(error_msg) from e


async def retry_failed_snaplogic(
    temp_path: str, tracking: TrackingService
) -> Dict[str, Any]:
    """
    Retente l'envoi à Snaplogic avec des données sauvegardées.
    """
    try:
        # Charger les données
        with open(temp_path, "rb") as f:
            excel_data, pdfs_data, metadata = pickle.load(f)
        logger.info(f"Données chargées depuis {temp_path}")

        # Configurer la session HTTP
        timeout = aiohttp.ClientTimeout(total=3600)  # 1 heure de timeout
        headers = get_headers()

        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                # Tenter l'envoi
                if len(pdfs_data) > 10:
                    response = await _send_large_data(
                        excel_data, pdfs_data, metadata, tracking
                    )
                else:
                    form = await _create_multipart(
                        excel_data, pdfs_data, metadata, 1, 1
                    )
                    response = await _send_http_request(
                        session, SNAPLOGIC_URL, form, headers
                    )

                # Si succès, supprimer le fichier temporaire et nettoyer
                await cleanup_temp_files(batch_id=metadata["batch_id"])

                return response

            except Exception as e:
                error_msg = SNAPLOGIC_ERRORS["SEND_ERROR"].format(str(e))
                logger.error(error_msg)

                await tracking.log_pipeline_operation(
                    OPERATION_TYPES["SNAPLOGIC_UPLOAD"],
                    status=STATUS["ERROR"],
                    error=error_msg,
                    metadata={"batch_id": metadata["batch_id"]},
                )

                raise Exception(error_msg) from e

    except Exception as e:
        error_msg = SNAPLOGIC_ERRORS["SEND_ERROR"].format(str(e))
        logger.error(error_msg)
        raise Exception(error_msg) from e


async def send_error_notification(message: str) -> Dict[str, Any]:
    """
    Envoie une notification d'erreur à l'endpoint de notification SnapLogic.
    Cette notification déclenchera l'envoi d'un email aux équipes métier.

    Args:
        message: Message d'erreur à envoyer

    Returns:
        Réponse de SnapLogic

    Raises:
        Exception: En cas d'erreur lors de l'envoi
    """
    url = f"{snaplogic_config.BASE_URL}{snaplogic_config.NOTIFICATION_ENDPOINT}"
    headers = {
        "Authorization": snaplogic_config.NOTIFICATION_BEARER,
        "Content-Type": "application/json",
    }

    try:
        timeout = aiohttp.ClientTimeout(
            total=60
        )  # Timeout plus court pour les notifications
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                url, json={"message": message}, headers=headers
            ) as response:
                if response.status != 200:
                    error_msg = SNAPLOGIC_ERRORS["NOTIFICATION_ERROR"].format(
                        response.status
                    )
                    logger.error(f"Notification error: {await response.text()}")
                    raise Exception(error_msg)

                return await response.json()

    except aiohttp.ClientError as e:
        error_msg = SNAPLOGIC_ERRORS["NOTIFICATION_ERROR"].format(str(e))
        logger.error(error_msg)
        raise Exception(error_msg) from e
    except Exception as e:
        error_msg = SNAPLOGIC_ERRORS["NOTIFICATION_ERROR"].format(str(e))
        logger.error(error_msg)
        raise Exception(error_msg) from e
