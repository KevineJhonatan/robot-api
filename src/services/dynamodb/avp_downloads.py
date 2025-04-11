"""Module pour gérer le suivi des téléchargements d'AVP dans DynamoDB."""

import logging
from datetime import datetime
from typing import Optional, Dict, List
from starlette.config import Config

from src.services.dynamodb.client import DynamoDBClient
from src.constants.error_messages import AVP_ERRORS
from src.constants import Environment

config = Config()
logger = logging.getLogger(__name__)

class AVPDownloadTracker:
    """Classe pour suivre les téléchargements d'AVP dans DynamoDB."""
    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        """
        Initialise la connexion à DynamoDB.
        
        Args:
            environment: Environnement d'exécution
        """
        self.environment = environment
        # En dev et staging, on utilise le stockage en mémoire par défaut
        self.use_dynamodb = environment == Environment.PRODUCTION
        self.dynamodb = DynamoDBClient(self.use_dynamodb)
        self.table_name = config('AWS_DYNAMODB_AVP_DOWNLOADS_TABLE', cast=str)
        
    async def get_cached_avps(self, siret: str) -> List[str]:
        """
        Récupère la liste des AVPs déjà téléchargés pour un SIRET donné.
        
        Args:
            siret: SIRET de l'entreprise
            
        Returns:
            List[str]: Liste des IDs d'AVPs déjà téléchargés
        """
        try:
            if not siret:
                error_msg = AVP_ERRORS['CACHE_ERROR'].format("SIRET is required")
                logger.error(error_msg)
                return []
            
            if not self.use_dynamodb:
                return self.dynamodb._in_memory_storage.get(siret, [])
                
            key = {'siret': {'S': siret}}
            response = await self.dynamodb.get_item(self.table_name, key)
            return [item['avp_id']['S'] for item in response.get('Items', [])]
            
        except Exception as e:
            error_msg = AVP_ERRORS['CACHE_ERROR'].format(str(e))
            logger.error(error_msg)
            return []
            
    async def mark_avp_downloaded(self, siret: str, avp_id: str, metadata: Optional[Dict] = None) -> None:
        """
        Marque un AVP comme téléchargé.
        
        Args:
            siret: SIRET de l'entreprise
            avp_id: ID de l'AVP
            metadata: Métadonnées optionnelles
        """
        try:
            if not siret or not avp_id:
                error_msg = AVP_ERRORS['DOWNLOAD_ERROR'].format(
                    siret or "Unknown", "SIRET and AVP ID are required"
                )
                logger.error(error_msg)
                return
            
            if not self.use_dynamodb:
                if siret not in self.dynamodb._in_memory_storage:
                    self.dynamodb._in_memory_storage[siret] = []
                if avp_id not in self.dynamodb._in_memory_storage[siret]:
                    self.dynamodb._in_memory_storage[siret].append(avp_id)
                return
                
            item = {
                'siret': {'S': siret},
                'avp_id': {'S': avp_id},
                'download_date': {'S': datetime.now().isoformat()}
            }
            if metadata:
                item['metadata'] = {'M': metadata}
            
            success = await self.dynamodb.put_item(self.table_name, item)
            if not success:
                error_msg = AVP_ERRORS['DOWNLOAD_ERROR'].format(
                    siret, f"Failed to mark AVP {avp_id} as downloaded"
                )
                logger.error(error_msg)
                
        except Exception as e:
            error_msg = AVP_ERRORS['DOWNLOAD_ERROR'].format(siret, str(e))
            logger.error(error_msg)
            
    async def update_downloaded_avps(self, avps_data: Dict[str, List[Dict]]) -> None:
        """
        Met à jour la base DynamoDB avec les AVPs téléchargés.
        
        Args:
            avps_data: Dictionnaire avec SIRET comme clé et liste d'AVPs comme valeur
        """
        try:
            if not avps_data:
                error_msg = AVP_ERRORS['UPDATE_ERROR'].format("No AVP data provided")
                logger.error(error_msg)
                return
            
            if not self.use_dynamodb:
                for siret, avps in avps_data.items():
                    if siret not in self.dynamodb._in_memory_storage:
                        self.dynamodb._in_memory_storage[siret] = []
                    for avp in avps:
                        if avp['id'] not in self.dynamodb._in_memory_storage[siret]:
                            self.dynamodb._in_memory_storage[siret].append(avp['id'])
                return
                
            for siret, avps in avps_data.items():
                for avp in avps:
                    item = {
                        'siret': {'S': siret},
                        'avp_id': {'S': str(avp['id'])},
                        'file_path': {'S': f"data/sylae/avps/{siret}/{avp['id']}.pdf"},
                        'download_date': {'S': datetime.now().isoformat()}
                    }
                    success = await self.dynamodb.put_item(self.table_name, item)
                    if not success:
                        error_msg = AVP_ERRORS['UPDATE_ERROR'].format(
                            f"Failed to update AVP {avp['id']} for SIRET {siret}"
                        )
                        logger.error(error_msg)
                        continue
                        
            logger.info(f"Base DynamoDB mise à jour avec succès")
            
        except Exception as e:
            error_msg = AVP_ERRORS['UPDATE_ERROR'].format(str(e))
            logger.error(error_msg)
            
            # Fallback to memory store
            if not self.use_dynamodb:
                for siret, avps in avps_data.items():
                    if siret not in self.dynamodb._in_memory_storage:
                        self.dynamodb._in_memory_storage[siret] = []
                    for avp in avps:
                        if avp['id'] not in self.dynamodb._in_memory_storage[siret]:
                            self.dynamodb._in_memory_storage[siret].append(avp['id'])
