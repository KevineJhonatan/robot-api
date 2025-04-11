"""Messages d'erreur pour l'application."""

# Messages d'erreur généraux
GENERAL_ERRORS = {
    'INVALID_REQUEST': 'Requête invalide: {}',
    'NETWORK_ERROR': 'Erreur réseau: {}',
    'TIMEOUT_ERROR': 'Timeout de la requête: {}',
    'INVALID_RESPONSE': 'Réponse invalide: {}'
}

# Messages d'erreur AWS
AWS_ERRORS = {
    'CONFIG_ERROR': 'Erreur de configuration AWS: {}',
    'SESSION_ERROR': 'Erreur lors de la création de la session AWS: {}',
    'CREDENTIALS_ERROR': 'Erreur de credentials AWS: {}',
    'SERVICE_ERROR': 'Erreur du service AWS {}: {}'
}

# Messages d'erreur DynamoDB
DYNAMODB_ERRORS = {
    'INIT_ERROR': 'Échec de l\'initialisation de DynamoDB: {}',
    'GET_ERROR': 'Échec de la récupération de l\'item dans DynamoDB: {}',
    'PUT_ERROR': 'Échec de l\'enregistrement de l\'item dans DynamoDB: {}',
    'UPDATE_ERROR': 'Échec de la mise à jour de l\'item dans DynamoDB: {}',
    'DELETE_ERROR': 'Échec de la suppression de l\'item dans DynamoDB: {}',
    'SCAN_ERROR': 'Échec du scan de la table DynamoDB: {}'
}

# Messages d'erreur SnapLogic
SNAPLOGIC_ERRORS = {
    'GENERAL_ERROR': 'Erreur lors de l\'envoi des données à SnapLogic: {}',
    'INVALID_JSON': 'Réponse JSON invalide de SnapLogic: {}',
    'API_ERROR': 'SnapLogic a retourné une erreur {}: {}',
    'NETWORK_ERROR': 'Erreur réseau lors de l\'envoi à SnapLogic: {}',
    'SEND_ERROR': 'Erreur lors de l\'envoi des données à SnapLogic: {}',
    'LARGE_DATA_ERROR': 'Erreur lors de l\'envoi des données volumineuses à SnapLogic: {}',
    'RESPONSE_ERROR': 'Réponse invalide de SnapLogic: {}',
    'REQUEST_ERROR': 'Erreur lors de l\'envoi de la requête à SnapLogic: {}',
    'BATCH_ERROR': 'Erreur lors de l\'envoi du batch à SnapLogic: {}',
    'FORM_ERROR': 'Erreur lors de la création du formulaire: {}',
    'NOTIFICATION_ERROR': 'Erreur lors de l\'envoi de la notification d\'erreur: {}',
    'BATCH_ERROR': 'Erreur lors de l\'envoi du batch à SnapLogic: {}',
    'INVALID_JSON_RESPONSE': 'Réponse JSON invalide de SnapLogic: {}',
    'UPLOAD_ERROR': 'Erreur lors de l\'envoi des données à SnapLogic: {}',
    'CONNECTION_ERROR': 'Erreur de connexion à SnapLogic: {}',
}

# Messages d'erreur Pipeline
PIPELINE_ERRORS = {
    'COMPANY_ERROR': 'Erreur lors du traitement de l\'entreprise {}: {}',
    'DATA_ERROR': 'Erreur lors de la récupération des données: {}',
    'EXCEL_ERROR': 'Erreur lors de la préparation du fichier Excel: {}',
    'PDF_ERROR': 'Erreur lors de la préparation des PDFs: {}',
    'PROCESS_ERROR': 'Erreur lors du traitement: {}',
    'ALT_ERROR': 'Erreur lors de la récupération des alternants: {}',
    'AVP_ERROR': 'Erreur lors de la récupération des AVPs: {}'
}

# Messages d'erreur AVP
AVP_ERRORS = {
    'DOWNLOAD_ERROR': 'Échec du téléchargement de l\'AVP pour {}: {}',
    'CACHE_ERROR': 'Erreur lors de la vérification du cache AVP: {}',
    'UPDATE_ERROR': 'Erreur lors de la mise à jour des AVPs téléchargés: {}'
}

# Messages d'erreur tracking
TRACKING_ERRORS = {
    'INVALID_STATUS': 'Status invalide: {}',
    'INVALID_OPERATION': 'Type d\'opération invalide: {}',
    'UPDATE_ERROR': 'Erreur lors de la mise à jour du tracking: {}',
    'LOG_ERROR': 'Échec de l\'enregistrement de l\'opération: {}',
    'STATUS_ERROR': 'Statut invalide: {}',
    'OPERATION_TYPE_ERROR': 'Type d\'opération invalide: {}'
}
