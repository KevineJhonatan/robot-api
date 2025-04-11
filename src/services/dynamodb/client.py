"""Client DynamoDB pour l'application."""

import logging
import boto3
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.constants.error_messages import DYNAMODB_ERRORS
from src.services.aws import get_aws_config

logger = logging.getLogger(__name__)

class DynamoDBClient:
    """Client pour interagir avec DynamoDB."""
    
    def __init__(self, use_dynamodb: bool = False):
        """
        Initialise le client DynamoDB.
        
        Args:
            use_dynamodb: Si True, utilise DynamoDB, sinon stockage en mémoire
        """
        self.use_dynamodb = use_dynamodb
        self._session = None
        self._client = None
        self._in_memory_storage = {}
        
        if use_dynamodb:
            self._init_session()
    
    def _init_session(self) -> None:
        """Initialise la session AWS."""
        try:
            aws_config = get_aws_config()
            self._session = boto3.Session(
                aws_access_key_id=aws_config['access_key_id'],
                aws_secret_access_key=aws_config['secret_access_key'],
                region_name=aws_config['region']
            )
            self._client = self._session.client('dynamodb')
        except Exception as e:
            logger.error(DYNAMODB_ERRORS['INIT_ERROR'].format(str(e)))
            raise
    
    async def get_item(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Récupère un item dans DynamoDB.
        
        Args:
            table_name: Nom de la table
            key: Clé de l'item
            
        Returns:
            Item trouvé ou None
        """
        if not self.use_dynamodb:
            return self._in_memory_storage.get(f"{table_name}:{str(key)}")
        
        try:
            response = self._client.get_item(
                TableName=table_name,
                Key=key
            )
            return response.get('Item')
        except Exception as e:
            logger.error(DYNAMODB_ERRORS['GET_ERROR'].format(str(e)))
            return None
    
    async def put_item(self, table_name: str, item: Dict[str, Any]) -> bool:
        """
        Enregistre un item dans DynamoDB.
        
        Args:
            table_name: Nom de la table
            item: Item à enregistrer
            
        Returns:
            True si succès, False sinon
        """
        if not self.use_dynamodb:
            key = f"{table_name}:{str(item)}"
            self._in_memory_storage[key] = item
            return True
        
        try:
            self._client.put_item(
                TableName=table_name,
                Item=item
            )
            return True
        except Exception as e:
            logger.error(DYNAMODB_ERRORS['PUT_ERROR'].format(str(e)))
            return False
    
    async def update_item(self, table_name: str, key: Dict[str, Any], 
                         update_expression: str, expression_values: Dict[str, Any]) -> bool:
        """
        Met à jour un item dans DynamoDB.
        
        Args:
            table_name: Nom de la table
            key: Clé de l'item
            update_expression: Expression de mise à jour
            expression_values: Valeurs pour l'expression
            
        Returns:
            True si succès, False sinon
        """
        if not self.use_dynamodb:
            stored_key = f"{table_name}:{str(key)}"
            if stored_key in self._in_memory_storage:
                self._in_memory_storage[stored_key].update(expression_values)
                return True
            return False
        
        try:
            self._client.update_item(
                TableName=table_name,
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            return True
        except Exception as e:
            logger.error(DYNAMODB_ERRORS['UPDATE_ERROR'].format(str(e)))
            return False
    
    async def delete_item(self, table_name: str, key: Dict[str, Any]) -> bool:
        """
        Supprime un item dans DynamoDB.
        
        Args:
            table_name: Nom de la table
            key: Clé de l'item
            
        Returns:
            True si succès, False sinon
        """
        if not self.use_dynamodb:
            stored_key = f"{table_name}:{str(key)}"
            if stored_key in self._in_memory_storage:
                del self._in_memory_storage[stored_key]
                return True
            return False
        
        try:
            self._client.delete_item(
                TableName=table_name,
                Key=key
            )
            return True
        except Exception as e:
            logger.error(DYNAMODB_ERRORS['DELETE_ERROR'].format(str(e)))
            return False
    
    async def scan_table(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Scanne tous les items d'une table DynamoDB.
        
        Args:
            table_name: Nom de la table
            
        Returns:
            Liste des items trouvés
        """
        if not self.use_dynamodb:
            return list(self._in_memory_storage.values())
        
        try:
            items = []
            last_evaluated_key = None
            
            while True:
                if last_evaluated_key:
                    response = self._client.scan(
                        TableName=table_name,
                        ExclusiveStartKey=last_evaluated_key
                    )
                else:
                    response = self._client.scan(
                        TableName=table_name
                    )
                
                items.extend(response.get('Items', []))
                
                last_evaluated_key = response.get('LastEvaluatedKey')
                if not last_evaluated_key:
                    break
            
            return items
            
        except Exception as e:
            logger.error(DYNAMODB_ERRORS['SCAN_ERROR'].format(str(e)))
            return []
