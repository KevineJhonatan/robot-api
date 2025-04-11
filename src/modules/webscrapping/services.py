import logging
import os
from datetime import datetime, timedelta

from src.modules.webscrapping.queries.alternant import get_alternant
from src.modules.storage.services import get_cached_session, cache_session
from src.modules.storage.delta.delta import refresh_deltas_in_avps, refresh_deltas_in_avps_bydate
from src.modules.storage.avps.avps import update_avps

from src.modules.webscrapping.queries.alternants import get_alternant_datas
from src.modules.storage.services import get_cached_session, cache_session

from .scenarios.connexion import Authentification

from .queries.avispaiements import fetch_avps_list, get_entreprise_avps_pdf, get_entreprise_avps_pdf_memory
from .queries.entreprises import get_entreprises_list
from .queries.alternant_etat_de_presence import get_alternant_etat_presence
from .queries.alternant import get_alternant
from .queries.alternants import get_alternant_datas


lg = logging.getLogger()
lg.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s;')

# Configuration du fichier de log
log_file = 'logs/sylae_scraping.log'
os.makedirs('logs', exist_ok=True)
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Configuration de la sortie console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Ajout des handlers au logger
lg.addHandler(file_handler)
lg.addHandler(console_handler)

async def create_or_get_valid_session(username : str, password : str) -> str:
    expiration = (datetime.now() + timedelta(minutes=15)).strftime("%d%m%Y-%H-%M-%S")
    content = await get_cached_session()
    if content:
        return content
    else :
        sessionId = await Authentification(username,password)
        await cache_session(sessionId,expiration)
        return sessionId


async def get_entreprises(username : str, password : str) -> dict:
    sessionID = await create_or_get_valid_session(username, password)
    entreprises = await get_entreprises_list(sessionID)
    return entreprises

async def fetch_avps(username : str, password : str, empId : str, ref_date: datetime)-> dict:

    sessionID = await create_or_get_valid_session(username, password)
    avps = await fetch_avps_list(sessionID, empId, ref_date)
    return avps

async def download_avps_pdfs(username: str, password: str, empId: str, siret: str, avps: dict) -> dict:
    """
    Télécharge les PDFs des AVPs d'une entreprise et les retourne en mémoire.
    
    Args:
        username: Identifiant pour l'API
        password: Mot de passe pour l'API
        empId: ID de l'entreprise
        siret: SIRET de l'entreprise
        avps: Liste des AVPs à télécharger
        
    Returns:
        Dict contenant les PDFs en mémoire avec leur statut delta
        Format: {
            'siret_AVP1': {
                'content': bytes_content,
                'delta': bool
            }
        }
    """
    sessionID = await create_or_get_valid_session(username, password)
    pdf_contents = await get_entreprise_avps_pdf(sessionID, empId, siret, avps)
    
    # Formatage des PDFs selon le format attendu
    formatted_pdfs = {}
    for pdf_info in pdf_contents:
        formatted_pdfs[f'{siret}_{pdf_info["id"]}'] = {
            'content': pdf_info['content'],
            'delta': pdf_info['delta']
        }
    
    return formatted_pdfs

async def download_avps_pdfs_memory(username: str, password: str, empId: str, siret: str, avps: dict) -> dict:
    """
    Télécharge les PDFs des AVPs d'une entreprise directement en mémoire.
    
    Args:
        username: Identifiant pour l'API
        password: Mot de passe pour l'API
        empId: ID de l'entreprise
        siret: SIRET de l'entreprise
        avps: Liste des AVPs à télécharger
        
    Returns:
        Dict contenant les PDFs en mémoire avec leur statut delta
        Format: {
            'siret_AVP1': {
                'content': bytes_content,
                'delta': bool
            }
        }
    """
    sessionID = await create_or_get_valid_session(username, password)
    return await get_entreprise_avps_pdf_memory(sessionID, empId, siret, avps)

async def refresh_deltas(siret : str, avps : dict):
    new_avps = await refresh_deltas_in_avps(siret,avps)
    await update_avps(new_avps, siret)

async def refresh_deltas_bydate(siret: str, avps: dict, reference_date: datetime):
    """
    Met à jour les AVPs en fonction de leur date de création/modification par rapport à une date de référence.
    Les AVPs plus récents que la date de référence sont placés dans delta, les autres dans data.
    
    Args:
        siret: SIRET de l'entreprise
        avps: Liste des AVPs à traiter
        reference_date: Date de référence pour le tri
    """
    new_avps = await refresh_deltas_in_avps_bydate(siret, avps, reference_date)
    await update_avps(new_avps, siret)

async def fetch_alts(username : str, password : str, empId : str)-> dict:

    sessionID = await create_or_get_valid_session(username, password)
    alts = await get_alternant_datas(sessionID, empId)
    alts = alts['items']
    total = len(alts)
    for i, alt in enumerate(alts, 1):
        lg.info(f"Traitement {i}/{total} - Alternant {alt['id']}")
        alt_datas = await get_alternant(sessionID,empId ,alt['id'])
        last_date = await get_alternant_etat_presence(sessionID, alt['id'])
        alt.update({"details":alt_datas, "last_date":last_date})
    return alts
