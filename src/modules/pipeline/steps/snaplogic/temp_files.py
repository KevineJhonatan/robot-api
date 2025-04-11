"""Gestion des fichiers temporaires pour SnapLogic."""

import os
import tempfile
import logging
import pickle
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from io import BytesIO

logger = logging.getLogger(__name__)

TEMP_FILE_PREFIX = "snaplogic_retry_"

async def find_latest_temp_file() -> Optional[str]:
    """
    Trouve le fichier temporaire le plus récent.
    Format des fichiers : snaplogic_retry_BATCH_ID_YYYYMMDD_HHMMSS.pkl
    
    Returns:
        Chemin du fichier temporaire le plus récent ou None si aucun fichier trouvé
    """
    temp_dir = tempfile.gettempdir()
    latest_file = None
    latest_timestamp = None
    
    for f in os.listdir(temp_dir):
        if not f.startswith(TEMP_FILE_PREFIX):
            continue
            
        try:
            # Format: snaplogic_retry_BATCH_ID_YYYYMMDD_HHMMSS.pkl
            parts = f.split("_")
            if len(parts) < 4:  # prefix + batch_id + timestamp
                continue
                
            timestamp_str = parts[-1].replace(".pkl", "")
            timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
            
            if latest_timestamp is None or timestamp > latest_timestamp:
                latest_timestamp = timestamp
                latest_file = os.path.join(temp_dir, f)
                
        except (ValueError, IndexError):
            continue
    
    return latest_file

async def cleanup_temp_files(max_age_hours: int = 24, batch_id: str = None) -> None:
    """
    Nettoie les fichiers temporaires.
    
    Args:
        max_age_hours: Âge maximum des fichiers en heures
        batch_id: Si spécifié, ne supprime que les fichiers de ce batch
    """
    temp_dir = tempfile.gettempdir()
    now = datetime.now()
    
    for f in os.listdir(temp_dir):
        if not f.startswith(TEMP_FILE_PREFIX):
            continue
            
        # Si batch_id spécifié, ne supprimer que les fichiers de ce batch
        if batch_id and not f.startswith(f"{TEMP_FILE_PREFIX}{batch_id}_"):
            continue
            
        file_path = os.path.join(temp_dir, f)
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        # Supprimer si trop vieux ou si batch_id spécifié
        if batch_id or (now - file_time) > timedelta(hours=max_age_hours):
            try:
                os.remove(file_path)
                logger.info(f"Fichier temporaire supprimé : {f}")
            except Exception as e:
                logger.warning(f"Impossible de supprimer le fichier temporaire {f}: {e}")

async def remove_temp_files() -> None:
    """
    Supprime tous les fichiers temporaires de SnapLogic.
    """
    temp_dir = tempfile.gettempdir()
    
    for f in os.listdir(temp_dir):
        if not f.startswith(TEMP_FILE_PREFIX):
            continue
            
        file_path = os.path.join(temp_dir, f)
        try:
            os.remove(file_path)
            logger.info(f"Fichier temporaire supprimé : {f}")
        except Exception as e:
            logger.warning(f"Impossible de supprimer le fichier temporaire {f}: {e}")

async def create_temp_file(excel_data: BytesIO, pdfs_data: Dict[str, Dict[str, Any]], metadata: Dict[str, Any]) -> str:
    """
    Sauvegarde les données dans un dossier temporaire pour retry.
    
    Args:
        excel_data: Données Excel
        pdfs_data: Données PDFs
        metadata: Métadonnées
        
    Returns:
        str: Chemin du fichier temporaire créé
    """
    # Supprimer les anciens fichiers temporaires pour ce batch_id
    temp_dir = tempfile.gettempdir()
    batch_id = metadata['batch_id']
    for f in os.listdir(temp_dir):
        if f.startswith(f"{TEMP_FILE_PREFIX}{batch_id}_"):
            try:
                os.remove(os.path.join(temp_dir, f))
            except Exception as e:
                logger.warning(f"Impossible de supprimer l'ancien fichier temporaire: {str(e)}")
    
    # Créer le nouveau fichier temporaire
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_filename = f"{TEMP_FILE_PREFIX}{batch_id}_{timestamp}.pkl"
    temp_path = os.path.join(temp_dir, temp_filename)
    
    # Préparer les données à sauvegarder
    data_to_save = {
        'excel_data': excel_data.getvalue(),
        'pdfs_data': pdfs_data,
        'metadata': metadata,
        'timestamp': timestamp,
        'created_at': datetime.now().isoformat()
    }
    
    # Sauvegarder les données
    with open(temp_path, 'wb') as f:
        pickle.dump(data_to_save, f)
    
    logger.info(f"Données sauvegardées dans {temp_path}")
    return temp_path

async def _load_temp_data(temp_path: str) -> tuple:
    """
    Charge les données depuis un fichier temporaire.
    
    Args:
        temp_path: Chemin du fichier temporaire
        
    Returns:
        Tuple[BytesIO, Dict, Dict]: Données chargées (excel, pdfs, metadata)
    """
    with open(temp_path, 'rb') as f:
        data = pickle.load(f)
    
    # Recréer les objets
    excel_data = BytesIO(data['excel_data'])
    pdfs_data = data['pdfs_data']
    metadata = data['metadata']
    
    logger.info(f"Données chargées depuis {temp_path}")
    return excel_data, pdfs_data, metadata
