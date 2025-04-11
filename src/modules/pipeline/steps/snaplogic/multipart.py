"""Gestion des requêtes multipart pour SnapLogic."""

import logging
import aiohttp
from io import BytesIO
from typing import Dict, Any, Optional

from .config import MIME_TYPES

logger = logging.getLogger(__name__)


async def _create_multipart(
    excel_data: Optional[BytesIO],
    pdfs_batch: Dict[str, Dict[str, Any]],
    metadata: Dict[str, Any],
    batch_number: int,
    total_batches: int,
) -> aiohttp.FormData:
    """
    Crée le contenu multipart pour l'envoi à SnapLogic.

    Args:
        excel_data: Données Excel en mémoire (optionnel)
        pdfs_batch: Dictionnaire des PDFs pour ce batch
        metadata: Métadonnées pour SnapLogic
        batch_number: Numéro du batch courant
        total_batches: Nombre total de batchs

    Returns:
        FormData: Données formatées pour l'envoi multipart
    """
    form = aiohttp.FormData()

    # Ajouter les métadonnées
    metadata["batch_info"] = {"current": batch_number, "total": total_batches}
    form.add_field("metadata", str(metadata), content_type=MIME_TYPES["JSON"])

    # Ajouter le fichier Excel s'il est présent
    if excel_data is not None:
        form.add_field(
            "excel_file",
            excel_data,
            filename="data.xlsx",
            content_type=MIME_TYPES["EXCEL"],
        )

    # Ajouter les PDFs
    for pdf_key, pdf_info in pdfs_batch.items():
        form.add_field(
            f"pdf_{pdf_key}",
            pdf_info["content"],
            filename=f"{pdf_key}",
            content_type=MIME_TYPES["PDF"],
        )

    return form
