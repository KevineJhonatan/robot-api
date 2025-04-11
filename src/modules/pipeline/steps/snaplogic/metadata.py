"""Gestion des métadonnées pour SnapLogic."""

from typing import Dict, Any
from datetime import datetime

def prepare_metadata(batch_id: str, entreprises: list, success_count: int) -> Dict[str, Any]:
    """
    Prépare les métadonnées pour SnapLogic.
    
    Args:
        batch_id: Identifiant unique du batch
        entreprises: Liste des entreprises traitées
        success_count: Nombre d'entreprises traitées avec succès
        
    Returns:
        Dict contenant :
        - batch_id: Identifiant du batch
        - timestamp: Date et heure de création
        - entreprises: Liste des entreprises avec siret et dénomination
        - stats: Statistiques sur le traitement
    """
    return {
        'batch_id': batch_id,
        'timestamp': datetime.now().isoformat(),
        'entreprises': [
            {
                'siret': e.get('siret', 'N/A'),
                'denomination': e.get('denomination', 'N/A')
            }
            for e in entreprises
        ],
        'stats': {
            'total_entreprises': len(entreprises),
            'success_count': success_count
        }
    }
