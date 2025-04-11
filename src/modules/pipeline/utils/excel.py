"""Utilitaires de gestion des fichiers Excel."""

from typing import List, Dict, Any
from io import BytesIO
import pandas as pd

from src.modules.extract.parsers.alternantsJSON import alts_parsing
from src.modules.extract.parsers.avisdepaiement import avps_parsing
from src.modules.extract.parsers.entreprises import entreprise_parsing
from src.modules.extract.parsers.utils import save_excel


async def prepare_excel(successful_data: List[Dict[str, Any]], output: BytesIO) -> None:
    """
    Prépare un fichier Excel avec les données fournies et l'écrit dans un BytesIO.
    
    Args:
        successful_data: Liste des données récupérées avec succès. Chaque élément contient:
            - entreprise: Données de l'entreprise
            - data: Dictionnaire contenant:
                - avps: Liste des avis de paiement
                - alternants: Liste des alternants (optionnel)
        output: Objet BytesIO dans lequel écrire le fichier Excel. 
               Le curseur sera positionné au début après l'écriture.
    """
    # Extraire les AVPs de toutes les entreprises
    all_avps = []
    for item in successful_data:
        if "avps" in item["data"]:
            all_avps.extend(item["data"]["avps"])
    df_avps = await avps_parsing(pd.DataFrame(all_avps))

    # Extraire les données des entreprises
    entreprises_data = [item["entreprise"] for item in successful_data]
    df_ent = await entreprise_parsing(entreprises_data)

    # Extraire les données des alternants (si présentes)
    all_alts = []
    for item in successful_data:
        if "alternants" in item["data"]:
            all_alts.extend(item["data"]["alternants"])
    df_alts = await alts_parsing(pd.DataFrame(all_alts))

    # Création du fichier Excel en mémoire puis transformation en BytesIO
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        save_excel(writer, df_avps, "AVPs")
        save_excel(writer, df_ent, "Entreprises")
        save_excel(writer, df_alts, "Alternants")

    # Remettre le curseur au début du BytesIO pour permettre la lecture
    output.seek(0)
