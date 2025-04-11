"""Configuration AWS pour le tracking des opérations."""

import os
import logging
from typing import Dict, Any
from starlette.config import Config
import boto3

from src.constants.error_messages import AWS_ERRORS

logger = logging.getLogger(__name__)

config = Config()

AWS_REGION = config('AWS_REGION', cast=str, default='eu-west-3')
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', cast=str, default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', cast=str, default='')
AWS_SESSION_TOKEN = config('AWS_SESSION_TOKEN', cast=str, default='')

# Configuration DynamoDB
TRACKING_TABLE = config('AWS_DYNAMODB_TRACKING_TABLE', cast=str, default='sylae_tracking')
TABLE_CONFIG = {
    'TableName': TRACKING_TABLE,
    'KeySchema': [
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'  # Clé de partition
        }
    ],
    'AttributeDefinitions': [
        {
            'AttributeName': 'id',
            'AttributeType': 'S'  # String
        }
    ],
    'BillingMode': 'PAY_PER_REQUEST'  # On-demand
}

def get_aws_config() -> Dict[str, str]:
    """
    Retourne la configuration AWS.
    
    Returns:
        Dict contenant la configuration AWS
        
    Raises:
        Exception: Si la configuration est invalide
    """
    try:
        return {
            'region_name': AWS_REGION,
            'aws_access_key_id': AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': AWS_SECRET_ACCESS_KEY,
            'aws_session_token': AWS_SESSION_TOKEN
        }
    except Exception as e:
        error_msg = AWS_ERRORS['CONFIG_ERROR'].format(str(e))
        logger.error(error_msg)
        raise Exception(error_msg) from e

def get_dynamodb_session() -> boto3.Session:
    """
    Crée une session AWS pour DynamoDB en fonction de l'environnement.
    Sur ECS, utilise les credentials IAM.
    En local, utilise les variables d'environnement.
    
    Returns:
        Session boto3 configurée
        
    Raises:
        Exception: Si la création de la session échoue
    """
    try:
        if "AWS_EXECUTION_ENV" in os.environ:  # Vérifie si l'application tourne sur ECS
            session = boto3.Session()
        else:
            # En local, utilise les variables d'environnement
            aws_config = get_aws_config()
            session = boto3.Session(
                region_name=aws_config['region_name'],
                aws_access_key_id=aws_config['aws_access_key_id'],
                aws_secret_access_key=aws_config['aws_secret_access_key'],
                aws_session_token=aws_config['aws_session_token']
            )
            
        return session
        
    except Exception as e:
        error_msg = AWS_ERRORS['SESSION_ERROR'].format(str(e))
        logger.error(error_msg)
        raise Exception(error_msg) from e

# Types d'opérations pour le tracking
OPERATION_TYPES = {
    'PIPELINE_START': 'PIPELINE_START',  # Démarrage du pipeline complet
    'SCRAPING_START': 'SCRAPING_START',  # Début du scraping
    'ENTREPRISES_DONE': 'ENTREPRISES_DONE',  # Liste des entreprises récupérée
    'AVPS_DONE': 'AVPS_DONE',  # AVPs récupérés
    'ALTERNANTS_DONE': 'ALTERNANTS_DONE',  # Alternants récupérés
    'EXPORT_READY': 'EXPORT_READY',  # Données prêtes pour SnapLogic
    'EXPORT_ERROR': 'EXPORT_ERROR'  # Erreur lors de l'export
}

# Statuts des opérations
STATUS = {
    'RUNNING': 'RUNNING',      # Opération en cours
    'SUCCESS': 'SUCCESS',      # Opération réussie
    'ERROR': 'ERROR',         # Erreur pendant l'opération
    'PENDING': 'PENDING',     # En attente de démarrage
    'SKIPPED': 'SKIPPED',     # Opération ignorée
    'COMPLETED': 'COMPLETED', # Opération terminée avec succès
    'FAILED': 'FAILED'       # Opération échouée
}
