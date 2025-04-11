from fastapi import APIRouter, HTTPException, status
import logging
import requests
from datetime import datetime

from src.modules.storage.avps.avps import complete_pdf_avps, get_stored_avps, save_avps
from src.modules.storage.entreprises.entreprises import get_stored_entreprises, get_old_entreprises, save_new_entreprises, save_old_entreprises, clean_all_folders
from src.modules.storage.delta.delta import delete_all_emptyfolders
from src.modules.storage.alternants.alternants import save_alts

from .services import *

router = APIRouter()

lg = logging.getLogger()
lg.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s;')


@router.get("/step1-get-new-sirets", status_code=status.HTTP_200_OK)
async def get_new_siret(old_folder_name: str)-> str :
    lg.info("Début récupération entreprises")
    sessionID = await create_or_get_valid_session("username", "password")
    fetch_ent = await get_entreprises_list(sessionID)
    all_entreprise = fetch_ent["items"]
    old_entreprise = await get_old_entreprises(old_folder_name)
    await save_new_entreprises(all_entreprise, old_entreprise)
    return "step1-get-new-sirets => ok"


@router.get("/step2-all-avp", status_code=status.HTTP_200_OK)
async def save_all_avps(reference_date: str)-> str :
    lg.info('Début récupération des relevés de toutes les entreprises')
    entreprises_dict = await get_stored_entreprises()
    total_entreprises = len(entreprises_dict)
    total_avps = 0

    ref_date = datetime(2020, 1, 1)
    if isinstance(reference_date, str) and reference_date:
        ref_date = datetime.strptime(reference_date, "%Y-%m-%d")
    
    for i, entreprise in enumerate(entreprises_dict, 1):
        lg.info(f"Traitement entreprise {i}/{total_entreprises} - SIRET: {entreprise['siret']}")
        avis_de_paiements = await fetch_avps("username","password",entreprise["empId"], ref_date)
        if avis_de_paiements:
            total_avps += len(avis_de_paiements)
        await save_avps(avis_de_paiements, entreprise["siret"])
    return "step2-all-avp => ok"


@router.get("/step3-all-alternants", status_code=status.HTTP_200_OK)
async def save_all_alternants()-> str :
    lg.info('Début récupération des infos de toutes les alternants')
    entreprises_dict = await get_stored_entreprises()
    total_entreprises = len(entreprises_dict)
    total_alternants = 0
    errors = []

    for i, entreprise in enumerate(entreprises_dict, 1):
        try:
            lg.info(f"Traitement entreprise {i}/{total_entreprises} - SIRET: {entreprise['siret']}")
            alternants = await fetch_alts("username", "password", entreprise["empId"])
            if alternants:
                total_alternants += len(alternants)
            await save_alts(alternants, entreprise["siret"])
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Erreur de connexion pour l'entreprise {entreprise['siret']}: Le site sylae.asp-public.fr est inaccessible"
            lg.error(error_msg)
            errors.append(error_msg)
            continue
        except Exception as e:
            error_msg = f"Erreur pour l'entreprise {entreprise['siret']}: {str(e)}"
            lg.error(error_msg)
            errors.append(error_msg)
            continue

    lg.info("=== Résumé de la récupération des alternants ===")
    lg.info(f"Alternants trouvés: {total_alternants}")
    if errors:
        lg.error("Erreurs rencontrées:")
        for error in errors:
            lg.error(f"  - {error}")
    lg.info("==========================================")
    return "step3-all-alternants => ok"


@router.get("/step4-save-pdfs", status_code=status.HTTP_200_OK)
async def save_avp_pdfs() -> str :
    lg.info('Début récupération des PDFs des avis de paiement')
    entreprises_dict = await get_stored_entreprises()
    total_entreprises = len(entreprises_dict)
    total_downloads = 0
    
    for i, entreprise in enumerate(entreprises_dict, 1):
        lg.info(f"Traitement entreprise {i}/{total_entreprises} - SIRET: {entreprise['siret']}")
        avps_dict = await get_stored_avps(entreprise['siret'])
        
        if not complete_pdf_avps(entreprise["siret"]):
            lg.info(f"Téléchargement des PDFs manquants...")
            await download_avps_pdfs("username", "password", entreprise['empId'], entreprise['siret'], avps_dict)
            total_downloads += 1
    
    lg.info(f"Entreprises traitées: {total_entreprises}")
    return "step4-save-pdfs => ok"


@router.get("/refresh-delta-bydate", status_code=status.HTTP_200_OK)
async def refresh_delta_bydate(reference_date: str) -> str:
    """
    Rafraîchit les deltas en fonction d'une date de référence.
    Les PDFs ayant une date de création/modification postérieure à la date de référence seront placés dans delta,
    les autres dans data.
    
    Args:
        reference_date: Date de référence au format YYYY-MM-DD
    """
    try:
        ref_date = datetime.strptime(reference_date, "%Y-%m-%d")
        
        entreprises_dict = await get_stored_entreprises()
        for entreprise in entreprises_dict:
            avps_dict = await get_stored_avps(entreprise['siret'])
            await refresh_deltas_bydate(entreprise['siret'], avps_dict, ref_date)
            
        delete_all_emptyfolders("data/sylae/avps_delta")        
        
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Format de date invalide. Utilisez le format YYYY-MM-DD")    
    return "refresh-delta-bydate => ok"


@router.get("/step6-pass-from-new-to-old-siret", status_code=status.HTTP_200_OK)
async def new_to_old_siret()-> str:
    lg.info("Cleaning folders")
    await clean_all_folders()
    return "step6-pass-from-new-to-old-siret => ok"


@router.get("/step7-get-old-sirets", status_code=status.HTTP_200_OK)
async def get_old_siret(old_folder_name: str)-> str :
    lg.info("Début récupération entreprises")
    old_entreprise = await get_old_entreprises(old_folder_name)
    await save_old_entreprises(old_entreprise)
    return "step7-get-old-sirets => ok"