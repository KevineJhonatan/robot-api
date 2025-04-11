"""Service de tracking des opérations."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from src.services.dynamodb import DynamoDBClient
from src.constants.error_messages import TRACKING_ERRORS
from src.constants import Environment
from .constants import STATUS, OPERATION_TYPES

logger = logging.getLogger(__name__)

class TrackingService:
    """Service de tracking des opérations du pipeline.
    
    Le service utilise DynamoDB en production et un stockage en mémoire en développement.
    L'utilisation de DynamoDB est déterminée automatiquement en fonction de l'environnement :
    - DEVELOPMENT et TEST : stockage en mémoire
    - PRODUCTION : DynamoDB
    """
    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        """
        Initialise le service de tracking.
        
        Args:
            environment: Environnement d'exécution (DEVELOPMENT, TEST, PRODUCTION)
                        Détermine si on utilise DynamoDB (PRODUCTION) ou le stockage en mémoire (autres)
        """
        self.environment = environment
        # En dev et staging, on utilise le stockage en mémoire par défaut
        self.use_dynamodb = environment == Environment.PRODUCTION
        self.dynamodb = DynamoDBClient(self.use_dynamodb)
        self.table_name = 'pipeline_operations'
    
    async def log_pipeline_operation(
        self,
        operation_type: str,
        siret: str = "all",
        status: str = STATUS['SUCCESS'],
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Enregistre une opération du pipeline.
        
        Args:
            operation_type: Type d'opération (voir OPERATION_TYPES)
            siret: SIRET de l'entreprise concernée
            status: Statut de l'opération (voir STATUS)
            error: Message d'erreur si échec
            metadata: Métadonnées additionnelles
            
        Returns:
            True si succès, False sinon
        """
        try:
            # Vérifier le statut
            if status not in STATUS.values():
                error_msg = TRACKING_ERRORS['STATUS_ERROR'].format(status)
                logger.error(error_msg)
                return False
            
            # Vérifier le type d'opération
            if operation_type not in OPERATION_TYPES.values():
                error_msg = TRACKING_ERRORS['OPERATION_TYPE_ERROR'].format(operation_type)
                logger.error(error_msg)
                return False
            
            timestamp = datetime.now().isoformat()
            
            item = {
                'timestamp': {'S': timestamp},
                'operation_type': {'S': operation_type},
                'status': {'S': status},
                'siret': {'S': siret}
            }
            
            if error:
                item['error'] = {'S': error}
            
            if metadata:
                item['metadata'] = {'M': {k: {'S': str(v)} for k, v in metadata.items()}}
            
            success = await self.dynamodb.put_item(self.table_name, item)
            
            if not success:
                logger.error(TRACKING_ERRORS['LOG_ERROR'].format("Failed to write to DynamoDB"))
                return False
                
            return True
            
        except Exception as e:
            error_msg = TRACKING_ERRORS['LOG_ERROR'].format(str(e))
            logger.error(error_msg)
            return False
